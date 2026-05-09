# Farming — On-Device Debugging

## Watering Pico data not appearing in the web page

Work through these steps in order after deploying the latest
`sensor-timelapse-script.py` and restarting the process on the Pi.

---

### Step 1 — Confirm port assignment at startup

```bash
sudo grep "Serial ports" /var/log/sensor-timelapse.log
```

Expected output:

```
Serial ports: auto-detected=['/dev/ttyACM0', '/dev/ttyACM1'], greenhouse='/dev/ttyACM0', watering='/dev/ttyACM1'
```

**If both values are `None`** — neither Pico was detected. Check USB cables and
run `ls /dev/ttyACM*` to confirm the devices exist.

**If `watering` is `None` but `greenhouse` has a value** — only one Pico is
visible. The second one may not be powered or may be on a different port.

**If the assignment looks swapped** — proceed to Step 5 to pin the ports
permanently.

---

### Step 2 — Check what the watering branch is actually receiving

```bash
sudo grep "Watering" /var/log/sensor-timelapse.log
```

Interpret the output:

| Log line | Meaning |
|---|---|
| `Watering: soil 32.0% pump 12.3s` | Working correctly — ports and format are fine. |
| `Watering raw (no parse): 'Moisture  32.00%    Pump Time  12.34s'` | Port is correct but the regex does not match — copy the exact line and share it to fix the parser. |
| `Watering raw (no parse): 'Moisture: 16% (raw: 123) \| ...'` | **Ports are swapped** — the greenhouse Pico is on the watering port. Go to Step 5. |
| Nothing at all | Watering port is `None`, or the Pico has not printed since the script started. Go to Step 3. |

---

### Step 3 — Confirm the watering Pico is actually printing

The watering script (`automatic_watering.py`) only prints **once per 20-minute
cycle**. Listen directly on the port to catch its output:

```bash
# Replace /dev/ttyACM1 with whatever port Step 1 showed for watering
python3 -c "
import serial, time
s = serial.Serial('/dev/ttyACM1', 115200, timeout=2)
for _ in range(30):
    line = s.readline()
    if line:
        print(repr(line))
    time.sleep(1)
"
```

If nothing prints for more than 20 minutes the Pico may be in sleep mode
(battery-powered path via `plant.sleep()`). Connect it over USB-only power and
watch for the startup banner `Automatic Watering Script v...`.

---

### Step 4 — If the port is correct but the line does not parse

Copy the exact `repr(...)` string from the log line and compare it to the
expected format:

```
Moisture  32.00%    Pump Time  12.34s
```

The regex used in `parse_watering_line` is:

```python
r"Moisture\s+([\d.]+)%\s+Pump\s+Time\s+([\d.]+)s"
```

Common causes of a mismatch:

- Extra whitespace or a different number of spaces between fields
- A negative moisture value (sensor not seated correctly)
- Non-ASCII whitespace (copy the repr carefully — Python will show `\xa0` etc.)

Share the exact repr and the regex can be updated to match.

---

### Step 5 — Pin the ports permanently (fixes swapped / unstable assignment)

USB enumeration order can change after a reboot. Set environment variables
**before** the timelapse script starts. Edit `/etc/rc.local` (or the relevant
`systemd` unit) and add these lines before the `python3` call:

```bash
export PICO_GREENHOUSE_PORT=/dev/ttyACM0
export PICO_WATERING_PORT=/dev/ttyACM1
```

Swap the numbers if Step 1 showed them in the wrong order, then restart.

To confirm which physical Pico is on which port, run:

```bash
python3 -c "
import serial.tools.list_ports
for p in serial.tools.list_ports.comports():
    print(p.device, '|', p.description, '|', p.manufacturer)
"
```

Each Pico shows a description such as `Board CDC` or `Raspberry Pi Pico`.
Plug/unplug one at a time to identify which is which.

---

### General log monitoring commands

```bash
# Live log tail (all events)
sudo tail -f /var/log/sensor-timelapse.log

# Show only sensor update lines
sudo grep "Updated:" /var/log/sensor-timelapse.log | tail -20

# Show only watering-related lines
sudo grep -i "watering" /var/log/sensor-timelapse.log | tail -20

# Show only errors
sudo grep "ERROR\|error" /var/log/sensor-timelapse.log | tail -20

# Check current sensor-data.json
cat /var/www/html/sensor-data.json
```
