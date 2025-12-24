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

   **Note:** Whenever you modify `farming-index.html` in the repo, you must copy it again to `/var/www/html/index.html` for the changes to appear on the website. Nginx serves files from `/var/www/html/`, not from the repo location.

6. Run the sensor script (as a service or manually) from the repo location:

   ```bash
   sudo python3 ~/repos/rainbow-connection/python/farming/sensor-timelapse-script.py
   ```

   **Note:** Running from the repo means when you `git pull` to get updates, you'll automatically use the latest version of the script. The path is `~/repos/rainbow-connection` based on your setup.

7. Connect your Raspberry Pi Pico to the Raspberry Pi 5 via USB. The script will automatically detect the Pico's serial port.

7. **Set up automatic startup with rc.local:**

   Copy the rc.local file to `/etc/rc.local`:

   ```bash
   sudo cp ~/repos/rainbow-connection/python/farming/rc.local /etc/rc.local
   sudo chmod +x /etc/rc.local
   ```

   Create the log file with proper permissions:

   ```bash
   sudo touch /home/tim/rc.local.log
   sudo chown tim:tim /home/tim/rc.local.log
   ```

   Verify rc-local service is enabled:

   ```bash
   sudo systemctl enable rc-local.service
   sudo systemctl status rc-local.service
   ```

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

**Daylight Hours:** By default, images are only captured during daylight hours (9 AM to 5 PM) to avoid dark images and save storage space. This can be configured in the script:

- `CAPTURE_START_HOUR = 9` - Start capturing at 9 AM
- `CAPTURE_END_HOUR = 17` - Stop capturing at 5 PM (17:00)
- `ENABLE_DAYLIGHT_ONLY = True` - Set to `False` to capture 24/7

To adjust these settings, edit the configuration section at the top of `sensor-timelapse-script.py`.

### Verification After Setup

After setting up and rebooting, use these commands to verify everything is working:

1. **Check if the script is running:**

   ```bash
   ps aux | grep sensor-timelapse-script.py
   ```

   You should see a process running. If not, check the rc.local log:

   ```bash
   cat /home/tim/rc.local.log
   ```

   **If the log file doesn't exist**, it means rc.local either hasn't run yet or failed before creating the log. Check:

   ```bash
   # Verify rc.local exists and is executable
   ls -l /etc/rc.local
   sudo chmod +x /etc/rc.local
   
   # Check rc-local service status
   sudo systemctl status rc-local.service
   
   # Create the log file manually if needed
   sudo touch /home/tim/rc.local.log
   sudo chown tim:tim /home/tim/rc.local.log
   
   # Test rc.local manually to see if it works
   sudo /etc/rc.local
   cat /home/tim/rc.local.log
   ```

   **If the script isn't running after reboot**, verify:
   
   ```bash
   # Check if rc.local content is correct
   sudo cat /etc/rc.local
   
   # Make sure rc-local service is enabled
   sudo systemctl enable rc-local.service
   
   # Check service logs for errors
   sudo journalctl -u rc-local.service -n 50
   ```

2. **Check the script's log file for activity:**

   ```bash
   sudo tail -f /var/log/sensor-timelapse.log
   ```

   Look for:
   - "Sensor Timelapse Script Starting"
   - "Connected to Pico on /dev/ttyACM0"
   - "Timelapse worker thread started"
   - "Attempting to capture image"
   - "Captured image: ..." or "Skipping capture - outside daylight hours"

3. **Verify Pico is connected:**

   ```bash
   ls -l /dev/ttyACM*
   ```

   Should show `/dev/ttyACM0` or similar.

4. **Check if sensor data is being updated:**

   ```bash
   cat /var/www/html/sensor-data.json
   ```

   Should show current sensor values with a recent timestamp.

5. **Verify images directory exists and has files:**

   ```bash
   ls -lh /var/www/html/images/ | tail -10
   ```

   Should show recent image files if captures are happening.

6. **Test camera manually:**

   ```bash
   rpicam-still -o /var/www/html/images/test-manual.jpg --timeout 1 --nopreview --immediate
   ls -lh /var/www/html/images/test-manual.jpg
   ```

   If this works, the camera is functional.

7. **Check nginx is running:**

   ```bash
   sudo systemctl status nginx
   ```

8. **Verify web page is accessible:**

   ```bash
   hostname -I
   ```

   Then visit `http://<ip-address>` in a browser.

9. **Check if it's daylight hours:**

   ```bash
   date
   ```

   If it's outside 9 AM - 5 PM, images won't be captured (unless `ENABLE_DAYLIGHT_ONLY = False`).

10. **If script isn't running, start it manually to see errors:**

    ```bash
    sudo python3 ~/repos/rainbow-connection/python/farming/sensor-timelapse-script.py
    ```

    Watch for any error messages.

**Common Issues:**

- **No images:** Check if it's daylight hours, or set `ENABLE_DAYLIGHT_ONLY = False` temporarily
- **Script not running:** Check `/home/tim/rc.local.log` for errors
- **Pico not connected:** Verify USB connection and check `/dev/ttyACM*`
- **Camera not working:** Test manually with `rpicam-still` command
- **Web page not updating:** Clear browser cache or do a hard refresh (Ctrl+F5)

## Plant io setup

Based on the [](https://youtu.be/0wI8gDeB3WM), 

The code is in the [official repo](https://github.com/CoreElectronics/CE-Makerverse-Plant_io)

We will need 

- CE-Makerverse-Plant_io/code/Plant_io.py
