# PiicoDev Atmospheric Sensor BME280 + Air Quality ENS160 + OLED Display Demo
# This program reads Temperature, Pressure, Relative Humidity, AQI, TVOC, and eCO2
# and displays Temp, Pressure, Humidity as plots, and air quality values as a single text line.

import math
from PiicoDev_BME280 import PiicoDev_BME280
from PiicoDev_ENS160 import PiicoDev_ENS160
from PiicoDev_SSD1306 import *
from PiicoDev_Unified import sleep_ms

# Initialize the sensors and display
sensor = PiicoDev_BME280()
air_sensor = PiicoDev_ENS160()
display = create_PiicoDev_SSD1306()

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

# Data storage for plotting (keep last 64 readings)
max_history = 64
temp_history = [tempC] * max_history
pres_history = [pres_hPa] * max_history
hum_history = [humRH] * max_history

print("Atmospheric + Air Quality Sensor OLED Demo Started")
print("Temp, Pressure, Humidity as plots; AQI, TVOC, eCO2 as text.")

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
    
    # Update history (FIFO)
    temp_history.pop(0)
    pres_history.pop(0)
    hum_history.pop(0)
    temp_history.append(tempC)
    pres_history.append(pres_hPa)
    hum_history.append(humRH)
    
    # Clear display
    display.fill(0)
    
    # Calculate plot positions and scaling
    # Each plot gets 16px height, 3 plots total, with 2px between each
    plot_height = 16
    plot_gap = 2
    y_offsets = [5]
    for i in range(2):
        y_offsets.append(y_offsets[-1] + plot_height + plot_gap)
    temp_y_offset, pres_y_offset, hum_y_offset = y_offsets
    
    # Plot temperature data
    display.text("T:", 0, temp_y_offset, 1)
    for i, temp in enumerate(temp_history):
        scaled_temp = int((temp / 50) * plot_height)
        y_pos = temp_y_offset + plot_height - scaled_temp
        x_pos = i * 2
        if x_pos < WIDTH - 65:
            display.pixel(x_pos + 15, y_pos, 1)
    # Plot pressure data
    display.text("P:", 0, pres_y_offset, 1)
    for i, pres in enumerate(pres_history):
        scaled_pres = int(((pres - 950) / 100) * plot_height)
        y_pos = pres_y_offset + plot_height - scaled_pres
        x_pos = i * 2
        if x_pos < WIDTH - 75:
            display.pixel(x_pos + 15, y_pos, 1)
    # Plot humidity data
    display.text("H:", 0, hum_y_offset, 1)
    for i, hum in enumerate(hum_history):
        scaled_hum = int((hum / 100) * plot_height)
        y_pos = hum_y_offset + plot_height - scaled_hum
        x_pos = i * 2
        if x_pos < WIDTH - 65:
            display.pixel(x_pos + 15, y_pos, 1)
    
    # Show current values as text (truncated to 2 decimal places)
    display.text(f"{tempC:.2f}C", WIDTH - 70, temp_y_offset, 1)
    display.text(f"{pres_hPa:.2f}hPa", WIDTH - 80, pres_y_offset, 1)
    display.text(f"{humRH:.2f}%", WIDTH - 60, hum_y_offset, 1)
    
    # Show air quality values as a single text line at the bottom
    air_text = f"A:{aqi} T:{tvoc} eCO2:{eco2}"
    display.text(air_text, 0, 56, 1)
    
    # Update display
    display.show()
    
    # Print to console for debugging
    print(f"{tempC:.1f} °C  {pres_hPa:.1f} hPa  {humRH:.1f} %RH  AQI:{aqi} TVOC:{tvoc} eCO2:{eco2}")
    
    # Wait before next reading
    sleep_ms(500)  # Update every 500ms
