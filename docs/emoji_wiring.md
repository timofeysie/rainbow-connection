# Emoji OS — Pico wiring

This note matches a **Raspberry Pi Pico** (40-pin) with **GlowBit 8×8** on **VBUS**, **PiicoDev RFID (I2C)** on **3V3**, and the GPIO choices used by `python/emoji-os/emoji-os-pico-0.2.4.py`.

## GPIO numbers vs physical pin numbers

MicroPython uses **GPIO (GP) numbers** in `Pin(n)` and in libraries (for example GlowBit’s default `pin=18` means **GP18**, not “header pin 18”).

On the Pico 40-pin header:

- **Physical pin 18** is **GND** — do not connect GlowBit `Din` there.
- **GP18** (data to the GlowBit chain) is **physical pin 24**.

When a vendor or tutorial says “pin 18” for NeoPixel/GlowBit-style data on a Pico, they almost always mean **GPIO 18 → physical pin 24**.

## GlowBit 8×8 matrix

| Signal | Connect to (Pico) | Physical pin |
|--------|-------------------|-------------:|
| VCC    | VBUS              |           40 |
| GND    | AGND (pin 38)     |           38 |
| Din    | GP18              |           24 |

- **VCC (pin 40):** 5 V from VBUS; suitable LED supply current compared with Pico **3V3**.
- **GND (pin 38):** Pico pin 38 is **ADC_GND**; it is the same ground net as the digital **GND** pins (e.g. 3, 8, 13, 18, 23, 28, 33) for normal builds.
- **Din (GP18 / pin 24):** Matches `glowbit.matrix8x8(..., pin=18)` in code (`pin` is GPIO 18).

## PiicoDev RFID (NFC, I2C)

Power the RFID board only from **3.3 V** (I2C and the module are 3.3 V).

| Signal | Connect to (Pico) | Physical pin |
|--------|-------------------|-------------:|
| VCC    | 3V3 (OUT)         |           36 |
| GND    | GND               | see below    |
| SDA    | GP16              |           21 |
| SCL    | GP17              |           22 |

- **VCC (pin 36):** **3V3 (OUT)** — the Pico's 3.3 V output. Do **not** use pin **37**, which is `3V3_EN` (an enable input, not a power output); wiring VCC there leaves the module unpowered.
- **GND:** Use any Pico **GND** pin (for example **3**, **8**, **13**, **18**, **23**, **28**, or **33**).
- **SDA/SCL:** **I2C0** on **GP16** / **GP17** (physical pins **21** / **22**), same side of the header as each other. See `python/tests/test-rfid.py`. Other GP pairs are valid if you update PiicoDev init accordingly.

## Other GPIO used by `emoji-os-pico-0.2.4.py`

| Function    | GPIO | Physical pin |
|-------------|-----:|-------------:|
| Button 1    | GP22 |           29 |
| Button 2    | GP21 |           27 |
| Button 3    | GP20 |           26 |
| Buzzer      | GP11 |           15 |
| Onboard LED | —    | `Pin("LED")` |

`Pin("LED")` is board-defined (Pico vs Pico W differ). **GP16** / **GP17** are used for RFID I2C in this layout; they must not clash with other peripherals you add.

## Quick reference — pins mentioned in this build

| Physical pin | Pico function | Use                          |
|-------------:|---------------|------------------------------|
|           21 | GP16          | RFID SDA                     |
|           22 | GP17          | RFID SCL                     |
|           15 | GP11          | Buzzer                       |
|           24 | GP18          | GlowBit Din                  |
|           26 | GP20          | Button 3                     |
|           27 | GP21          | Button 2                     |
|           29 | GP22          | Button 1                     |
|           36 | 3V3 (OUT)     | RFID VCC                     |
|           38 | AGND          | GlowBit GND                  |
|           40 | VBUS          | GlowBit VCC                  |

For the official full pinout, see the [Raspberry Pi Pico datasheet](https://datasheets.raspberrypi.com/pico/pico-datasheet.pdf) (pinout diagram).

## Visual quick reference (diagrams.net)

The same quick-reference table is in **`emoji_wiring_quickref.drawio`** (draw.io / [diagrams.net](https://app.diagrams.net/) XML). Open the site, choose **File → Open from → Device**, and select that file. You can resize the shape, change colours, or export **PNG** / **SVG** from **File → Export as**.
