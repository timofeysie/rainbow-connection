# RFID smoke test — wiring aligned with Emoji OS Pico layout:
# I2C0: SDA = GP16 (physical pin 21), SCL = GP17 (physical pin 22).
# Requires PiicoDev_RFID and PiicoDev_Unified on the Pico filesystem.
from machine import Pin

from PiicoDev_RFID import PiicoDev_RFID
from PiicoDev_Unified import sleep_ms

rfid = PiicoDev_RFID(bus=0, sda=Pin(16), scl=Pin(17), freq=400_000)

print("Place tag near the PiicoDev RFID Module")
print(rfid)

while True:
    if rfid.tagPresent():
        tag_id = rfid.readID()
        if tag_id == "5B:6F:B8:08":
            print("R12")
        elif tag_id == "DB:93:B7:08":
            print("W3 - Clown")
        elif tag_id == "CB:61:B8:08":
            print("9")
        else:
            print(tag_id)
    sleep_ms(100)
