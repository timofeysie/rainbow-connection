# Ambient Light Sensor

We want to use a PiicoDev Ambient Light Sensor VEML6030 with a Raspberry Pi Pico to calculate the amount of hours of direct sunlight per day a spot in a garden gets

## Measuring Direct Sunlight Hours Using a PiicoDev VEML6030 (Raspberry Pi Pico)

This guide shows how to use a **PiicoDev Ambient Light Sensor (VEML6030)** with a **Raspberry Pi Pico** to estimate how many **hours of direct sunlight per day** a specific spot in your garden receives. This is ideal for deciding whether a location is suitable for sun-loving plants like zucchini.

Lux is the SI unit of illuminance (light intensity). It stands for lumen per square meter.

The basic idea is:

1. Measure **ambient light (lux)** at regular intervals
2. Decide a **lux threshold** that represents *direct sunlight*
3. Count how long readings stay above that threshold
4. Convert that accumulated time into **sun-hours per day**

## What the VEML6030 Measures

The VEML6030 measures **illuminance in lux** (how bright light appears to the human eye).

Typical outdoor values:

| Lighting condition        | Approx. lux |
|---------------------------|-------------|
| Full direct sunlight      | 60,000–100,000 |
| Bright shade / thin cloud | 10,000–30,000 |
| Overcast sky              | 1,000–5,000 |

Note the sensor does **not** know the direction of light. It cannot distinguish direct sun from reflections, so thresholds are used.

## Choosing a Direct Sunlight Threshold

For garden planning, this rule works well:

```text
DIRECT_SUN_LUX = 40,000
```

## Implementation: `ambient-light-sensor.py`

The `ambient-light-sensor.py` script provides a complete implementation for continuous light monitoring on a Raspberry Pi Pico W. It's designed to run all day in a sealed plastic box with a clear cover placed in a garden spot.

### Features

- **Continuous light monitoring**: Reads lux values every 500ms (2 readings per second)
- **Timestamped logging**: Records all lux readings to CSV file with timestamps
- **Sunlight hour tracking**: Calculates and tracks cumulative direct sunlight hours per day
- **Daily summaries**: Automatically saves daily sunlight hour totals to a text file
- **Error handling**: Gracefully handles sensor errors and file write failures
- **Minimal dependencies**: Uses only the PiicoDev VEML6030 sensor and standard libraries

### Output Files

The script creates two output files:

1. **`lux_readings.csv`**: CSV file containing timestamped lux readings
   - Format: `timestamp,lux`
   - Example: `1234567890.12,42356.78`
   - Appends new readings continuously

2. **`sunlight_hours.txt`**: Text file containing daily sunlight hour summaries
   - Format: `Day X: Y.YY hours`
   - Example: `Day 0: 6.35 hours`
   - Automatically appended when each day completes

### Core Functionality

#### Light Reading (`read_light()`)

- Reads the current lux value from the VEML6030 sensor
- Returns 0 if reading fails (handles sensor errors gracefully)

#### Lux Logging (`write_lux_reading()`)

- Appends timestamp and lux value to `lux_readings.csv`
- Uses append mode to preserve all historical data
- Silently fails if file write is unavailable (e.g., no SD card)

#### Sunlight Tracking (`update_sunlight_tracking()`)

- Tracks cumulative time when lux exceeds `DIRECT_SUN_LUX` (40,000 lux)
- Resets daily tracking every 24 hours (based on boot time)
- Returns current day's sunlight hours in decimal format
- Automatically saves previous day's total when day resets

#### Main Loop

- Continuously reads light sensor every 500ms
- Logs each reading with timestamp
- Updates sunlight hour tracking
- Prints current status to console: `Light: XXXX lux | Sun: Y.YYh`

### Usage

1. **Setup**: Connect PiicoDev VEML6030 to Raspberry Pi Pico W via I2C
2. **Deploy**: Place the Pico W in a sealed plastic box with clear cover in the garden
3. **Run**: Upload and execute `ambient-light-sensor.py`
4. **Monitor**: Check console output or retrieve data files
5. **Analyze**: Review CSV data for detailed patterns, or text file for daily summaries

### Configuration

The script uses a single configuration constant:

- **`DIRECT_SUN_LUX = 40000`**: Threshold in lux for counting direct sunlight
  - Any reading at or above this value counts toward sunlight hours
  - Based on typical outdoor direct sunlight conditions (40,000+ lux)

### Day Tracking

The script tracks days based on seconds since boot (86400 seconds = 24 hours). For more accurate day tracking with actual calendar dates, you would need an RTC (Real-Time Clock) module, but for garden monitoring purposes, the simple boot-time-based tracking is sufficient.

### Data Collection

With readings every 500ms, the script generates approximately:

- **172,800 readings per day** (2 per second × 86,400 seconds)
- **CSV file size**: ~3-4 MB per day (depending on timestamp precision)
- **Memory usage**: Minimal - only current tracking state kept in memory

This high-frequency sampling ensures accurate sunlight hour calculations even with brief cloud cover or shadows passing over the sensor.

## Mobile Phone Access via Bluetooth

The script broadcasts sensor data via Bluetooth Low Energy (BLE), allowing mobile phones to connect and read current values on-demand.

### Connecting from a Mobile Device

1. **Install a BLE Scanner App**:
   - **iOS**: LightBlue (free) or nRF Connect
   - **Android**: nRF Connect (free) or BLE Scanner

2. **Discover the Device**:
   - Enable Bluetooth on your phone
   - Open the BLE scanner app and start scanning
   - Look for device name: **"Garden-Light-Sensor"**
   - Connect to the device

3. **Read Data Characteristics**:
   After connecting, navigate to the service with UUID `A5B1C2D3-E4F5-A6B7-C8D9-E0F1A2B3C4D5` and read the three characteristics:
   
   - **Lux Characteristic** (`...000000000001`): Current lux reading (float32, 4 bytes)
   - **Sunlight Hours Characteristic** (`...000000000002`): Today's sunlight hours (float32, 4 bytes)
   - **Statistics Characteristic** (`...000000000003`): JSON string with current_lux, sunlight_hours, readings_today, avg_lux, max_lux

### Data Format

- **Lux Characteristic** (`...000000000001`): UTF-8 text string (decimal number with 2 decimal places)
  - Format: `"16.00"` (example showing 16.00 lux)
  - Readable directly in nRF Connect as text
  - Example values: `"1234.56"`, `"0.00"`, `"89234.12"`
  
- **Sunlight Hours Characteristic** (`...000000000002`): UTF-8 text string (decimal number with 2 decimal places)
  - Format: `"4.23"` (example showing 4.23 hours)
  - Readable directly in nRF Connect as text
  - Example values: `"0.00"`, `"6.35"`, `"8.92"`
  
- **Statistics Characteristic** (`...000000000003`): UTF-8 JSON string
  - Contains all data in one read: current_lux, sunlight_hours, readings_today, avg_lux, max_lux
  - Readable directly in nRF Connect as text/JSON
  - Example: `{"current_lux": 12345.67, "sunlight_hours": 4.23, "readings_today": 172800, "avg_lux": 15234.56, "max_lux": 89345.12}`

### Viewing Data in nRF Connect

All characteristics send UTF-8 text strings, so they're immediately readable:

1. **Tap any characteristic** → **Tap "Read"** → Values appear as human-readable text
2. **For Lux/Hours**: Shows decimal numbers like `"16.00"` or `"4.23"`
3. **For Statistics**: Shows JSON text with all values in one read

### Usage Tips

- Characteristics are read-only - tap "Read" to get current values
- Values update every 500ms in real-time
- Device advertises continuously and can be accessed anytime
- Connection status is shown on the Pico console: `BLE: CONNECTED` / `BLE: DISCONNECTED`
- If you see hex values, change the view format in nRF Connect to see decoded floats/text