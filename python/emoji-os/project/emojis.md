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

If you keep the current hardware exactly as it is (Pico + DFR0446 only), **you can at best implement Option 1** by tapping the battery node and doing a voltage‑based estimate. To get a reliable, user‑friendly battery remaining value suitable for UI, **Option 2 with a fuel gauge is recommended**.

