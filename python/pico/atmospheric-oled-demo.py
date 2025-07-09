# PiicoDev Atmospheric Sensor BME280 + OLED Display Demo
# This program reads Temperature, Pressure and Relative Humidity
# from the PiicoDev Atmospheric Sensor and displays them as
# real-time plots on the PiicoDev OLED Module SSD1306

import math
from PiicoDev_BME280 import PiicoDev_BME280
from PiicoDev_SSD1306 import *
from PiicoDev_Unified import sleep_ms

# Initialize the sensor and display
sensor = PiicoDev_BME280()
display = create_PiicoDev_SSD1306()

# Take initial readings for baseline
tempC, presPa, humRH = sensor.values()
pres_hPa = presPa / 100

# Data storage for plotting (keep last 64 readings)
temp_history = []
pres_history = []
hum_history = []
max_history = 64

# Initialize history with current values
for i in range(max_history):
    temp_history.append(tempC)
    pres_history.append(pres_hPa)
    hum_history.append(humRH)

print("Atmospheric Sensor OLED Demo Started")
print("Temperature, Pressure, Humidity will be plotted in real-time")

while True:
    # Read sensor data
    tempC, presPa, humRH = sensor.values()
    pres_hPa = presPa / 100
    
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
    # Temperature plot (top section)
    temp_y_offset = 5
    temp_height = 18
    
    # Pressure plot (middle section)
    pres_y_offset = 28
    pres_height = 18
    
    # Humidity plot (bottom section)
    hum_y_offset = 51
    hum_height = 18
    
    # Plot temperature data
    display.text("T:", 0, temp_y_offset, 1)
    for i, temp in enumerate(temp_history):
        # Scale temperature to fit in plot area (assuming range 0 to 50°C)
        scaled_temp = int((temp / 50) * temp_height)
        y_pos = temp_y_offset + temp_height - scaled_temp
        x_pos = i * 2  # 2 pixels per data point
        if x_pos < WIDTH - 65:  # Leave space for label
            display.pixel(x_pos + 15, y_pos, 1)
    
    # Plot pressure data
    display.text("P:", 0, pres_y_offset, 1)
    for i, pres in enumerate(pres_history):
        # Scale pressure to fit in plot area (assuming range 950 to 1050 hPa)
        scaled_pres = int(((pres - 950) / 100) * pres_height)
        y_pos = pres_y_offset + pres_height - scaled_pres
        x_pos = i * 2
        if x_pos < WIDTH - 75:
            display.pixel(x_pos + 15, y_pos, 1)
    
    # Plot humidity data
    display.text("H:", 0, hum_y_offset, 1)
    for i, hum in enumerate(hum_history):
        # Scale humidity to fit in plot area (0-100%)
        scaled_hum = int((hum / 100) * hum_height)
        y_pos = hum_y_offset + hum_height - scaled_hum
        x_pos = i * 2
        if x_pos < WIDTH - 65:
            display.pixel(x_pos + 15, y_pos, 1)
    
    # Show current values as text (truncated to 2 decimal places)
    display.text(f"{tempC:.2f}C", WIDTH - 70, temp_y_offset, 1)
    display.text(f"{pres_hPa:.2f}hPa", WIDTH - 80, pres_y_offset, 1)
    display.text(f"{humRH:.2f}%", WIDTH - 60, hum_y_offset, 1)
    
    # Update display
    display.show()
    
    # Print to console for debugging
    print(f"{tempC:.1f} °C  {pres_hPa:.1f} hPa  {humRH:.1f} %RH")
    print(f"Humidity debug: raw={humRH}, scaled={int((humRH / 100) * hum_height)}, y_pos={hum_y_offset + hum_height - int((humRH / 100) * hum_height)}")
    
    # Wait before next reading
    sleep_ms(500)  # Update every 500ms
