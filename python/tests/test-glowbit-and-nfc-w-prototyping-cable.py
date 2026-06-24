# The Glowbit demo is for the Glowbit 8x8 matrix display.
# The test method is for the PiicoDev RFID (NFC, I2C) using a
# PiicoDev Prototyping Cable (Male) to connect to a Raspberry Pi Pico.

import glowbit
import time
matrix = glowbit.matrix8x8()

from machine import Pin

from PiicoDev_RFID import PiicoDev_RFID
from PiicoDev_Unified import sleep_ms

# NFC setup
# I2C0: SDA = GP16 (physical pin 21), SCL = GP17 (physical pin 22).
# All four args are required: the unified driver only uses sda/scl when
# freq is also supplied, otherwise it falls back to the default I2C0 pins.
#
# Over the 200mm prototyping cable the module sometimes NAKs the first
# reset() right after power-up (EIO). Let it settle, then retry the init a
# few times before giving up.
sleep_ms(200)   # let the module power up before the first I2C write
rfid = None
for attempt in range(5):
    try:
        rfid = PiicoDev_RFID(bus=0, sda=Pin(16), scl=Pin(17), freq=100_000)
        break
    except OSError as err:
        print('RFID init attempt {} failed ({}); retrying...'.format(attempt + 1, err))
        sleep_ms(200)
if rfid is None:
    raise SystemExit('RFID init failed after retries - check wiring/pull-ups')

print('Place tag near the PiicoDev RFID Module')
print(rfid)

while True:
    # matrix
    matrix.drawCircle(3, 3, 3, matrix.blue())
    matrix.pixelsShow()
    print("Circle drawn")
    time.sleep(1)
    matrix.pixelsFill(matrix.black())
    matrix.pixelsShow()
    print("Circle cleared")
    time.sleep(1)
    matrix.drawCircle(3, 3, 3, matrix.red())
    matrix.pixelsShow()
    print("Circle drawn")
    time.sleep(1)
    matrix.pixelsFill(matrix.black())
    matrix.pixelsShow()
    print("Circle cleared")
    time.sleep(1)
    
    # NFC
    if rfid.tagPresent():    # if an RFID tag is present
        id = rfid.readID()   # get the id
        if (id == "5B:6F:B8:08"):
            print("R12 - Monkey")
        elif (id == "DB:93:B7:08"):
            print("W3 - Clown")
        elif (id == "CB:61:B8:08"):
            print("9")
        else:
            print(id)
    sleep_ms(100)

