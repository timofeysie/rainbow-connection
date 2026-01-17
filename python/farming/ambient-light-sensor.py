# -*- coding:utf-8 -*-
# Ambient Light Sensor Logger for Raspberry Pi Pico W v0.1.0
# PiicoDev Ambient Light Sensor VEML6030
# Records light readings all day and tracks direct sunlight hours
# Designed to run in a sealed plastic box with clear cover in a garden spot

from PiicoDev_VEML6030 import PiicoDev_VEML6030
from PiicoDev_Unified import sleep_ms
import time

# File paths for data logging
LUX_LOG_FILE = "lux_readings.csv"
SUNLIGHT_HOURS_FILE = "sunlight_hours.txt"

# Initialize the light sensor
light_sensor = PiicoDev_VEML6030()

# Direct sunlight threshold (lux) - based on ambient-light-sensor.md
DIRECT_SUN_LUX = 40000

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

print("Ambient Light Sensor Logger Started")
print(f"Light sensor initialized. Direct sun threshold: {DIRECT_SUN_LUX} lux")
print(f"Lux readings will be saved to: {LUX_LOG_FILE}")
print(f"Sunlight hours will be saved to: {SUNLIGHT_HOURS_FILE}")

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
    
    # Log lux reading to file (with timestamp)
    current_time = time.time()
    write_lux_reading(lux, current_time)
    
    # Print to console for debugging
    print(f"Light: {lux:.0f} lux | Sun: {sunlight_hours:.2f}h")
    
    # Wait before next reading (500ms = 2 readings per second)
    sleep_ms(500)
