# Farming Workflow

This system is made up of a Raspberry Pi with a connected camera taking timelapse photos of a plant.
There is a Raspberry Pi Pico connected to the Raspberry Pi via USB that is used to control the watering of the plant.
There is also a Raspberry Pi Pico connected to the Raspberry Pi via USB that is used to read the sensor data.

## The Raspberry Pi workflow

``
rpicam-still -o test.jpg
```

```
rpicam-hello -t 0 --qt-preview
```

Find the Zero's IP address on the local network

hostname -I

http://192.168.68.59:8888/
192.168.68.52 


If the imelapse-script has changed in the repo, it must be copied again after getting the latest:

```
sudo cp ~/repos/rainbow-connection/python/farming/farming-index.html /var/www/html/index.html
```

The sensor-timelapse-script.py script is run from its repo location.

```
sudo nano /etc/rc.local
```

Check if the script is running:

```
ps aux | grep sensor-timelapse-script.py
```

Check the rc.local log:

```
cat /home/tim/rc.local.log
```

Check the script's log file for activity:

```
sudo tail -f /var/log/sensor-timelapse.log
```

and this logfile:
```

Change the time over value:
```
CAPTURE_END_HOUR = 23    # Stop capturing at 5 PM (17:00)
```


## The Sensor Data

```Soil Moisture
-- %
--
Temperature
-- Â°C
--
Humidity
-- %RH
--
Pressure
-- hPa
--
AQI (Air Quality Index)
--
--
TVOC (Total Volatile Organic Compounds)
-- ppb
--
eCO2 (Equivalent CO2)
-- ppm
--
```
