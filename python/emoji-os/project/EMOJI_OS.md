# Emoji OS

## States for the learning sport

1. ready to sign up for game (blinking cursor)
2. joined game (check)
3. game ready (countdown?)
4. reading question (dots)
5. game on! (spinning wheel)
6. correct answer (green circle)
7. incorrect answer (red X)
8. second attempt correct (white circle)
9. game over result from server

These should all have small animations that can be interrupted if needed.

### Ready to sign up for game

This would be when the Pico is broadcasting on wifi.  The network connection is tested and the current data and time are called for.

This actually blocks the thread while it is happening, hence we need something like a blinking cursor to signal that something is happening.

When I pair with the Pico it starts its loop of counting how long it is connected for.  This is where whoever is using the app on the phone can start to prepare the game by collecting the details from each broadcasting Pico and send them the message that the game is about to start.

How does a user register their name as connected to the medallion device they will use?

One solution would be for them to have an NFC card with their username on it so this can be used to broadcast their availability.

## LiPo power

The current hardware consists of a Raspberry Pi Pico with a DFR0446 Evaluation Board, Charger Module, MP2636.

### Reading remaining battery capacity

The DFR0446 / MP2636 board is a charger and boost converter only. It **does not expose a built‑in fuel gauge**, so you cannot directly read “battery percentage remaining” from the module itself.

There are two realistic options if you want Emoji OS to show some notion of remaining battery:

- **Option 1 – Voltage-based estimate (no extra hardware)**
  - Sense the raw LiPo voltage (the battery side of the DFR0446, not the 5 V output) with a Pico ADC pin.
  - Use a resistor divider so that the maximum battery voltage (about 4.2 V) is scaled safely below 3.3 V for the ADC.
  - Convert the measured voltage into an approximate state of charge using a lookup table or a simple curve fit for a 1‑cell LiPo (for example, treat ~4.2 V as “full” and ~3.3 V as “empty”, with a non‑linear mapping in between).
  - Show a coarse emoji (e.g. empty / half / full battery) rather than a precise percentage, because LiPo voltage vs capacity is not linear and depends on load, temperature and cell health.

- **Option 2 – Add an external fuel gauge (extra hardware, better accuracy)**
  - Add a dedicated fuel‑gauge IC/module (for example, a MAX17043/MAX17048‑based board or DFRobot’s fuel‑gauge breakout) on the I²C bus.
  - The gauge continuously tracks charge and discharge and exposes a true state‑of‑charge register that can be read from MicroPython.
  - Emoji OS can then display a more accurate battery level emoji (for example, quarter/half/three‑quarter/full or even a numeric percentage).

### Wiring plan using the BAT+ pad

The DFR0446 board exposes the raw battery positive node on a labelled `BAT+` pad (next to the LiPo connector) and battery negative on `BAT-` (ground). To let the Pico “see” battery voltage you need a **simple three‑wire tap**:

- **Wire 1 – Battery sense from `BAT+`**
  - Solder a thin wire to the `BAT+` pad on the DFR0446.
  - This wire goes to the **top of a resistor divider** on your breadboard or perfboard (for example, 100kΩ resistor).

- **Wire 2 – Divider to ground**
  - From the bottom of that 100kΩ resistor, connect to a second resistor down to ground (for example, 220kΩ to GND).
  - Ground can be taken from `BAT-` or any ground pin that is common between the DFR0446 and the Pico (they are already tied together via the USB cable).

- **Wire 3 – Pico ADC input**
  - Also from the **junction between the two resistors**, run a wire to a free Pico ADC‑capable pin (for example, GP26 / `ADC0`).
  - With 100kΩ (to `BAT+`) and 220kΩ (to GND), a full LiPo at 4.2 V is divided down to about 2.9 V, which is safe for the Pico’s 3.3 V‑max ADC.

Once this wiring exists, Emoji OS can periodically read that ADC pin, map the measured voltage onto 0–8 “bars”, and display them as a horizontal 8‑pixel battery bar on the LED matrix. There is **no pure software‑only way** to measure the battery with the current USB‑only connection; the Pico never directly sees the LiPo voltage unless you add this extra three‑wire tap.
