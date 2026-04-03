# Pico 2 W + door sensor → Home Assistant — implementation plan

This document outlines how to run MicroPython on a **Raspberry Pi Pico 2 W**, read a **normally open (NO) reed** door sensor with a **falling-edge interrupt**, and drive **Home Assistant** automations.

## Goals

- Detect **door open** reliably (product: ~10 mm range; stronger magnet increases usable gap).
- Use **`IRQ_FALLING`** so “open” is a **high → low** transition on the chosen GPIO (see wiring).
- Connect the Pico to the same LAN as Home Assistant and **publish state or events** so automations can run on open (and optionally on close).

## 1. Electrical: reed switch and “falling edge = open”

A NO reed is **open** with no magnet and **shorted** when the magnet is aligned.

Typical wiring for **falling edge on open**:

- Use the Pico **internal pull-down** (or an external pull-down resistor) so the pin idles **low** when the reed is open.
- Connect the reed between **3.3 V** and the GPIO so that when the door is **closed** (magnet near), the reed **shorts** and the pin reads **high**; when the door **opens**, the reed opens and the pin returns **low**.
- Then **door open** = **falling edge** (`HIGH → LOW`). Wire length and the 100 mA max rating are fine for a logic input; series resistor (e.g. 1 kΩ) optional for extra protection.

Alternative (pull-up to 3.3 V, reed to GND): closed = **low**, open = **high** → door open is a **rising** edge. If you use that wiring, either swap to `IRQ_RISING` or invert in software; the product note asked for falling edge, so prefer the pull-down + reed-to-3V3 layout above.

**Ground reference:** common GND between Pico and the sensor wires.

## 2. MicroPython on Pico 2 W

- Flash **MicroPython** built for **Pico 2** (RP2350) with WiFi support; confirm the official release matches **Pico 2 W** before deploying.
- Pin configuration: `Pin.IN`, `pull=Pin.PULL_DOWN` (for the falling-edge-on-open wiring above).
- Interrupt: `pin.irq(handler=on_fall, trigger=Pin.IRQ_FALLING)`.
- **Debounce:** reeds can chatter; in the ISR or a scheduled task, **ignore repeats** within **20–50 ms** (tune after testing). Avoid heavy work inside the ISR: set a flag or schedule `micropython.schedule` / a small queue.

## 3. What to send to Home Assistant

Pick one primary transport (MQTT is the usual default).

### Option A — MQTT (recommended)

- Run an **MQTT broker** Mosquitto is common) reachable by both the Pico and Home Assistant (often on the HA host or another always-on machine).
- In Home Assistant: **Settings → Devices & services → Add integration → MQTT** (if not already).
- Pico: connect over **WiFi**, publish to a topic such as `home/door/front/state` with payload `ON`/`OFF` or JSON, and optionally **LWT** (Last Will) so HA sees `unavailable` if the Pico drops off the network.
- Map the topic to a **binary sensor** (MQTT) or **device trigger** automation; automations trigger on **state** or **payload**.

### Option B — REST / webhooks

- Pico **HTTP POST**s to Home Assistant **Webhook** or **REST API** with a **long-lived access token** stored in `secrets` on the device. Simpler broker-wise but you must handle **TLS**, **token rotation**, and **connectivity** yourself; MQTT is usually easier for ongoing state.

### Option C — ESPHome / other bridges

- Not required if the Pico runs custom MicroPython; listed only if you later prefer a different device. The Pico path here is **custom firmware + MQTT or REST**.

## 4. Script structure (logical modules)

1. **`boot.py` / `main.py` entry** — load config, connect WiFi, connect MQTT (or HTTP client), register IRQ.
2. **Config** — WiFi SSID/password, broker host/port, TLS if used, topic names, GPIO pin number; keep secrets out of git (e.g. `secrets.py` on device only).
3. **GPIO layer** — setup pin, `IRQ_FALLING`, debounce, optional timer for “still open after N s”.
4. **Network layer** — WiFi reconnect with backoff; MQTT `connect` + `ping`/keepalive loop in main thread.
5. **HA integration layer** — on debounced “open”: publish MQTT state or fire webhook; on “close” if needed for automations.
6. **Main loop** — process debounced events, run MQTT `wait_msg()` or periodic `check_msg()`, feed watchdog if used.

## 5. Home Assistant side

- **Binary sensor (MQTT)** with `device_class: door` (or `opening`) if the payload matches HA conventions.
- **Automation** — trigger: state changes to “open” (or `on`); optional conditions (time, people home, etc.).
- **Dashboard** — optional Lovelace card for door state and history.

## 6. Testing checklist

- Bench-test: magnet in/out, confirm **one** falling edge per open with a print or LED toggle.
- WiFi: reconnect after router reboot.
- MQTT: subscribe with `mosquitto_sub` to verify payloads before relying on HA.
- HA: trigger automation on open; confirm no duplicate fires after debounce tuning.

## 7. Future improvements

- **TLS** to the MQTT broker.
- **OTA** or USB deploy workflow for updates.
- **Battery / deep sleep** — less relevant for USB-powered Pico; note RP2350 low-power options only if you later change power model.

## 8. Bench test script (sensor on GP2 + GND)

Wire the reed **between GP2 and GND** (one wire each). Enable the **internal pull-up** on GP2 so that:

- **Reed closed** (magnet aligned) → pin shorted to GND → reads **LOW** (`0`).
- **Reed open** (no magnet / door open) → pin pulled high → reads **HIGH** (`1`).

This matches the “GPIO + GND” layout; for production you may prefer the pull-down + 3V3 wiring in §1 if you need a **falling** edge for “open.”

Copy the block below to the Pico as `main.py` (or run from the REPL), connect over USB serial, and move the magnet: you should see lines only when the debounced state changes.

```python
"""Bench test: NO reed between GP2 and GND. Pull-up: closed=LOW, open=HIGH."""

from machine import Pin
import time

PIN = 2
DEBOUNCE_MS = 50

pin = Pin(PIN, Pin.IN, Pin.PULL_UP)

last_value = None
last_change_ms = 0


def describe(value):
    if value == 0:
        return "LOW  — reed closed (magnet near)"
    return "HIGH — reed open (no magnet / door open)"


print("Door sensor test on GP2 + GND. Ctrl+C to stop.")

while True:
    v = pin.value()
    now = time.ticks_ms()
    if v != last_value:
        if last_value is None or time.ticks_diff(now, last_change_ms) >= DEBOUNCE_MS:
            last_value = v
            last_change_ms = now
            print(describe(v))
    time.sleep_ms(10)
```

**What to expect:** bringing the magnet close should print the LOW line; removing it should print the HIGH line. If nothing changes, check continuity, that you are on **GP2** (not a 3V3 or RUN pin), and a common **GND**.

This plan is enough to implement `main.py` + small helpers on the Pico and configure MQTT + one automation in Home Assistant without locking you into a single HA version.
