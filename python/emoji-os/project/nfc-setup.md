# PiicoDev RFID/NFC Module setup

- Radio Frequency Identification (RFID) is a technology that allows for the identification of objects by using radio waves.
- Near Field Communication (NFC) is a type of RFID that operates at a range of 10 cm or less.

This will usually be referred to as NFC as we will be using it with NFC tags.

The Raspberry Pi Pico NFC module can be bought from [Core Electronics](https://core-electronics.com.au/piicodev-rfid-module.html).

For the emoji badge project, we will use a [PiicoDev Prototyping Cable (Male) 200mm](https://core-electronics.com.au/piicodev-breakout-cable-200mm.html) to connect directly to the Raspberry Pi Pico pins, rather than the PiicoDev plug connection cables.

It is also possible to solder your own wires to the top of the board.

## PiicoDev RFID (NFC, I2C) wiring

Power the RFID board only from **3.3 V** (I2C and the module are 3.3 V).

| Signal | Connect to (Pico) | Physical pin | Color  |
|--------|-------------------|-------------:|--------|
| VCC    | 3V3 (OUT)         |           36 | Red    |
| GND    | GND               | any GND pin  | Black  |
| SDA    | GP16              |           21 | Blue   |
| SCL    | GP17              |           22 | Yellow |

- **VCC (pin 36):** **3V3 (OUT)** — the Pico's 3.3 V output. Do **not** use pin **37**, which is `3V3_EN` (an enable input, not a power output); wiring VCC there leaves the module unpowered.
- **GND:** Use any Pico **GND** pin (for example **3**, **8**, **13**, **18**, **23**, **28**, or **33**).
- **SDA/SCL:** **I2C0** on **GP16** / **GP17** (physical pins **21** / **22**), same side of the header as each other. See `python/tests/test-rfid.py`. Other GP pairs are valid if you update PiicoDev init accordingly.

## Testing

To test out the NFC module and a pico, first install the PiicoDev library.

Then connect the module and run the code in rainbow-connection\python\tests\test-nfc-with-prototyping-cable.py as the main.py file.
