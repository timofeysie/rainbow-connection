# The Glowbit demo is for the Glowbit 8x8 matrix display.
# The test method is for the PiicoDev RFID (NFC, I2C) using a
# PiicoDev Prototyping Cable (Male) to connect to a Raspberry Pi Pico.
#
# The glowbit display reacts to the card shown:
#   "5B:6F:B8:08"  (R12 - Monkey)  → blue circle for 5 s, then question mark
#   "DB:93:B7:08"  (W3  - Clown)   → red cross  for 5 s, then question mark
#   unknown card                    → question mark (unchanged)
#   no tag present                  → question mark (idle/waiting state)
#
# CARD_DISPLAY_S — how long a matched card's circle stays on screen.
CARD_DISPLAY_S = 5

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


def draw_red_cross():
    """Draw a red '✕' (diagonal cross) on the 8×8 matrix.

    Pixel layout (0 = off, 1 = on):
      # . . . . . . #
      . # . . . . # .
      . . # . . # . .
      . . . # # . . .
      . . . # # . . .
      . . # . . # . .
      . # . . . . # .
      # . . . . . . #
    """
    matrix.pixelsFill(matrix.black())
    X = [
        [1, 0, 0, 0, 0, 0, 0, 1],
        [0, 1, 0, 0, 0, 0, 1, 0],
        [0, 0, 1, 0, 0, 1, 0, 0],
        [0, 0, 0, 1, 1, 0, 0, 0],
        [0, 0, 0, 1, 1, 0, 0, 0],
        [0, 0, 1, 0, 0, 1, 0, 0],
        [0, 1, 0, 0, 0, 0, 1, 0],
        [1, 0, 0, 0, 0, 0, 0, 1],
    ]
    for row, r in enumerate(X):
        for col, c in enumerate(r):
            if c:
                matrix.pixelSetXY(col, row, matrix.red())
    matrix.pixelsShow()


def draw_question_mark():
    """Draw a '?' glyph on the 8×8 matrix in white.

    Pixel layout (0 = off, 1 = on):
      . . # # # . . .
      . # . . . # . .
      . . . . . # . .
      . . . . # . . .
      . . . # . . . .
      . . . . . . . .
      . . . # . . . .
      . . . . . . . .
    """
    matrix.pixelsFill(matrix.black())
    Q = [
        [0, 0, 1, 1, 1, 0, 0, 0],
        [0, 1, 0, 0, 0, 1, 0, 0],
        [0, 0, 0, 0, 0, 1, 0, 0],
        [0, 0, 0, 0, 1, 0, 0, 0],
        [0, 0, 0, 1, 0, 0, 0, 0],
        [0, 0, 0, 0, 0, 0, 0, 0],
        [0, 0, 0, 1, 0, 0, 0, 0],
        [0, 0, 0, 0, 0, 0, 0, 0],
    ]
    for row, r in enumerate(Q):
        for col, c in enumerate(r):
            if c:
                matrix.pixelSetXY(col, row, matrix.white())
    matrix.pixelsShow()


# Start in the idle/waiting state.
draw_question_mark()

while True:
    if rfid.tagPresent():
        id = rfid.readID()
        if id == "5B:6F:B8:08":
            print("R12 - Monkey")
            matrix.pixelsFill(matrix.black())
            matrix.drawCircle(3, 3, 3, matrix.blue())
            matrix.pixelsShow()
            time.sleep(CARD_DISPLAY_S)
            draw_question_mark()
        elif id == "DB:93:B7:08":
            print("W3 - Clown")
            draw_red_cross()
            time.sleep(CARD_DISPLAY_S)
            draw_question_mark()
        else:
            # Unknown card — question mark is already showing; just log the ID.
            print(id)
    sleep_ms(100)
