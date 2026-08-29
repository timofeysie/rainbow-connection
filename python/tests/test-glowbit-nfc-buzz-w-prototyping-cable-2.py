# Glowbit 8x8 + PiicoDev RFID + PiicoDev Buzzer test (version 2).
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
# Behaviour:
#   idle (? shown)              → looping 80s A-minor pentatonic synth beat
#   "5B:6F:B8:08" (R12 Monkey) → beat pauses, blue circle + rising jingle
#   "DB:93:B7:08" (W3  Clown)  → beat pauses, red cross  + rising jingle
#   unknown card               → quick beep, beat resumes immediately
#   after display timeout      → beat resumes from where it left off
#   
# The beat sequencer is non-blocking: it uses ticks_ms() so the main loop
# keeps polling the RFID at full speed (no long sleeps while the beat runs).
#
# CARD_DISPLAY_S — how long a matched card's graphic stays on screen.
CARD_DISPLAY_S = 5

# ── beat sequencer parameters ───────────────────────────────────────────────
# 16 steps × 120 ms = 1.92 s loop at ~125 BPM (16th notes).
# Each entry: (frequency_Hz, note_on_ms)
#   frequency 0  = rest (buzzer stays silent for the full step)
#   note_on_ms   = how long the buzzer sounds within the step; the remainder
#                  is silence, giving the staccato xylophone/synth feel.
BEAT_STEP_MS = 120

BEAT = [
    (220, 90),   # A3  — downbeat 1
    (440, 55),   # A4  — octave echo (80s bounce)
    (330, 65),   # E4  —
    (  0,  0),   # rest
    (220, 90),   # A3  — downbeat 2
    (  0,  0),   # rest
    (294, 65),   # D4  —
    (392, 65),   # G4  —
    (220, 90),   # A3  — downbeat 3
    (440, 55),   # A4  — octave echo
    (330, 65),   # E4  —
    (262, 65),   # C4  —
    (220, 90),   # A3  — downbeat 4
    (  0,  0),   # rest
    (392, 65),   # G4  —
    (440, 75),   # A4  — high-point to end the bar
]

import glowbit
import time
matrix = glowbit.matrix8x8()

from machine import Pin
from time import ticks_ms, ticks_diff

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


# ── beat sequencer state ─────────────────────────────────────────────────────
_beat_step    = 0
_beat_step_ts = ticks_ms()
_beat_note_on = False
_beat_enabled = True

# Fire the very first note immediately so the beat starts on time.
_f0, _d0 = BEAT[0]
if _f0 > 0:
    buzz.tone(_f0)
    _beat_note_on = True


def _beat_tick():
    """Advance the beat sequencer. Must be called on every main-loop iteration."""
    global _beat_step, _beat_step_ts, _beat_note_on
    if not _beat_enabled:
        return
    now     = ticks_ms()
    elapsed = ticks_diff(now, _beat_step_ts)
    _freq, note_dur = BEAT[_beat_step]

    if _beat_note_on and elapsed >= note_dur:
        buzz.noTone()
        _beat_note_on = False

    if elapsed >= BEAT_STEP_MS:
        _beat_step    = (_beat_step + 1) % len(BEAT)
        _beat_step_ts = now
        freq, note_dur = BEAT[_beat_step]
        if freq > 0:
            buzz.tone(freq)
            _beat_note_on = True


def _pause_beat():
    """Silence the buzzer and suspend sequencer advances."""
    global _beat_enabled, _beat_note_on
    _beat_enabled = False
    if _beat_note_on:
        buzz.noTone()
        _beat_note_on = False


def _resume_beat():
    """Resume the sequencer from the current step position."""
    global _beat_enabled, _beat_step_ts, _beat_note_on
    _beat_enabled = True
    _beat_step_ts = ticks_ms()
    freq, note_dur = BEAT[_beat_step]
    if freq > 0:
        buzz.tone(freq)
        _beat_note_on = True


# ── display helpers ──────────────────────────────────────────────────────────

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

    Each note is started as a continuous tone then explicitly stopped so
    timing is driven by MicroPython rather than the buzzer hardware timer.
    The 40 ms gap of silence between notes keeps the hits crisply staccato.
    """
    notes = [523, 659, 784, 1047]   # C5, E5, G5, C6
    durs  = [130, 130, 130, 320]    # ms per note
    gap   = 40                      # ms of silence between notes
    for freq, dur in zip(notes, durs):
        buzz.tone(freq)
        sleep_ms(dur)
        buzz.noTone()
        sleep_ms(gap)


# ── main ──────────────────────────────────────────────────────────────────────

draw_question_mark()

while True:
    _beat_tick()

    if rfid.tagPresent():
        id = rfid.readID()
        if id == "5B:6F:B8:08":
            print("R12 - Monkey")
            _pause_beat()
            matrix.pixelsFill(matrix.black())
            matrix.drawCircle(3, 3, 3, matrix.blue())
            matrix.pixelsShow()
            play_jingle()
            time.sleep(CARD_DISPLAY_S)
            draw_question_mark()
            _resume_beat()
        elif id == "DB:93:B7:08":
            print("W3 - Clown")
            _pause_beat()
            draw_red_cross()
            play_jingle()
            time.sleep(CARD_DISPLAY_S)
            draw_question_mark()
            _resume_beat()
        else:
            print(id)
            _pause_beat()
            buzz.tone(600)
            sleep_ms(100)
            buzz.noTone()
            _resume_beat()

    sleep_ms(5)
