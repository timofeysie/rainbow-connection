# Bluetooth Communication Scripts - Product Requirements Document

## Project Overview

This project implements Bluetooth Low Energy (BLE) communication between a Raspberry Pi Zero 2 W (controller) and a Raspberry Pi Pico 2 W (client). The Zero acts as a central device that sends text commands to the Pico, which acts as a peripheral device that receives and processes these commands.

## Architecture

- **Raspberry Pi Zero 2 W**: BLE Central device running Python with `bleak` library
- **Raspberry Pi Pico 2 W**: BLE Peripheral device running MicroPython
- **Protocol**: Nordic UART Service (NUS) over BLE
- **Communication**: Unidirectional (Zero → Pico) with simple text commands

## Hardware Requirements

### Raspberry Pi Zero 2 W (Controller)
- Raspberry Pi Zero 2 W with Bluetooth capability
- MicroSD card with Raspberry Pi OS
- Power supply (5V, 2.5A recommended)
- Optional: Display, keyboard, mouse for setup

### Raspberry Pi Pico 2 W (Client)
- Raspberry Pi Pico 2 W with Bluetooth capability
- MicroUSB cable for programming and power
- Optional: Breadboard and jumper wires for external components

## Software Dependencies

### Raspberry Pi Zero 2 W
- Python 3.7+
- `bleak` library for BLE communication
- Installation: `pip3 install bleak`

### Raspberry Pi Pico 2 W
- MicroPython firmware with BLE support
- `ble_advertising.py` helper module (included in project)

## BLE Protocol Details

### Nordic UART Service (NUS)
- **Service UUID**: `6E400001-B5A3-F393-E0A9-E50E24DCCA9E`
- **RX Characteristic**: `6E400002-B5A3-F393-E0A9-E50E24DCCA9E` (write from central)
- **TX Characteristic**: `6E400003-B5A3-F393-E0A9-E50E24DCCA9E` (notify to central)

### Supported Commands
- `ON`: Turn on LED
- `OFF`: Turn off LED
- `STATUS`: Report current LED status
- `BLINK`: Blink LED 3 times

## Setup Instructions

### Raspberry Pi Pico 2 W Setup

1. **Install MicroPython**:
   - Download MicroPython firmware for Pico 2 W
   - Hold BOOTSEL button while connecting USB
   - Copy firmware `.uf2` file to mounted drive

2. **Install Thonny IDE**:
   - Download and install Thonny
   - Configure interpreter for MicroPython on Pico

3. **Upload Required Files**:
   - Copy `ble_advertising.py` from `python/pico_w/` to Pico
   - Copy `client.py` to Pico
   - Ensure both files are in the root directory

4. **Run the Client**:
   - Open `client.py` in Thonny
   - Run the script
   - Should see "Starting advertising..." message

### Raspberry Pi Zero 2 W Setup

1. **Install Dependencies**:
   ```bash
   sudo apt update
   sudo apt install python3-pip
   pip3 install bleak
   ```

2. **Enable Bluetooth**:
   ```bash
   sudo systemctl enable bluetooth
   sudo systemctl start bluetooth
   ```

3. **Run the Controller**:
   ```bash
   python3 controller.py
   ```

## Usage Instructions

### Basic Operation

1. **Start the Pico Client**:
   - Power on Pico 2 W
   - Run `client.py` in Thonny
   - LED will blink slowly indicating advertising mode

2. **Start the Zero Controller**:
   - Run `python3 controller.py` on Zero
   - Script will scan for "Pico-Client" device
   - Upon connection, LED on Pico will turn on solid

3. **Command Execution**:
   - Controller automatically sends test sequence: ON, OFF, STATUS, BLINK
   - Commands appear in Pico's Thonny console
   - LED provides visual feedback

### Interactive Mode

After the automatic command sequence, the controller offers interactive mode:
- Enter commands manually: `ON`, `OFF`, `STATUS`, `BLINK`
- Type `quit` to exit
- Commands are sent immediately to the Pico

## Expected Output

### Pico Client Console Output
```
BLE Client started
Waiting for connections...
Available commands: ON, OFF, STATUS, BLINK
Starting advertising...
New connection: 1
Received command: 'ON'
Command: Turning ON
Received command: 'OFF'
Command: Turning OFF
Received command: 'STATUS'
Command: STATUS requested
LED is OFF
Received command: 'BLINK'
Command: BLINK
```

### Zero Controller Console Output
```
BLE Controller for Raspberry Pi Zero 2 W
==================================================
Scanning for 'Pico-Client' for 10 seconds...
Found Pico-Client at address: XX:XX:XX:XX:XX:XX
Connecting to XX:XX:XX:XX:XX:XX...
Successfully connected!

Sending command sequence...
Sent command: 'ON'
Sent command: 'OFF'
Sent command: 'STATUS'
Sent command: 'BLINK'

Would you like to enter interactive mode? (y/n):
```

## Troubleshooting

### Common Issues

1. **"Could not find 'Pico-Client'"**:
   - Ensure Pico is running `client.py`
   - Check that BLE is enabled on both devices
   - Try restarting both devices

2. **"Failed to connect"**:
   - Check Bluetooth permissions on Zero
   - Ensure devices are within range (typically 10m)
   - Restart Bluetooth service: `sudo systemctl restart bluetooth`

3. **"Not connected to any device"**:
   - Connection may have dropped
   - Restart both scripts
   - Check for interference from other Bluetooth devices

4. **Commands not received**:
   - Verify Pico is still running and connected
   - Check Thonny console for error messages
   - Ensure `ble_advertising.py` is present on Pico

### Debug Tips

- **Pico LED Behavior**:
  - Slow blink: Advertising (not connected)
  - Solid on: Connected
  - Off: Error or disconnected

- **Enable Verbose Logging**:
  - Add `print()` statements in both scripts
  - Monitor Thonny console for detailed output

- **Test Bluetooth Functionality**:
  - Use `bluetoothctl` on Zero to scan for devices
  - Verify Pico appears in scan results

## File Structure

```
python/bluetooth/
├── client.py                           # Pico 2 W MicroPython script
├── controller.py                       # Zero 2 W Python script
├── product-requirements-document.md    # This documentation
└── ble_advertising.py                  # Required helper (copy from pico_w/)
```

## Future Enhancements

- Bidirectional communication (Pico → Zero)
- Additional command types
- Command queuing and buffering
- Error handling and retry logic
- Configuration file support
- Multiple device support
- Security and authentication

## Technical Notes

- BLE advertising interval: 500ms (configurable)
- Command timeout: 10 seconds for scanning
- Maximum command length: Limited by BLE MTU (typically 20 bytes)
- Power consumption: Optimized for battery operation
- Range: Up to 10 meters in open space

## Support

For issues or questions:
1. Check this documentation first
2. Review console output for error messages
3. Verify all dependencies are installed
4. Test with minimal setup (just LED control)
5. Check hardware connections and power supply
