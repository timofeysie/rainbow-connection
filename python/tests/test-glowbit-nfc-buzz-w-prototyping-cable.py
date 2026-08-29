# Glowbit 8x8 + PiicoDev RFID + PiicoDev Buzzer test.
#
# Hardware:
#   - Raspberry Pi Pico 2 W
#   - GlowBit 8x8 matrix (SPI, default pins)
#   - PiicoDev RFID Module (NFC 13.56 MHz, I2C0)
#     connected via PiicoDev Prototyping Cable (Male):
#       SDA → GP16 (physical pin 21)
#       SCL → GP17 (physical pin 22)
#   - PiicoDev Buzzer Module
#     connected via PiicoDev connector on the RFID module
#     (same I2C0 bus, daisy-chained)
#
# Behaviour when a tag is scanned:
#   "5B:6F:B8:08"  (R12 - Monkey)  → blue circle  + rising jingle (~1 s)
#   "DB:93:B7:08"  (W3  - Clown)   → red cross    + rising jingle (~1 s)
#   unknown card                    → question mark + short beep (600 Hz, 100 ms)
#   no tag present                  → question mark (idle/waiting state)
#
# play_jingle() — rising C5-E5-G5-C6 xylophone arpeggio (game-show "ding dong dang dong").
#
# CARD_DISPLAY_S — how long a matched card's graphic stays on screen.
CARD_DISPLAY_S = 5

import glowbit
import time
matrix = glowbit.matrix8x8()

from machine import Pin

from PiicoDev_RFID import PiicoDev_RFID
from PiicoDev_Buzzer import PiicoDev_Buzzer
from PiicoDev_Unified import sleep_ms

# I2C0: SDA = GP16 (physical pin 21), SCL = GP17 (physical pin 22).
# Over the 200 mm prototyping cable the module sometimes NAKs the first
# reset() right after power-up (EIO). Let it settle, then retry a few times.
sleep_ms(200)

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

# Buzzer is daisy-chained on the same I2C0 bus via the RFID module's
# PiicoDev connector.
buzz = PiicoDev_Buzzer(bus=0, sda=Pin(16), scl=Pin(17), freq=100_000, volume=2)

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


def play_jingle():
    """Rising xylophone arpeggio: C5 → E5 → G5 → C6.

    Mimics the bright staccato "ding dong dang dong" game-show correct-answer
    sound. Each note is started as a continuous tone and then explicitly stopped
    so the timing is driven by MicroPython rather than the buzzer's hardware
    timer. The 40 ms gap of silence between notes keeps the hits crisply
    staccato; the final C6 is held a little longer for a satisfying finish.
    """
    notes = [523, 659, 784, 1047]   # C5, E5, G5, C6
    durs  = [130, 130, 130, 320]    # ms per note
    gap   = 40                      # ms of silence between notes
    for freq, dur in zip(notes, durs):
        buzz.tone(freq)
        sleep_ms(dur)
        buzz.noTone()
        sleep_ms(gap)


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
            play_jingle()
            time.sleep(CARD_DISPLAY_S)
            draw_question_mark()
        elif id == "DB:93:B7:08":
            print("W3 - Clown")
            draw_red_cross()
            play_jingle()
            time.sleep(CARD_DISPLAY_S)
            draw_question_mark()
        else:
            print(id)
            buzz.tone(600, 100)
            sleep_ms(100)
    sleep_ms(100)
