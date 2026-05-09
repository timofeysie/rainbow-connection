#!/usr/bin/env python3
"""
Sensor Timelapse Script - Raspberry Pi 5
Reads sensor data from one or two Raspberry Pi Picos via USB serial and serves
a merged JSON file for the timelapse web interface.

1. Greenhouse / weather Pico: sensor-platform.py line format (BME280, ENS160, etc.)
2. Optional watering Pico: automatic_watering.py line format (moisture %, pump seconds)

Optional environment overrides (empty = auto-discover USB serial ports):
  PICO_GREENHOUSE_PORT=/dev/ttyACM0
  PICO_WATERING_PORT=/dev/ttyACM1

Auto mode assigns sorted device paths: first = greenhouse, second = watering.

Usage:
    python3 sensor-timelapse-script.py
"""

import serial
import serial.tools.list_ports
import re
import json
import time
import os
import subprocess
import threading
from datetime import datetime

# Configuration
VERSION = "1.1.2"
SERIAL_BAUDRATE = 115200
SERIAL_TIMEOUT = 1
DATA_FILE = "/var/www/html/sensor-data.json"
LOG_FILE = "/var/log/sensor-timelapse.log"
IMAGE_DIR = "/var/www/html/images"
TIMELAPSE_INTERVAL = 60  # Capture image every 60 seconds (adjust as needed)
# Optional: set on the Pi if USB enumeration order is wrong (see module docstring)
PICO_GREENHOUSE_PORT = os.environ.get("PICO_GREENHOUSE_PORT", "").strip() or None
PICO_WATERING_PORT = os.environ.get("PICO_WATERING_PORT", "").strip() or None

# Daylight hours configuration (24-hour format)
CAPTURE_START_HOUR = 9   # Start capturing at 9 AM
CAPTURE_END_HOUR = 17    # Stop capturing at 5 PM (17:00)
ENABLE_DAYLIGHT_ONLY = True  # Set to False to capture 24/7

# Rate-limited diagnostic when a Moisture: line fails to parse (seconds)
MOISTURE_PARSE_FAIL_LOG_INTERVAL = 60.0
# How often to log/print a sensor summary (file log + optional stdout; avoids per-sample spam)
SENSOR_UPDATE_LOG_INTERVAL = 60.0
_parse_diag = {"last_moisture_fail_log": 0.0, "last_sensor_log": 0.0}
data_lock = threading.Lock()

# Sensor data structure (merged JSON for the web UI)
sensor_data = {
    "moisture_percent": 0,
    "moisture_raw": 0,
    "temperature_c": 0.0,
    "pressure_hpa": 0.0,
    "humidity_rh": 0.0,
    "aqi": 0,
    "tvoc": 0,
    "eco2": 0,
    "timestamp": "",
    "last_update": "",
    "watering_soil_moisture": None,
    "watering_pump_seconds": None,
    "watering_last_update": None,
}


def list_usb_serial_devices():
    """Return sorted unique candidate serial device paths (Picos, USB-UART, etc.)."""
    devices = []
    for p in serial.tools.list_ports.comports():
        parts = ((p.device or "") + " " + (p.description or "")).lower()
        if (
            "ttyacm" in parts
            or "ttyusb" in parts
            or "usb" in parts
            or "serial" in parts
            or parts.strip().startswith("com")
        ):
            devices.append(p.device)
    return sorted(set(devices))


def resolve_greenhouse_and_watering_ports():
    """
    Resolve device paths for two Picos. Env vars win; otherwise use sorted
    USB serial list (first = greenhouse, next unused = watering).
    """
    auto = list_usb_serial_devices()
    gh = PICO_GREENHOUSE_PORT
    wt = PICO_WATERING_PORT
    remaining = [d for d in auto if d not in {x for x in (gh, wt) if x}]
    if gh is None and remaining:
        gh = remaining.pop(0)
    if wt is None and remaining:
        wt = remaining.pop(0)
    if gh and wt and gh == wt:
        wt = None
    return gh, wt


def parse_sensor_line(line):
    """
    Parse sensor data from Pico print statement.

    Matches legacy one-line format or sensor-platform.py with optional middle
    segments (e.g. Light/Sun) between moisture and the atmospheric block:
    "Moisture: {moisture}% (raw: {raw}) | ... | {temp} °C  {pres} hPa  {hum} %RH  AQI:{aqi} TVOC:{tvoc} eCO2:{eco2}"
    """
    pattern = (
        r"Moisture: (\d+)% \(raw: (\d+)\) \|"
        r".*?"
        r"([\d.]+) °C  ([\d.]+) hPa  ([\d.]+) %RH  AQI:(\d+) TVOC:(\d+) eCO2:(\d+)"
    )
    match = re.match(pattern, line.strip())
    
    if match:
        return {
            "moisture_percent": int(match.group(1)),
            "moisture_raw": int(match.group(2)),
            "temperature_c": float(match.group(3)),
            "pressure_hpa": float(match.group(4)),
            "humidity_rh": float(match.group(5)),
            "aqi": int(match.group(6)),
            "tvoc": int(match.group(7)),
            "eco2": int(match.group(8))
        }
    return None


def parse_watering_line(line):
    """
    Parse automatic_watering.py console line, e.g.:
    Moisture  32.00%    Pump Time  12.34s
    """
    pattern = r"Moisture\s+([\d.]+)%\s+Pump\s+Time\s+([\d.]+)s"
    match = re.match(pattern, line.strip())
    if match:
        return {
            "watering_soil_moisture": float(match.group(1)),
            "watering_pump_seconds": float(match.group(2)),
        }
    return None


def write_sensor_data(data):
    """Write sensor data to JSON file for web interface (atomic replace avoids empty reads)."""
    tmp_path = DATA_FILE + ".tmp"
    try:
        dest_dir = os.path.dirname(DATA_FILE)
        os.makedirs(dest_dir, exist_ok=True)

        data["timestamp"] = datetime.now().isoformat()
        data["last_update"] = datetime.now().strftime("%Y-%m-%d %H:%M:%S")

        with open(tmp_path, "w") as f:
            json.dump(data, f, indent=2)
            f.flush()
            os.fsync(f.fileno())
        os.replace(tmp_path, DATA_FILE)
        os.chmod(DATA_FILE, 0o644)
    except Exception as e:
        print(f"Error writing sensor data: {e}")
        try:
            if os.path.exists(tmp_path):
                os.unlink(tmp_path)
        except OSError:
            pass


def log_message(message):
    """Log message to file"""
    try:
        os.makedirs(os.path.dirname(LOG_FILE), exist_ok=True)
        with open(LOG_FILE, 'a') as f:
            timestamp = datetime.now().strftime("%Y-%m-%d %H:%M:%S")
            f.write(f"[{timestamp}] {message}\n")
    except Exception as e:
        print(f"Error logging: {e}")


def is_daylight_hours():
    """Check if current time is within daylight capture hours"""
    if not ENABLE_DAYLIGHT_ONLY:
        return True
    
    current_time = datetime.now().time()
    start_time = datetime.strptime(f"{CAPTURE_START_HOUR:02d}:00:00", "%H:%M:%S").time()
    end_time = datetime.strptime(f"{CAPTURE_END_HOUR:02d}:00:00", "%H:%M:%S").time()
    
    return start_time <= current_time <= end_time


def capture_image():
    """Capture a timelapse image using rpicam-still"""
    try:
        # Check if we should capture based on daylight hours
        if not is_daylight_hours():
            log_message(f"Skipping capture - outside daylight hours ({CAPTURE_START_HOUR}:00-{CAPTURE_END_HOUR}:00)")
            return False
        
        # Ensure image directory exists
        os.makedirs(IMAGE_DIR, exist_ok=True)
        
        # Generate filename with timestamp
        timestamp = datetime.now().strftime("%Y-%m-%d_%H-%M-%S")
        filename = f"image_{timestamp}.jpg"
        filepath = os.path.join(IMAGE_DIR, filename)
        
        log_message(f"Attempting to capture image to: {filepath}")
        
        # Capture image using rpicam-still
        # -o specifies output file
        # --timeout 1 means capture after 1 second (small delay for camera to initialize)
        # --nopreview disables preview window
        # --immediate captures immediately without preview delay
        # Note: On Raspberry Pi, camera access may require sudo or user in video group
        # Redirect stderr to avoid blocking on verbose camera initialization messages
        with open(os.devnull, 'w') as devnull:
            result = subprocess.run(
                ["rpicam-still", "-o", filepath, "--timeout", "1", "--nopreview", "--immediate"],
                stdout=devnull,
                stderr=devnull,
                timeout=60,  # Increased timeout to 60 seconds for camera initialization
                check=False  # Don't raise exception on non-zero return code
            )
        
        if result.returncode == 0:
            # Verify file was created
            if os.path.exists(filepath):
                # Set permissions so web server can serve the image
                os.chmod(filepath, 0o644)
                file_size = os.path.getsize(filepath)
                message = f"Captured image: {filename} ({file_size} bytes)"
                print(message)
                log_message(message)
                return True
            else:
                error_msg = f"rpicam-still returned success but file not created: {filepath}"
                print(f"ERROR: {error_msg}")
                log_message(error_msg)
                return False
        else:
            error_msg = f"Failed to capture image. Return code: {result.returncode}. Check camera permissions and that rpicam-still is working."
            print(f"ERROR: {error_msg}")
            log_message(error_msg)
            return False
            
    except subprocess.TimeoutExpired:
        error_msg = "Image capture timed out after 60 seconds"
        print(f"ERROR: {error_msg}")
        log_message(error_msg)
        return False
    except FileNotFoundError:
        error_msg = "rpicam-still not found. Install with: sudo apt install -y rpicam-apps"
        print(f"ERROR: {error_msg}")
        log_message(error_msg)
        return False
    except Exception as e:
        error_msg = f"Error capturing image: {e}"
        print(f"ERROR: {error_msg}")
        log_message(error_msg)
        import traceback
        log_message(f"Traceback: {traceback.format_exc()}")
        return False


def timelapse_worker():
    """Worker thread function to capture timelapse images periodically"""
    # Wait a bit before first capture to let system settle
    time.sleep(5)
    
    # Test if rpicam-still is available
    try:
        result = subprocess.run(
            ["which", "rpicam-still"],
            capture_output=True,
            text=True,
            timeout=5
        )
        if result.returncode != 0:
            error_msg = "rpicam-still not found in PATH. Install it with: sudo apt install -y rpicam-apps"
            print(f"ERROR: {error_msg}")
            log_message(error_msg)
            return
        else:
            log_message(f"rpicam-still found at: {result.stdout.strip()}")
    except Exception as e:
        error_msg = f"Error checking for rpicam-still: {e}"
        print(f"ERROR: {error_msg}")
        log_message(error_msg)
    
    log_message("Timelapse worker thread started")
    print("Timelapse worker thread started")
    
    while True:
        try:
            log_message(f"Attempting to capture image (interval: {TIMELAPSE_INTERVAL}s)")
            success = capture_image()
            if success:
                log_message("Image capture successful")
            else:
                log_message("Image capture failed - check logs for details")
            time.sleep(TIMELAPSE_INTERVAL)
        except Exception as e:
            error_msg = f"Error in timelapse worker: {e}"
            print(f"ERROR: {error_msg}")
            log_message(error_msg)
            import traceback
            log_message(f"Traceback: {traceback.format_exc()}")
            time.sleep(TIMELAPSE_INTERVAL)  # Wait before retrying


def maybe_log_sensor_summary():
    """Rate-limited combined log line (greenhouse + optional watering)."""
    with data_lock:
        now = time.time()
        if now - _parse_diag["last_sensor_log"] < SENSOR_UPDATE_LOG_INTERVAL:
            return
        _parse_diag["last_sensor_log"] = now
        sd = dict(sensor_data)
    detail = (
        f"Updated: {sd['moisture_percent']}% moisture, "
        f"{sd['temperature_c']:.1f}°C, "
        f"{sd['humidity_rh']:.1f}%RH | "
        f"{sd['pressure_hpa']:.1f} hPa "
        f"AQI:{sd['aqi']} TVOC:{sd['tvoc']} eCO2:{sd['eco2']}"
    )
    if sd.get("watering_last_update") is not None:
        wm = sd.get("watering_soil_moisture")
        wp = sd.get("watering_pump_seconds")
        if wm is not None and wp is not None:
            detail += (
                f" | Watering: {wm:.1f}% pump {wp:.1f}s "
                f"(at {sd['watering_last_update']})"
            )
    print(detail)
    log_message(detail)


def serial_reader_loop(role, port_name):
    """
    role: 'greenhouse' (sensor-platform) or 'watering' (automatic_watering).
    port_name: serial device path or None if not configured.
    """
    ser = None
    label = "greenhouse" if role == "greenhouse" else "watering"
    while True:
        if port_name is None:
            time.sleep(10)
            continue
        if ser is None or not ser.is_open:
            try:
                ser = serial.Serial(port_name, SERIAL_BAUDRATE, timeout=SERIAL_TIMEOUT)
                print(f"Connected {label} Pico on {port_name}")
                log_message(f"Connected {label} Pico on {port_name}")
                time.sleep(2)
            except Exception as e:
                print(f"Error connecting {label} to {port_name}: {e}")
                log_message(f"Error connecting {label} to {port_name}: {e}")
                ser = None
                time.sleep(5)
                continue
        try:
            if ser.in_waiting > 0:
                line = ser.readline().decode("utf-8", errors="ignore").strip()
                if not line:
                    pass
                elif role == "greenhouse":
                    parsed = parse_sensor_line(line)
                    if parsed:
                        with data_lock:
                            sensor_data.update(parsed)
                            write_sensor_data(sensor_data)
                        maybe_log_sensor_summary()
                    else:
                        if "Atmospheric" in line or "Sensor" in line:
                            print(f"Pico message ({label}): {line}")
                            log_message(f"Pico message ({label}): {line}")
                        elif line.startswith("Moisture:"):
                            now = time.time()
                            if (
                                now - _parse_diag["last_moisture_fail_log"]
                                >= MOISTURE_PARSE_FAIL_LOG_INTERVAL
                            ):
                                _parse_diag["last_moisture_fail_log"] = now
                                snippet = line[:200] + ("…" if len(line) > 200 else "")
                                msg = f"Greenhouse line did not parse: {snippet}"
                                print(msg)
                                log_message(msg)
                else:
                    parsed = parse_watering_line(line)
                    if parsed:
                        wlu = datetime.now().strftime("%Y-%m-%d %H:%M:%S")
                        with data_lock:
                            sensor_data["watering_soil_moisture"] = parsed[
                                "watering_soil_moisture"
                            ]
                            sensor_data["watering_pump_seconds"] = parsed[
                                "watering_pump_seconds"
                            ]
                            sensor_data["watering_last_update"] = wlu
                            write_sensor_data(sensor_data)
                        msg = (
                            f"Watering: soil {parsed['watering_soil_moisture']:.1f}% "
                            f"pump {parsed['watering_pump_seconds']:.1f}s"
                        )
                        print(msg)
                        log_message(msg)
                        maybe_log_sensor_summary()
                    elif line:
                        now = time.time()
                        if (
                            now - _parse_diag.get("last_watering_fail_log", 0.0)
                            >= MOISTURE_PARSE_FAIL_LOG_INTERVAL
                        ):
                            _parse_diag["last_watering_fail_log"] = now
                            snippet = repr(line[:200])
                            msg = f"Watering raw (no parse): {snippet}"
                            print(msg)
                            log_message(msg)
            time.sleep(0.1)
        except serial.SerialException as e:
            print(f"Serial error ({label}): {e}")
            log_message(f"Serial error ({label}): {e}")
            try:
                ser.close()
            except Exception:
                pass
            ser = None
            time.sleep(5)
        except Exception as e:
            print(f"Unexpected error ({label}): {e}")
            log_message(f"Unexpected error ({label}): {e}")
            time.sleep(1)


def main():
    """Start timelapse capture and one serial reader thread per configured Pico."""
    started_at = datetime.now().strftime("%Y-%m-%d %H:%M:%S")
    print(f"Sensor Timelapse Script v{VERSION} starting at {started_at}...")
    log_message(f"Sensor Timelapse Script v{VERSION} starting at {started_at}")

    gh_port, wt_port = resolve_greenhouse_and_watering_ports()
    auto_list = list_usb_serial_devices()
    log_message(
        f"Serial ports: auto-detected={auto_list}, "
        f"greenhouse={gh_port!r}, watering={wt_port!r}"
    )
    print(
        f"Pico serial - greenhouse: {gh_port or 'none'}, "
        f"watering: {wt_port or 'none'} "
        f"(set PICO_GREENHOUSE_PORT / PICO_WATERING_PORT to override)"
    )

    timelapse_thread = threading.Thread(target=timelapse_worker, daemon=True)
    timelapse_thread.start()
    print(f"Timelapse capture started (interval: {TIMELAPSE_INTERVAL} seconds)")
    log_message(f"Timelapse capture started (interval: {TIMELAPSE_INTERVAL} seconds)")

    threading.Thread(
        target=serial_reader_loop, args=("greenhouse", gh_port), daemon=True
    ).start()
    threading.Thread(
        target=serial_reader_loop, args=("watering", wt_port), daemon=True
    ).start()

    try:
        while True:
            time.sleep(3600)
    except KeyboardInterrupt:
        raise


if __name__ == "__main__":
    try:
        main()
    except KeyboardInterrupt:
        print("\nShutting down...")
        log_message("Script stopped by user")

