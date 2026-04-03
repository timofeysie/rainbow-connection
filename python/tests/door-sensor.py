"""Bench test: NO reed between GP2 and GND. Pull-up: closed=LOW, open=HIGH.
Run on Raspberry Pi Pico (MicroPython). Copy to the device as main.py or run from REPL.
"""

from machine import Pin  # type: ignore[import-untyped]
import time

PIN = 2
DEBOUNCE_MS = 50
pin = Pin(PIN, Pin.IN, Pin.PULL_UP)
last_value = None
last_change_ms = 0

def describe(value):
    if value == 0:
        return "LOW  - reed closed (magnet near)"
    return "HIGH - reed open (no magnet / door open)"

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
