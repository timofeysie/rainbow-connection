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

## The Automatic Watering system

The automatic watering system comes originally from the [Core Electronitcs Plant.io project](https://core-electronics.com.au/guides/plant-io/plant-io-basic-setup-guide-automatically-water-a-seedling-based-on-soil-moisture/).

It has been modified to work with our sensor platform and timelapse camera system.  It makes sense to only need one rasbperry pi pico, so in the future this may be rolled into the sensor platform as well.

## Direct serial listener — reading a Pico from the Pi terminal

When the timelapse script is not logging watering data, you can read the
watering Pico's serial output directly from the Pi terminal to see exactly
what it is printing (or whether it is printing anything at all).

Open an SSH session on the Pi and run:

```bash
python3 -c "
import serial, time
PORT = '/dev/ttyACM1'   # change to the watering port shown in the log
s = serial.Serial(PORT, 115200, timeout=2)
print('Listening on', PORT, '- press Ctrl+C to stop')
while True:
    line = s.readline()
    if line:
        print(repr(line))
"
```

The `repr()` wrapper shows the **exact bytes** received, including spaces,
newlines, and any unexpected characters — this is the format needed to verify
or fix the parser regex.

**What you should see from the watering Pico:**

```
b'Automatic Watering Script v1.1.0 starting...\r\n'
b'Moisture  32.00%    Pump Time   0.00s\r\n'
```

The number portion uses Python `:5.2f` formatting (right-padded to 5
characters), so there will be leading spaces before small numbers.

**What to do with the output:**

- If you see those lines — the port assignment is correct and the parser should
  work. Copy a data line and compare it to the expected format above.
- If you see greenhouse sensor lines (`Moisture: X% (raw: Y) | ...`) — the
  ports are swapped; swap the `PICO_GREENHOUSE_PORT` and `PICO_WATERING_PORT`
  environment variables in `rc.local`.
- If nothing appears for more than 20 minutes — the Pico may be in deep sleep
  (`plant.sleep()`) which cuts USB power internally. Reset the Pico by
  unplugging and replugging it, or comment out `plant.sleep()` for USB-only
  use.

**Finding which physical device is on which port:**

```bash
python3 -c "
import serial.tools.list_ports
for p in serial.tools.list_ports.comports():
    print(p.device, '|', p.description, '|', p.manufacturer)
"
```

Unplug one Pico at a time — the line that disappears tells you which device
path belongs to that Pico.

---

## Credits and Licensing

The scripts for the automatic watering system are in the following files:

- Plant_io.py
- python\farming\automatic_watering.py

This is the firmware repo for the [Core Electronics Makerverse Plant_io Project](https://core-electronics.com.au/guides/plant-io/).

These files are open source and **Core Electronics software is released under [Creative Commons Share-alike 4.0 International](http://creativecommons.org/licenses/by-sa/4.0/).
