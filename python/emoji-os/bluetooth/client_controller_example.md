# BLE Client-Controller Working Setup

This document details the working BLE communication setup between a Raspberry Pi Pico 2 W (client/peripheral) and a Raspberry Pi Zero 2 W or Raspberry Pi 5 (controller/central).

## Overview

The setup uses **Nordic UART Service (NUS)** for BLE communication:
- **Client** (`client_enhanced.py`): Runs on Pico 2 W, acts as BLE peripheral, receives commands
- **Controller** (`controller-1.py`): Runs on Raspberry Pi Zero 2 W/5, acts as BLE central, sends commands

## Key Components

### Nordic UART Service UUIDs

```python
UART_SERVICE_UUID = "6E400001-B5A3-F393-E0A9-E50E24DCCA9E"
UART_RX_CHAR_UUID = "6E400002-B5A3-F393-E0A9-E50E24DCCA9E"  # Write (controller → client)
UART_TX_CHAR_UUID = "6E400003-B5A3-F393-E0A9-E50E24DCCA9E"  # Notify (client → controller)
```

### Device Configuration

- **Device Name**: `Pico-Client` (advertised by the Pico)
- **MAC Address**: Automatically detected and logged (e.g., `2C:CF:67:05:A4:F4`)

## Client: `client_enhanced.py` (v1.2.0)

### Features

1. **BLE Stack Reset**: Forces BLE reset to clear cached device names
2. **MAC Address Logging**: Displays the Pico's BLE MAC address on startup
3. **Emoji Command Support**: Handles commands in format `MENU:POS:NEG`
4. **Legacy Commands**: Supports `ON`, `OFF`, `STATUS`, `BLINK`

### Key Implementation Details

#### BLE Initialization

```python
# Force BLE stack reset to clear cached name
self._ble.active(False)
time.sleep(0.1)
self._ble.active(True)
time.sleep(0.1)
```

This reset is **critical** - without it, the Pico may advertise with a cached name like "MPY BTSTACK" instead of "Pico-Client".

#### MAC Address Retrieval

The MAC address is retrieved from `ble.config('mac')`, which returns a tuple:
```python
mac_data = self._ble.config('mac')  # Returns: (addr_type, mac_bytes)
mac_bytes = mac_data[1]  # Extract the bytes object
```

The MAC is formatted and displayed as `XX:XX:XX:XX:XX:XX`.

#### Command Handling

Commands are received via the `_IRQ_GATTS_WRITE` event and processed in `handle_command()`:

- **Emoji Commands**: Format `"MENU:POS:NEG"` (e.g., `"0:1:0"` for menu 0, positive 1)
- **Legacy Commands**: Simple text strings (`"ON"`, `"OFF"`, `"STATUS"`, `"BLINK"`)

### Usage

1. Upload `client_enhanced.py` and `ble_advertising.py` to the Pico
2. Run the script (via Thonny or `main.py`)
3. The Pico will:
   - Display its MAC address
   - Start advertising as "Pico-Client"
   - Wait for connections
   - Process incoming commands

### Expected Output

```
BLE Client enhanced for Raspberry Pi Pico 2 W v1.2.0 - Enhanced for Emoji Commands
Device Name: Pico-Client
======================================================================
BLE MAC Address: 2C:CF:67:05:A4:F4
Starting advertising...
BLE Client started
BLE MAC Address: 2C:CF:67:05:A4:F4
Waiting for connections...
Supports emoji commands in format: 'MENU:POS:NEG'
Legacy commands: ON, OFF, STATUS, BLINK
Press Ctrl+C to stop
```

## Controller: `controller-1.py` (v1.2)

### Features

1. **Multiple Discovery Methods**:
   - Service UUID scan (most reliable)
   - Device name matching
   - Service verification by connection
2. **Known MAC Address Support**: Can connect directly using MAC address
3. **Interactive Mode**: Manual command entry
4. **Automatic Command Sequence**: Sends test commands on connection

### Key Implementation Details

#### Device Discovery

The controller tries multiple methods to find the Pico:

1. **Service UUID Scan**: Scans for devices advertising the Nordic UART Service
2. **Name Matching**: Looks for devices named "Pico-Client"
3. **Service Verification**: Connects to candidate devices and verifies they have the UART service

#### Direct Connection by MAC

If you know the Pico's MAC address, you can connect directly:

```bash
python controller-1.py 2C:CF:67:05:A4:F4
```

This skips scanning and connects immediately.

#### Service Discovery Compatibility

The code handles different versions of the `bleak` library:

```python
try:
    services = test_client.services  # Newer bleak versions
    if not services:
        services = await test_client.get_services()
except AttributeError:
    services = await test_client.get_services()  # Older versions
```

### Usage

1. Install dependencies: `pip install bleak`
2. Run the controller: `python controller-1.py`
3. Or connect directly: `python controller-1.py <MAC_ADDRESS>`

### Command Sending

```python
# Convert command to bytes
command_bytes = command.encode('utf-8')

# Write to the RX characteristic
await self.client.write_gatt_char(UART_RX_CHAR_UUID, command_bytes)
```

## Command Formats

### Legacy Commands

Simple text strings sent as-is:

- `"ON"` - Turn LED on
- `"OFF"` - Turn LED off
- `"STATUS"` - Get LED status
- `"BLINK"` - Blink LED 3 times

### Emoji Commands

Format: `"MENU:POS:NEG"`

- **MENU**: Menu index (0=Emojis, 1=Animations, 2=Characters, 3=Other)
- **POS**: Positive selection index (1-4)
- **NEG**: Negative selection index (1-4)

Examples:
- `"0:1:0"` - Menu 0 (Emojis), Positive 1 (Regular), Negative 0 (none)
- `"0:0:2"` - Menu 0 (Emojis), Positive 0 (none), Negative 2 (Sad)
- `"1:1:0"` - Menu 1 (Animations), Positive 1 (Fireworks)

## Known Working MAC Addresses

The controller maintains a list of known Pico MAC addresses for faster connection:

```python
known_pico_addresses = [
    "28:CD:C1:05:AB:A4",  # From previous successful connections
    "28:CD:C1:07:2C:E8",  # From previous successful connections
    "2C:CF:67:05:A4:F4"   # Current working address (verified)
]
```

**Note**: The automatic scanning/verification may fail with `'BleakClient' object has no attribute 'g'` error, but **direct connection by MAC address works reliably**:

```bash
python controller-1.py 2C:CF:67:05:A4:F4
```

This method bypasses the service verification step and connects directly.

## Troubleshooting

### Pico Not Found

1. **Check Pico is running**: Verify `client_enhanced.py` is running and shows "Starting advertising..."
2. **Check MAC address**: Note the MAC address displayed by the client
3. **Connect directly**: Use `python controller-1.py <MAC_ADDRESS>`
4. **Power cycle**: Unplug and replug the Pico to reset BLE stack
5. **Distance**: Keep devices within 1-2 meters

### Connection Fails

1. **Use direct MAC connection**: The most reliable method is to connect directly using the MAC address:
   ```bash
   python controller-1.py 2C:CF:67:05:A4:F4
   ```
2. **Service verification error**: If you see `'BleakClient' object has no attribute 'g'`, this is a known issue with the automatic verification. Use direct MAC connection instead.
3. **Check bleak version**: Update with `pip install --upgrade bleak` (though direct MAC connection works regardless)

### Device Name Issues

If the Pico advertises as "MPY BTSTACK" or "(No Name)" instead of "Pico-Client":

1. **Power cycle the Pico**: This resets the BLE stack
2. **Check BLE reset code**: Ensure the `active(False)` / `active(True)` reset is present
3. **Use MAC address**: Connect directly using the MAC address instead of name

## File Dependencies

### Client (`client_enhanced.py`)

- `bluetooth` (MicroPython built-in)
- `ble_advertising.py` (must be uploaded to Pico)
- `machine.Pin` (MicroPython built-in)

### Controller (`controller-1.py`)

- `bleak` (Python package: `pip install bleak`)
- `asyncio` (Python standard library)

## Success Indicators

### Client (Pico)

- Shows MAC address on startup
- Displays "Starting advertising..."
- Shows "✓ Connected: <handle>" when controller connects
- Processes and responds to commands

### Controller (Raspberry Pi)

- Finds device in scan (by name or MAC)
- Successfully connects: "✓ Successfully connected!"
- Verifies service: "✓ Verified Nordic UART Service is available"
- Sends commands: "✓ Sent command: '<command>'"

## Example Session

**On Pico:**
```
BLE Client enhanced for Raspberry Pi Pico 2 W v1.2.0
Device Name: Pico-Client
======================================================================
BLE MAC Address: 2C:CF:67:05:A4:F4
Starting advertising...
BLE Client started
Waiting for connections...
✓ Connected: 64
✓ Received command: 'ON'
Command: Turning ON
✓ Received command: '0:1:0'
Emoji Command - Menu: 0, Pos: 1, Neg: 0
Processing emoji selection:
  Menu: 0 (Emojis)
  Position: 1
  Negative: 0
  Selected positive emoji: Regular
```

**On Raspberry Pi:**
```
BLE Controller v1.2 for Raspberry Pi Zero 2 W
==================================================
Scanning for Pico device (preferred name: 'Pico-Client')...
Found 12 BLE devices:
--------------------------------------------------
 1. (No Name)            | 2C:CF:67:05:A4:F4
    *** FOUND TARGET DEVICE! ***
--------------------------------------------------
✓ Found Pico-Client at address: 2C:CF:67:05:A4:F4
Connecting to 2C:CF:67:05:A4:F4...
✓ Successfully connected!
✓ Verified Nordic UART Service is available
✓ Sent command: 'ON'
✓ Sent command: '0:1:0'
```

## Notes

- The BLE stack reset in the client is **essential** for proper device name advertising
- MAC addresses can change if the Pico's BLE stack is reset, but typically remain stable
- **Direct MAC address connection is the most reliable method** - it bypasses scanning and service verification issues
- The automatic service verification may fail with bleak version issues, but direct connection works regardless
- Once connected via MAC address, command sending works perfectly (as demonstrated by the successful ON/OFF/STATUS/BLINK commands)

