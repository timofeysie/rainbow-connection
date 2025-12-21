# Sensor Platform

This project describes a range of sensors for the Raspberry Pi Pico.

Moisture readings are done via the Capacitive Soil Moisture Sensor SKU SEN0193 connected now to a Raspberry Pi Pico.

The other sensors are the PiicoDev Atmospheric Sensor BME280 + Air Quality ENS160 + OLED Display Demo

This program reads Temperature, Pressure, Relative Humidity, AQI, TVOC, and eCO2 and displays Moisture, Temp+Humidity, Pressure as text rows, and air quality values as a single text line.

## Moisture Sensor

The Capacitive sensor can be bought for about 10$ from [Core Electronics](https://core-electronics.com.au/capacitive-soil-moisture-sensor-corrosion-resistant.html)

It includes an on-board voltage regulator which gives it an operating voltage range of 3.3 ~ 5.5V. It is compatible with low-voltage MCUs (both 3.3V and 5V logic). To make it compatible with a Raspberry Pi, an ADC converter is required.

See the [DFRobot wiki](https://wiki.dfrobot.com/Capacitive_Soil_Moisture_Sensor_SKU_SEN0193) for more information.

## Atmospheric, Air Quality Sensor, and OLED Display

The Atmospheric and other sensors are part of the PiicoDev platform.

It includes a BME280 sensor for temperature, pressure, and humidity, and an ENS160 sensor for air quality.

See the [PiicoDev wiki](https://core-electronics.com.au/piicodev.html) for more information.

## Integration with Raspberry Pi 5 Timelapse Project

This sensor platform can be integrated with a Raspberry Pi 5 running a timelapse camera project. The Pico connects via USB to the Pi 5, and sensor data is collected and displayed alongside timelapse images in a web interface.

### Setup Instructions

1. Install required Python package on Raspberry Pi 5:

   ```bash
   pip3 install pyserial
   ```

2. Copy the Python script to your Pi and make it executable:

   ```bash
   sudo cp python/farming/sensor-timelapse-script.py /home/tim/python/
   sudo chmod +x /home/tim/python/sensor-timelapse-script.py
   ```

3. Copy the HTML file to replace the existing index.html:

   ```bash
   sudo cp python/farming/farming-index.html /var/www/html/index.html
   ```

4. Run the sensor script (as a service or manually):

   ```bash
   sudo python3 /home/tim/python/sensor-timelapse-script.py
   ```

5. Connect your Raspberry Pi Pico to the Raspberry Pi 5 via USB. The script will automatically detect the Pico's serial port.

The web interface will display both timelapse images and live sensor data. Sensor data updates every 2 seconds, and the status indicator shows green when data is being received.