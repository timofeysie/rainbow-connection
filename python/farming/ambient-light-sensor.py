# -*- coding:utf-8 -*-
# Ambient Light Sensor Logger for Raspberry Pi Pico W v0.2.0
# PiicoDev Ambient Light Sensor VEML6030
# Records light readings all day and tracks direct sunlight hours
# Designed to run in a sealed plastic box with clear cover in a garden spot
# Includes BLE broadcasting for mobile phone access

from PiicoDev_VEML6030 import PiicoDev_VEML6030
from PiicoDev_Unified import sleep_ms
import time
import bluetooth
import struct
import json
from ble_advertising import advertising_payload
from micropython import const

# File paths for data logging
LUX_LOG_FILE = "lux_readings.csv"
SUNLIGHT_HOURS_FILE = "sunlight_hours.txt"

# Initialize the light sensor
light_sensor = PiicoDev_VEML6030()

# Direct sunlight threshold (lux) - based on ambient-light-sensor.md
DIRECT_SUN_LUX = 40000

# BLE constants
_IRQ_CENTRAL_CONNECT = const(1)
_IRQ_CENTRAL_DISCONNECT = const(2)
_IRQ_GATTS_READ = const(6)

_FLAG_READ = const(0x0002)

# Service and Characteristic UUIDs
_LIGHT_SERVICE_UUID = bluetooth.UUID("A5B1C2D3-E4F5-A6B7-C8D9-E0F1A2B3C4D5")
_LUX_CHAR_UUID = bluetooth.UUID("A5B1C2D3-E4F5-A6B7-C8D9-000000000001")
_SUNLIGHT_HOURS_CHAR_UUID = bluetooth.UUID("A5B1C2D3-E4F5-A6B7-C8D9-000000000002")
_STATS_CHAR_UUID = bluetooth.UUID("A5B1C2D3-E4F5-A6B7-C8D9-000000000003")

# Track sunlight hours per day
# Store: (day_start_timestamp, total_sunlight_seconds)
sunlight_tracker = {
    "day_start": None,
    "total_seconds": 0,
    "last_update": time.time(),
    "last_day_saved": None
}

def read_light():
    """Read ambient light sensor value in lux"""
    try:
        lux = light_sensor.read()
        return lux
    except:
        return 0

def write_lux_reading(lux, timestamp):
    """Write lux reading with timestamp to CSV file"""
    try:
        with open(LUX_LOG_FILE, "a") as f:
            f.write(f"{timestamp},{lux:.2f}\n")
    except Exception as e:
        # Silently fail if file write doesn't work (e.g., no SD card)
        pass

def save_sunlight_hours(hours, day_seconds):
    """Save daily sunlight hours to file"""
    try:
        with open(SUNLIGHT_HOURS_FILE, "a") as f:
            f.write(f"Day {day_seconds // 86400}: {hours:.2f} hours\n")
    except Exception as e:
        # Silently fail if file write doesn't work
        pass

def update_sunlight_tracking(lux):
    """Track direct sunlight hours per day"""
    current_time = time.time()
    
    # Get current day (simple approach: reset at midnight based on seconds since boot)
    # For a more accurate day tracking, you'd need RTC, but this works for daily tracking
    seconds_since_boot = current_time
    # Approximate day reset: every 86400 seconds (24 hours)
    # In practice, you might want to use RTC for actual day tracking
    day_seconds = int(seconds_since_boot) % 86400
    day_number = int(seconds_since_boot) // 86400
    
    # Initialize day tracking if needed
    if sunlight_tracker["day_start"] is None:
        sunlight_tracker["day_start"] = day_seconds
        sunlight_tracker["total_seconds"] = 0
        sunlight_tracker["last_day_saved"] = day_number
    
    # Check if new day (simple reset logic)
    if day_seconds < sunlight_tracker["day_start"]:
        # Day has rolled over - save previous day's total before resetting
        prev_hours = sunlight_tracker["total_seconds"] / 3600.0
        prev_day = sunlight_tracker["last_day_saved"]
        if prev_day is not None:
            save_sunlight_hours(prev_hours, prev_day * 86400)
        
        # Reset for new day
        sunlight_tracker["day_start"] = day_seconds
        sunlight_tracker["total_seconds"] = 0
        sunlight_tracker["last_day_saved"] = day_number
        day_changed = True
    
    # If lux exceeds threshold, add time since last update
    time_delta = current_time - sunlight_tracker["last_update"]
    if lux >= DIRECT_SUN_LUX and time_delta > 0:
        sunlight_tracker["total_seconds"] += time_delta
    
    sunlight_tracker["last_update"] = current_time
    
    # Convert to hours
    sunlight_hours = sunlight_tracker["total_seconds"] / 3600.0
    
    return sunlight_hours

# Statistics tracking
stats_tracker = {
    "readings_today": 0,
    "total_lux": 0.0,
    "max_lux": 0.0,
    "day_number": None
}

def calculate_statistics(lux):
    """Calculate statistics for today's readings"""
    current_time = time.time()
    seconds_since_boot = current_time
    day_number = int(seconds_since_boot) // 86400
    
    # Reset stats if new day
    if stats_tracker["day_number"] is None:
        stats_tracker["day_number"] = day_number
    
    if stats_tracker["day_number"] != day_number:
        # New day - reset statistics
        stats_tracker["readings_today"] = 0
        stats_tracker["total_lux"] = 0.0
        stats_tracker["max_lux"] = 0.0
        stats_tracker["day_number"] = day_number
    
    # Update statistics
    stats_tracker["readings_today"] += 1
    stats_tracker["total_lux"] += lux
    if lux > stats_tracker["max_lux"]:
        stats_tracker["max_lux"] = lux
    
    # Calculate average
    avg_lux = stats_tracker["total_lux"] / stats_tracker["readings_today"] if stats_tracker["readings_today"] > 0 else 0.0
    
    return {
        "readings_today": stats_tracker["readings_today"],
        "avg_lux": avg_lux,
        "max_lux": stats_tracker["max_lux"]
    }

class LightSensorPeripheral:
    """BLE Peripheral for ambient light sensor data"""
    
    def __init__(self, ble, name="Garden-Light-Sensor"):
        self._ble = ble
        # Force BLE stack reset to clear cached name
        self._ble.active(False)
        time.sleep(0.1)
        self._ble.active(True)
        time.sleep(0.1)
        self._ble.irq(self._irq)
        
        # Register service with characteristics
        _LIGHT_SERVICE = (
            _LIGHT_SERVICE_UUID,
            (
                (_LUX_CHAR_UUID, _FLAG_READ),
                (_SUNLIGHT_HOURS_CHAR_UUID, _FLAG_READ),
                (_STATS_CHAR_UUID, _FLAG_READ),
            ),
        )
        
        ((self._handle_lux, self._handle_hours, self._handle_stats),) = self._ble.gatts_register_services((_LIGHT_SERVICE,))
        
        print(f"BLE: Service UUID: {_LIGHT_SERVICE_UUID}")
        print(f"BLE: Registered service with handles:")
        print(f"  - Lux Characteristic (UUID: {_LUX_CHAR_UUID}) -> Handle: {self._handle_lux}")
        print(f"  - Hours Characteristic (UUID: {_SUNLIGHT_HOURS_CHAR_UUID}) -> Handle: {self._handle_hours}")
        print(f"  - Stats Characteristic (UUID: {_STATS_CHAR_UUID}) -> Handle: {self._handle_stats}")
        
        # Verify handles are valid (non-zero)
        if self._handle_lux == 0 or self._handle_hours == 0 or self._handle_stats == 0:
            print("ERROR: One or more characteristics failed to register!")
        
        self._connections = set()
        # Ensure BLE-only advertising (not BR/EDR compatible)
        self._payload = advertising_payload(name=name, services=[_LIGHT_SERVICE_UUID], br_edr=False)
        
        # Initialize characteristic values
        self._lux_value = struct.pack("<f", 0.0)
        self._hours_value = struct.pack("<f", 0.0)
        self._stats_value = json.dumps({}).encode('utf-8')[:512]
        
        # Write initial values
        try:
            self._ble.gatts_write(self._handle_lux, self._lux_value)
            print(f"BLE: Wrote initial value to Lux characteristic (handle {self._handle_lux})")
        except Exception as e:
            print(f"BLE: Error writing to Lux handle {self._handle_lux}: {e}")
            
        try:
            self._ble.gatts_write(self._handle_hours, self._hours_value)
            print(f"BLE: Wrote initial value to Hours characteristic (handle {self._handle_hours})")
        except Exception as e:
            print(f"BLE: Error writing to Hours handle {self._handle_hours}: {e}")
            
        try:
            self._ble.gatts_write(self._handle_stats, self._stats_value)
            print(f"BLE: Wrote initial value to Stats characteristic (handle {self._handle_stats})")
        except Exception as e:
            print(f"BLE: Error writing to Stats handle {self._handle_stats}: {e}")
        
        self._advertise()
    
    def _irq(self, event, data):
        """Handle BLE IRQ events"""
        if event == _IRQ_CENTRAL_CONNECT:
            conn_handle, addr_type, addr = data
            print("=" * 50)
            print(f"BLE: CONNECTED - Handle: {conn_handle}, Addr: {addr}")
            print("=" * 50)
            self._connections.add(conn_handle)
        elif event == _IRQ_CENTRAL_DISCONNECT:
            conn_handle, addr_type, addr = data
            print("=" * 50)
            print(f"BLE: DISCONNECTED - Handle: {conn_handle}, Addr: {addr}")
            print("=" * 50)
            self._connections.remove(conn_handle)
            self._advertise()
        elif event == _IRQ_GATTS_READ:
            conn_handle, value_handle = data
            # Determine which characteristic was read
            char_name = "Unknown"
            if value_handle == self._handle_lux:
                char_name = "LUX"
            elif value_handle == self._handle_hours:
                char_name = "HOURS"
            elif value_handle == self._handle_stats:
                char_name = "STATS"
            print(f"BLE: READ REQUEST - Handle: {conn_handle}, Char Handle: {value_handle} ({char_name})")
            # Read requests are handled automatically by gatts_read
            pass
    
    def update_values(self, lux, sunlight_hours, stats):
        """Update characteristic values with new sensor data"""
        try:
            # Update lux characteristic (float32, little-endian)
            self._lux_value = struct.pack("<f", float(lux))
            self._ble.gatts_write(self._handle_lux, self._lux_value)
            
            # Update sunlight hours characteristic (float32, little-endian)
            self._hours_value = struct.pack("<f", float(sunlight_hours))
            self._ble.gatts_write(self._handle_hours, self._hours_value)
            
            # Update statistics characteristic (JSON string, max 512 bytes)
            stats_json = json.dumps({
                "current_lux": lux,
                "sunlight_hours": sunlight_hours,
                "readings_today": stats.get("readings_today", 0),
                "avg_lux": stats.get("avg_lux", 0.0),
                "max_lux": stats.get("max_lux", 0.0)
            })
            self._stats_value = stats_json.encode('utf-8')[:512]
            self._ble.gatts_write(self._handle_stats, self._stats_value)
        except Exception as e:
            # Silently fail if BLE update fails
            pass
    
    def _advertise(self, interval_us=500000):
        """Start advertising the BLE service"""
        self._ble.gap_advertise(interval_us, adv_data=self._payload)
    
    def is_connected(self):
        """Check if any central device is connected"""
        return len(self._connections) > 0

print("Ambient Light Sensor Logger Started")
print(f"Light sensor initialized. Direct sun threshold: {DIRECT_SUN_LUX} lux")
print(f"Lux readings will be saved to: {LUX_LOG_FILE}")
print(f"Sunlight hours will be saved to: {SUNLIGHT_HOURS_FILE}")

# Initialize BLE peripheral
try:
    ble = bluetooth.BLE()
    print("Initializing BLE...")
    ble_peripheral = LightSensorPeripheral(ble, "Garden-Light-Sensor")
    print("=" * 50)
    print("BLE advertising started: 'Garden-Light-Sensor'")
    print("Waiting for connections...")
    print("=" * 50)
except Exception as e:
    print(f"BLE initialization failed: {e}")
    ble_peripheral = None

# Initialize lux log file with header if it doesn't exist
try:
    with open(LUX_LOG_FILE, "r") as f:
        pass  # File exists, don't overwrite
except:
    try:
        with open(LUX_LOG_FILE, "w") as f:
            f.write("timestamp,lux\n")
    except:
        pass  # Can't write, might not have storage

# Main loop: read and log light readings continuously
while True:
    # Read light sensor
    lux = read_light()
    sunlight_hours = update_sunlight_tracking(lux)
    
    # Calculate statistics
    stats = calculate_statistics(lux)
    
    # Update BLE characteristics if BLE is initialized
    if ble_peripheral is not None:
        try:
            ble_peripheral.update_values(lux, sunlight_hours, stats)
        except Exception as e:
            # Silently fail if BLE update fails
            pass
    
    # Log lux reading to file (with timestamp)
    current_time = time.time()
    write_lux_reading(lux, current_time)
    
    # Print connection status (commented out regular sensor output for debugging)
    if ble_peripheral is not None:
        if ble_peripheral.is_connected():
            print(f"BLE: Connected | Light: {lux:.0f} lux | Sun: {sunlight_hours:.2f}h")
        # else:
        #     print(f"BLE: Advertising (not connected)")
    # print(f"Light: {lux:.0f} lux | Sun: {sunlight_hours:.2f}h | Stats: {stats['readings_today']} readings, avg: {stats['avg_lux']:.0f}, max: {stats['max_lux']:.0f}")
    
    # Wait before next reading (500ms = 2 readings per second)
    sleep_ms(500)
