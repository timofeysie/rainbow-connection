# Farming Project

Three devices work together:

- **Raspberry Pi** — runs `sensor-timelapse-script.py`, serves the website, takes photos
- **Sensor Pico** — runs `sensor-platform.py` (BME280, ENS160, soil moisture, light)
- **Watering Pico** — runs `automatic_watering.py` (soil moisture, pump control)

The Pi reads both Picos over USB serial and writes `/var/www/html/sensor-data.json` for the web UI.

## SSH in

```bash
ping raspberrypi
ssh tim@raspberrypi
```

## Check the main script

```bash
ps aux | grep sensor-timelapse           # confirm script is running
tail -f /var/log/sensor-timelapse.log    # live log output
sudo systemctl status nginx              # confirm web server is up
```

## Debug: sensor data is stale on the website

```bash
# Check which USB serial ports the Pi can see
ls /dev/ttyACM*

# Check what the script assigned to each Pico
grep -i "serial ports" /var/log/sensor-timelapse.log | tail -5
grep -i "connected" /var/log/sensor-timelapse.log | tail -10

# Watch live serial output from the sensor Pico — press Ctrl+C to stop
stty -F /dev/ttyACM0 115200 raw && cat /dev/ttyACM0

# Check what is currently in the JSON file served to the web UI
cat /var/www/html/sensor-data.json

# Check when the JSON file was last written
ls -la /var/www/html/sensor-data.json
```

`stty` sets the baud rate and `cat` just prints everything the Pico sends. If nothing appears after a few seconds swap to `/dev/ttyACM1`.

## Debug: watering Pico not reporting / not watering

```bash
# Confirm the watering Pico is visible
ls /dev/ttyACM*

# Watch live serial output from the watering Pico — press Ctrl+C to stop
stty -F /dev/ttyACM1 115200 raw && cat /dev/ttyACM1

# Look for recent watering parse entries in the log
grep -i "watering" /var/log/sensor-timelapse.log | tail -20
grep -i "no parse\|did not parse\|raw" /var/log/sensor-timelapse.log | tail -20
```

## Restart the script

```bash
sudo pkill -f sensor-timelapse-script.py
sleep 2
nohup python3 /home/tim/python/sensor-timelapse-script.py \
  > /var/log/sensor-timelapse-stdout.log 2>&1 &
```

Or if running as a systemd service:

```bash
sudo systemctl restart sensor-timelapse
sudo journalctl -u sensor-timelapse -f
```

## Override Pico port assignment

If the Pi assigns the wrong port to each Pico, set environment variables before running:

```bash
export PICO_GREENHOUSE_PORT=/dev/ttyACM0
export PICO_WATERING_PORT=/dev/ttyACM1
python3 /home/tim/python/sensor-timelapse-script.py
```

## Images / camera

```bash
rpicam-still -o /var/www/html/images/test.jpg --timeout 1 --nopreview  # test shot
ls -lth /var/www/html/images/ | head -10                                # latest images
rm /var/www/html/images/*.jpg                                            # clear images
```

## Copy images to PC (run on Windows)

```powershell
scp tim@raspberrypi:/var/www/html/images/*.jpg C:\Users\timof\OneDrive\Pictures\farming\
```

## Logs

| File | Contents |
|---|---|
| `/var/log/sensor-timelapse.log` | Main script log (sensor updates, captures, errors) |
| `/var/log/sensor-timelapse-stdout.log` | stdout if run with `nohup` |
| `/var/www/html/sensor-data.json` | Live data served to the web UI |
