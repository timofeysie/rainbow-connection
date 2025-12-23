#!/usr/bin/env python3
"""
Sensor Timelapse Script - Raspberry Pi 5
Reads sensor data from Raspberry Pi Pico via USB serial connection
and serves it for display in the timelapse web interface.

This script:
1. Connects to the Pico via USB serial
2. Parses sensor data from the Pico's print statements
3. Writes sensor data to a JSON file that the web interface can read
4. Captures timelapse images using rpicam-still
5. Optionally serves sensor data via HTTP endpoint

Usage:
    python3 sensor-timelapse-script.py

The script should be run as a service or via systemd on the Raspberry Pi 5.

Updated JavaScript for /var/www/html/script.js:
The updated JavaScript code that combines image gallery functionality with
sensor data display is included in farming-index.html. The JavaScript includes:
- Image gallery functionality (fetching images, play/stop, selection)
- Sensor data fetching and real-time updates
- Status indicators for sensor connectivity

See farming-index.html for the complete implementation.
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
from pathlib import Path

# Configuration
SERIAL_BAUDRATE = 115200
SERIAL_TIMEOUT = 1
DATA_FILE = "/var/www/html/sensor-data.json"
LOG_FILE = "/var/log/sensor-timelapse.log"
IMAGE_DIR = "/var/www/html/images"
TIMELAPSE_INTERVAL = 60  # Capture image every 60 seconds (adjust as needed)

# Daylight hours configuration (24-hour format)
CAPTURE_START_HOUR = 9   # Start capturing at 9 AM
CAPTURE_END_HOUR = 17    # Stop capturing at 5 PM (17:00)
ENABLE_DAYLIGHT_ONLY = True  # Set to False to capture 24/7

# Sensor data structure
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
    "last_update": ""
}


def find_pico_port():
    """Find the USB serial port connected to the Raspberry Pi Pico"""
    ports = serial.tools.list_ports.comports()
    
    # Common identifiers for Pico
    pico_identifiers = ["Pico", "Raspberry Pi Pico", "USB Serial", "ttyACM", "ttyUSB"]
    
    for port in ports:
        port_str = str(port)
        for identifier in pico_identifiers:
            if identifier.lower() in port_str.lower():
                print(f"Found Pico on port: {port.device}")
                return port.device
    
    # If no specific match, try to find any USB serial device
    for port in ports:
        if "USB" in port_str or "ACM" in port_str or "USB" in port_str:
            print(f"Trying USB serial port: {port.device}")
            return port.device
    
    return None


def parse_sensor_line(line):
    """
    Parse sensor data from Pico print statement:
    Format: "Moisture: {moisture}% (raw: {raw}) | {temp} °C  {pres} hPa  {hum} %RH  AQI:{aqi} TVOC:{tvoc} eCO2:{eco2}"
    """
    pattern = r"Moisture: (\d+)% \(raw: (\d+)\) \| ([\d.]+) °C  ([\d.]+) hPa  ([\d.]+) %RH  AQI:(\d+) TVOC:(\d+) eCO2:(\d+)"
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


def write_sensor_data(data):
    """Write sensor data to JSON file for web interface"""
    try:
        # Ensure directory exists
        os.makedirs(os.path.dirname(DATA_FILE), exist_ok=True)
        
        # Add timestamp
        data["timestamp"] = datetime.now().isoformat()
        data["last_update"] = datetime.now().strftime("%Y-%m-%d %H:%M:%S")
        
        # Write to file
        with open(DATA_FILE, 'w') as f:
            json.dump(data, f, indent=2)
        
        # Set permissions so web server can read it
        os.chmod(DATA_FILE, 0o644)
        
    except Exception as e:
        print(f"Error writing sensor data: {e}")


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


def main():
    """Main function to read serial data and update sensor data file"""
    port = None
    ser = None
    
    print("Sensor Timelapse Script Starting...")
    log_message("Sensor Timelapse Script Starting")
    
    # Start timelapse capture thread
    timelapse_thread = threading.Thread(target=timelapse_worker, daemon=True)
    timelapse_thread.start()
    print(f"Timelapse capture started (interval: {TIMELAPSE_INTERVAL} seconds)")
    log_message(f"Timelapse capture started (interval: {TIMELAPSE_INTERVAL} seconds)")
    
    # Find and connect to Pico
    while True:
        if ser is None or not ser.is_open:
            port = find_pico_port()
            
            if port is None:
                print("Pico not found. Retrying in 5 seconds...")
                log_message("Pico not found. Retrying...")
                time.sleep(5)
                continue
            
            try:
                ser = serial.Serial(port, SERIAL_BAUDRATE, timeout=SERIAL_TIMEOUT)
                print(f"Connected to Pico on {port}")
                log_message(f"Connected to Pico on {port}")
                time.sleep(2)  # Wait for connection to stabilize
            except Exception as e:
                print(f"Error connecting to {port}: {e}")
                log_message(f"Error connecting to {port}: {e}")
                ser = None
                time.sleep(5)
                continue
        
        try:
            # Read line from serial
            if ser.in_waiting > 0:
                line = ser.readline().decode('utf-8', errors='ignore').strip()
                
                if line:
                    # Try to parse sensor data
                    parsed = parse_sensor_line(line)
                    if parsed:
                        # Update sensor data
                        sensor_data.update(parsed)
                        write_sensor_data(sensor_data)
                        print(f"Updated: {sensor_data['moisture_percent']}% moisture, "
                              f"{sensor_data['temperature_c']:.1f}°C, "
                              f"{sensor_data['humidity_rh']:.1f}%RH")
                    else:
                        # Log other messages for debugging
                        if "Atmospheric" in line or "Sensor" in line:
                            print(f"Pico message: {line}")
                            log_message(f"Pico message: {line}")
            
            time.sleep(0.1)  # Small delay to prevent CPU spinning
            
        except serial.SerialException as e:
            print(f"Serial error: {e}")
            log_message(f"Serial error: {e}")
            ser.close()
            ser = None
            time.sleep(5)
        except Exception as e:
            print(f"Unexpected error: {e}")
            log_message(f"Unexpected error: {e}")
            time.sleep(1)


if __name__ == "__main__":
    try:
        main()
    except KeyboardInterrupt:
        print("\nShutting down...")
        log_message("Script stopped by user")

