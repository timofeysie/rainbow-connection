# Sensor Platform for the Raspberry Pi Pico v0.0.2
# Moisture readings are done via the Capacitive Soil Moisture Sensor SKU SEN0193 connected now to a Raspberry Pi Pico.
# The other sensors are the PiicoDev Atmospheric Sensor BME280 + Air Quality ENS160 + OLED Display Demo
# This program reads Temperature, Pressure, Relative Humidity, AQI, TVOC, and eCO2
# and displays Moisture, Temp+Humidity, Pressure as text rows, and air quality values as a single text line.

import math
import machine
from PiicoDev_BME280 import PiicoDev_BME280
from PiicoDev_ENS160 import PiicoDev_ENS160
from PiicoDev_SSD1306 import *
from PiicoDev_Unified import sleep_ms

# Initialize the sensors and display
sensor = PiicoDev_BME280()
air_sensor = PiicoDev_ENS160()
display = create_PiicoDev_SSD1306()

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
    
    # Clear display
    display.fill(0)
    
    # Row 1: Moisture sensor (actual reading)
    display.text(f"M:{moisture_percent}%", 0, 8, 1)
    
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
    print(f"Moisture: {moisture_percent}% (raw: {raw_value}) | {tempC:.1f} °C  {pres_hPa:.1f} hPa  {humRH:.1f} %RH  AQI:{aqi} TVOC:{tvoc} eCO2:{eco2}")
    
    # Wait before next reading
    sleep_ms(500)  # Update every 500ms

