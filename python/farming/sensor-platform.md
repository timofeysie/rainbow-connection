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

### Nginx Web Server Setup

Before setting up the sensor integration, you need to install and configure Nginx web server on your Raspberry Pi 5. This matches the setup used in the original timelapse project.

1. Install Nginx:

   ```bash
   sudo apt-get update
   sudo apt-get install nginx -y
   ```

2. Check Nginx status:

   ```bash
   sudo systemctl status nginx.service
   ```

3. Create the web directory structure:

   ```bash
   sudo mkdir -p /var/www/html/images
   sudo chmod 755 /var/www/html/images
   ```

4. Configure Nginx to serve the web interface. Edit the default site configuration:

   ```bash
   sudo nano /etc/nginx/sites-available/default
   ```

   Add or verify the following location block for the images directory:

   ```nginx
   server {
       listen 80 default_server;
       listen [::]:80 default_server;
       
       root /var/www/html;
       index index.html;
       
       server_name _;
       
       location /images/ {
           alias /var/www/html/images/;
           autoindex on;
       }
   }
   ```

5. Test Nginx configuration:

   ```bash
   sudo nginx -t
   ```

6. Restart Nginx to apply changes:

   ```bash
   sudo systemctl restart nginx.service
   ```

   Or use:

   ```bash
   sudo service nginx restart
   ```

7. Verify Nginx is running by visiting your Raspberry Pi's IP address in a web browser. You should see the default Nginx page or your custom index.html.

### Setup Instructions

1. Install required Python package on Raspberry Pi 5:

   ```bash
   pip3 install pyserial
   ```

2. Clone or update the repository on your Raspberry Pi 5 (if not already done):

   ```bash
   # If cloning for the first time:
   cd ~/repos
   git clone <your-repo-url> rainbow-connection
   
   # Or if already cloned, just pull updates:
   cd ~/repos/rainbow-connection
   git pull
   ```

3. Make the script executable:

   ```bash
   chmod +x ~/repos/rainbow-connection/python/farming/sensor-timelapse-script.py
   ```

4. Set up proper permissions for the images directory:

   ```bash
   sudo mkdir -p /var/www/html/images
   sudo chmod 775 /var/www/html/images
   sudo chown -R www-data:www-data /var/www/html/images
   # Add your user to www-data group to write images
   sudo usermod -a -G www-data $USER
   ```

   **Note:** You'll need to log out and back in (or reboot) for group changes to take effect. Alternatively, you can run the script with sudo.

5. Copy the HTML file to replace the existing index.html:

   ```bash
   sudo cp ~/repos/rainbow-connection/python/farming/farming-index.html /var/www/html/index.html
   ```

6. Run the sensor script (as a service or manually) from the repo location:

   ```bash
   sudo python3 ~/repos/rainbow-connection/python/farming/sensor-timelapse-script.py
   ```

   **Note:** Running from the repo means when you `git pull` to get updates, you'll automatically use the latest version of the script. The path is `~/repos/rainbow-connection` based on your setup.

7. Connect your Raspberry Pi Pico to the Raspberry Pi 5 via USB. The script will automatically detect the Pico's serial port.

**Alternative:** If you prefer to copy the script to a fixed location (like `/home/tim/python/`), first create the directory:

   ```bash
   mkdir -p /home/tim/python
   sudo cp ~/repos/rainbow-connection/python/farming/sensor-timelapse-script.py /home/tim/python/
   sudo chmod +x /home/tim/python/sensor-timelapse-script.py
   ```

   Then run it from there:

   ```bash
   sudo python3 /home/tim/python/sensor-timelapse-script.py
   ```

   **Note:** If you use this approach, you'll need to re-copy the script after each `git pull` to get updates.

The web interface will display both timelapse images and live sensor data. Sensor data updates every 2 seconds, and the status indicator shows green when data is being received.

### Troubleshooting

If sensor data is showing but no images are being captured:

1. Check the log file for errors:

   ```bash
   sudo tail -f /var/log/sensor-timelapse.log
   ```

2. Verify `rpicam-still` is installed:

   ```bash
   which rpicam-still
   ```

   If not found, install it:

   ```bash
   sudo apt update
   sudo apt install -y rpicam-apps
   ```

3. Test camera capture manually:

   ```bash
   rpicam-still -o /var/www/html/images/test.jpg --timeout 1 --nopreview --immediate
   ```

   If you get permission errors, try with sudo:

   ```bash
   sudo rpicam-still -o /var/www/html/images/test.jpg --timeout 1 --nopreview --immediate
   ```

   **Note:** `--timeout 0` can cause the command to hang. Use `--timeout 1` with `--immediate` for faster capture.

   If sudo works, you may need to add your user to the video group:

   ```bash
   sudo usermod -a -G video $USER
   ```

   Then log out and back in, or reboot.

4. Check if the script is running:

   ```bash
   ps aux | grep sensor-timelapse-script.py
   ```

5. Verify the script has proper permissions and is executable:

   ```bash
   ls -l ~/rainbow-connection/python/farming/sensor-timelapse-script.py
   chmod +x ~/rainbow-connection/python/farming/sensor-timelapse-script.py
   ```

6. Run the script manually to see output:

   ```bash
   sudo python3 ~/repos/rainbow-connection/python/farming/sensor-timelapse-script.py
   ```

7. To find where the script is located:

   ```bash
   find ~ -name "sensor-timelapse-script.py" 2>/dev/null
   # Or check if it's in the repo:
   ls -l ~/repos/rainbow-connection/python/farming/sensor-timelapse-script.py
   ```

8. Fix image directory permissions if you can't write images:

   ```bash
   sudo chmod 775 /var/www/html/images
   sudo chown -R www-data:www-data /var/www/html/images
   sudo usermod -a -G www-data $USER
   ```

   Then log out and back in, or reboot for group changes to take effect.

   Look for messages like "Timelapse worker thread started" and "Attempting to capture image".

7. Check image directory permissions:

   ```bash
   ls -ld /var/www/html/images
   sudo chmod 755 /var/www/html/images
   ```

The script captures images every 60 seconds by default (configurable via `TIMELAPSE_INTERVAL` in the script).