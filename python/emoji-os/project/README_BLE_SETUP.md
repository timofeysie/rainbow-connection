# BLE Setup for Pico W

## Firmware Requirements

For the Pico W to support BLE, you need the correct MicroPython firmware:

### Download Options

1. **Official MicroPython for Pico W** (Recommended)
   - Download from: https://micropython.org/download/rp2-pico-w/
   - File: `rp2-pico-w-20231019-v1.22.0.uf2` (or newer)

2. **CircuitPython** (Alternative)
   - Download from: https://circuitpython.org/board/raspberry_pi_pico_w/
   - File: `adafruit-circuitpython-raspberry_pi_pico_w-en_US-8.x.uf2`

### Installation

1. **Hold down the BOOTSEL button** on your Pico W
2. **Plug in the USB cable** (keep BOOTSEL pressed)
3. **Release BOOTSEL**
4. Your computer should show a drive named `RPI-RP2`
5. **Copy the `.uf2` file** to the `RPI-RP2` drive
6. The Pico W will automatically restart with the new firmware

### Verify BLE Support

After flashing, test with this command in Thonny:

```python
import bluetooth
print("✓ BLE module available")
```

Or in REPL:

```python
>>> import bluetooth
>>> ble = bluetooth.BLE()
>>> ble.active(True)
True
```

### ble_advertising.py File

You also need the `ble_advertising.py` library file:

```python
# ble_advertising.py
# MicroPython BLE advertising utilities

import struct


def advertising_payload(limited_disc=False, br_edr=False, name=None, services=None, appearance=0):
    payload = bytearray()

    def _append(adv_type, value):
        nonlocal payload
        payload += struct.pack("BB", len(value) + 1, adv_type) + value

    _append(0x01, struct.pack("B", (0x01 if limited_disc else 0x02) + (0x00 if br_edr else 0x04)))

    if name:
        _append(0x09, name)

    if services:
        for uuid in services:
            b = bytes(uuid)
            if len(b) == 2:
                _append(0x03, b)
            elif len(b) == 4:
                _append(0x05, b)
            elif len(b) == 16:
                _append(0x07, b)

    if appearance:
        _append(0x19, struct.pack("<h", appearance))

    return payload


def decode_field(payload, adv_type):
    i = 0
    result = []
    while i + 1 < len(payload):
        if payload[i + 1] == adv_type:
            result.append(payload[i + 2:i + payload[i] + 1])
        i += 1 + payload[i]
    return result


def decode_name(payload):
    n = decode_field(payload, 0x09)
    return str(n[0], "utf-8") if n else ""


def irq_handler(adv_type, mac_addr, rssi, adv_data):
    name = decode_name(adv_data)
    print(f"BLE device: {name}, MAC: {mac_addr}, RSSI: {rssi}dBm")
```

Save this as `ble_advertising.py` on your Pico W (in the root directory or in a folder).

### Testing

After flashing the correct firmware and adding `ble_advertising.py`, try running:

```python
import bluetooth
from ble_advertising import advertising_payload

print("✓ BLE setup complete!")
```

If you see any errors, check:

1. Firmware is for **Pico W** (not regular Pico)
2. `ble_advertising.py` file is uploaded to the device
3. Board selection in Thonny is set to "Raspberry Pi Pico W"

## Troubleshooting

### "no module named 'bluetooth'"

- **Cause**: Wrong firmware or regular Pico (not Pico W)
- **Fix**: Flash Pico W-specific firmware

### "no module named 'ble_advertising'"

- **Cause**: Missing library file
- **Fix**: Upload `ble_advertising.py` to the device

### Connection Issues

- Make sure you're using the correct BLE service UUIDs
- Check that both devices are in pairing mode
- Verify the Pico W is advertising with the correct name
