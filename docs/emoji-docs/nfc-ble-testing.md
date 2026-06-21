# NFC & Bluetooth (BLE) Testing

BLE stands for Bluetooth Low Energy.  NFC stands for Near Field Communication.

This document describes the setup for testing NFC BLE communication between a Raspberry Pi Zero and a Raspberry Pi Pico.

It will send the id of scanned NFC tags over BLE to the Zero after they are paired.

There are two files associated with this testing:

- `nfc-zero-with-pairing.py` - runs on the Raspberry Pi Zero
- `nfc-pico-with-pairing.py` - runs on the Raspberry Pi Pico

## Pico setup

Like the emoji-os-pico, the nfc-pico-with-pairing.py file requires the piico dev library as well as the ble_advertising.py file loaded onto the Pico.

## Zero setup

To run the nfc-zero-with-pairing.py file, you need to install the bleak library.  Bleak is a library for Bluetooth Low Energy (BLE) communication in Python.

```sh
sudo apt install python3-bleak
```
