# Sensor Platform for the Raspberry Pi Pico v0.0.3
# Moisture readings are done via the Capacitive Soil Moisture Sensor SKU SEN0193 connected now to a Raspberry Pi Pico.
# The other sensors are the PiicoDev Atmospheric Sensor BME280 + Air Quality ENS160 + OLED Display Demo
# This program reads Temperature, Pressure, Relative Humidity, AQI, TVOC, and eCO2
# and displays Moisture, Temp+Humidity, Pressure as text rows, and air quality values as a single text line.
# Also includes PiicoDev Ambient Light Sensor VEML6030 for measuring direct sunlight hours.

import math
import machine
from PiicoDev_BME280 import PiicoDev_BME280
from PiicoDev_ENS160 import PiicoDev_ENS160
from PiicoDev_VEML6030 import PiicoDev_VEML6030
from PiicoDev_SSD1306 import *
from PiicoDev_Unified import sleep_ms
import time

# Initialize the sensors and display
sensor = PiicoDev_BME280()
air_sensor = PiicoDev_ENS160()
light_sensor = PiicoDev_VEML6030()
display = create_PiicoDev_SSD1306()

# Direct sunlight threshold (lux) - based on ambient-light-sensor.md
DIRECT_SUN_LUX = 40000

# Track sunlight hours per day
# Store: (day_start_timestamp, total_sunlight_seconds)
sunlight_tracker = {"day_start": None, "total_seconds": 0, "last_update": time.time()}

# Initialize ADC for moisture sensor on GP28 (Pin 28)
adc = machine.ADC(28)

def read_moisture():
    """Read moisture sensor value from ADC pin 28"""
    # Read raw ADC value (0-65535 for 16-bit ADC)
    raw_value = adc.read_u16()
    
    # Convert to voltage (0-3.3V)
    voltage = (raw_value / 65535) * 3.3
    
    # Convert to moisture percentage (adjusted based on calibration)
    # Your sensor readings: Air=59%, Water=77%
    # Map this range (59-77%) to proper moisture scale (0-100%)
    raw_moisture = ((3.3 - voltage) / 3.3) * 100
    
    # Calibrate: map 59-77% range to 0-100% moisture
    # Formula: (raw - 59) / (77 - 59) * 100
    moisture_percent = ((raw_moisture - 59) / 18) * 100
    
    # Clamp values between 0-100%
    moisture_percent = max(0, min(100, moisture_percent))
    
    return int(moisture_percent), raw_value

def read_light():
    """Read ambient light sensor value in lux"""
    try:
        lux = light_sensor.read()
        return lux
    except:
        return 0

def update_sunlight_tracking(lux):
    """Track direct sunlight hours per day"""
    current_time = time.time()
    
    # Get current day (simple approach: reset at midnight based on seconds since boot)
    # For a more accurate day tracking, you'd need RTC, but this works for daily tracking
    seconds_since_boot = current_time
    # Approximate day reset: every 86400 seconds (24 hours)
    # In practice, you might want to use RTC for actual day tracking
    day_seconds = int(seconds_since_boot) % 86400
    
    # Initialize day tracking if needed
    if sunlight_tracker["day_start"] is None:
        sunlight_tracker["day_start"] = day_seconds
        sunlight_tracker["total_seconds"] = 0
    
    # Check if new day (simple reset logic)
    if day_seconds < sunlight_tracker["day_start"]:
        # Day has rolled over
        sunlight_tracker["day_start"] = day_seconds
        sunlight_tracker["total_seconds"] = 0
    
    # If lux exceeds threshold, add time since last update
    time_delta = current_time - sunlight_tracker["last_update"]
    if lux >= DIRECT_SUN_LUX and time_delta > 0:
        sunlight_tracker["total_seconds"] += time_delta
    
    sunlight_tracker["last_update"] = current_time
    
    # Convert to hours
    sunlight_hours = sunlight_tracker["total_seconds"] / 3600.0
    
    return sunlight_hours

# Take initial readings for baseline
# Atmospheric
tempC, presPa, humRH = sensor.values()
pres_hPa = presPa / 100
# Air quality
aqi = air_sensor.aqi.value
try:
    tvoc = air_sensor.tvoc
except:
    tvoc = 0
try:
    eco2 = air_sensor.eco2.value
except:
    eco2 = 0

print("Atmospheric + Air Quality Sensor OLED Demo Started")
print("Moisture, Temp+Humidity, Pressure as text rows; AQI, TVOC, eCO2 as text.")
print(f"Light sensor initialized. Direct sun threshold: {DIRECT_SUN_LUX} lux")

while True:
    # Read atmospheric sensor data
    tempC, presPa, humRH = sensor.values()
    pres_hPa = presPa / 100
    # Read air quality sensor data
    aqi = air_sensor.aqi.value
    try:
        tvoc = air_sensor.tvoc
    except:
        tvoc = 0
    try:
        eco2 = air_sensor.eco2.value
    except:
        eco2 = 0
    
    # Read moisture sensor
    moisture_percent, raw_value = read_moisture()
    
    # Read light sensor
    lux = read_light()
    sunlight_hours = update_sunlight_tracking(lux)
    
    # Clear display
    display.fill(0)
    
    # Row 1: Moisture sensor and Light sensor (actual readings)
    # Format: "M:XX% L:XXXXX" where L shows lux (abbreviated if needed)
    moisture_text = f"M:{moisture_percent}%"
    # Format lux: show in thousands if > 1000, otherwise show full value
    if lux >= 1000:
        lux_display = f"L:{lux/1000:.1f}k"
    else:
        lux_display = f"L:{int(lux)}"
    # Position light reading to the right of moisture (starting around x=50)
    display.text(moisture_text, 0, 8, 1)
    display.text(lux_display, 50, 8, 1)
    
    # Row 2: Temperature and Humidity on same line
    temp_hum_text = f"T:{tempC:.2f}C H:{humRH:.2f}%"
    display.text(temp_hum_text, 0, 20, 1)
    
    # Row 3: Pressure
    pressure_text = f"P:{pres_hPa:.2f}Pa"
    display.text(pressure_text, 0, 32, 1)
    
    # Row 4: Air quality values as a single text line
    air_text = f"A:{aqi} T:{tvoc} eCO2:{eco2}"
    display.text(air_text, 0, 44, 1)
    
    # Update display
    display.show()
    
    # Print to console for debugging
    print(f"Moisture: {moisture_percent}% (raw: {raw_value}) | Light: {lux:.0f} lux | Sun: {sunlight_hours:.2f}h | {tempC:.1f} °C  {pres_hPa:.1f} hPa  {humRH:.1f} %RH  AQI:{aqi} TVOC:{tvoc} eCO2:{eco2}")
    
    # Wait before next reading
    sleep_ms(500)  # Update every 500ms

