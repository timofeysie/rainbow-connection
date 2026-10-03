# Glowbit 8x8 + PiicoDev RFID + PiicoDev Buzzer test (version 2).
#
# Hardware:
#   - Raspberry Pi Pico 2 W
#   - GlowBit 8x8 matrix (SPI, default pins)
#   - PiicoDev RFID Module (NFC 13.56 MHz, I2C0)
#     connected via PiicoDev Prototyping Cable (Male):
#       SDA â†’ GP16 (physical pin 21)
#       SCL â†’ GP17 (physical pin 22)
#   - PiicoDev Buzzer Module
#     connected via PiicoDev connector on the RFID module
#     (same I2C0 bus, daisy-chained)
#
# Behaviour:
#   idle (? shown)              â†’ 80s A-minor pentatonic synth beat, played
#                                 BEAT_REPEATS times, then silence
#   "5B:6F:B8:08" (R12 Monkey) â†’ beat pauses, blue circle + rising jingle
#   "DB:93:B7:08" (W3  Clown)  â†’ beat pauses, red cross  + rising jingle
#   unknown card               â†’ quick beep, beat replays from the start
#   after display timeout      â†’ beat replays from the start
#   
# The beat sequencer is non-blocking: it uses ticks_ms() so the main loop
# keeps polling the RFID at full speed (no long sleeps while the beat runs).
#
# CARD_DISPLAY_S â€” how long a matched card's graphic stays on screen.
CARD_DISPLAY_S = 5

# â”€â”€ beat sequencer parameters â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€
# 16 steps Ã— 120 ms = 1.92 s loop at ~125 BPM (16th notes).
# Each entry: (frequency_Hz, note_on_ms)
#   frequency 0  = rest (buzzer stays silent for the full step)
#   note_on_ms   = how long the buzzer sounds within the step; the remainder
#                  is silence, giving the staccato xylophone/synth feel.
BEAT_STEP_MS = 120
# Number of times the 16-step pattern plays before the beat stops for good.
BEAT_REPEATS = 2

BEAT = [
    (220, 90),   # A3  â€” downbeat 1
    (440, 55),   # A4  â€” octave echo (80s bounce)
    (330, 65),   # E4  â€”
    (  0,  0),   # rest
    (220, 90),   # A3  â€” downbeat 2
    (  0,  0),   # rest
    (294, 65),   # D4  â€”
    (392, 65),   # G4  â€”
    (220, 90),   # A3  â€” downbeat 3
    (440, 55),   # A4  â€” octave echo
    (330, 65),   # E4  â€”
    (262, 65),   # C4  â€”
    (220, 90),   # A3  â€” downbeat 4
    (  0,  0),   # rest
    (392, 65),   # G4  â€”
    (440, 75),   # A4  â€” high-point to end the bar
]

import glowbit
import time
matrix = glowbit.matrix8x8()

from machine import Pin
from time import ticks_ms, ticks_diff

from PiicoDev_Unified import sleep_ms
import PiicoDev_Unified as _uni
import PiicoDev_RFID as _rfid_mod
import PiicoDev_Buzzer as _buzz_mod
from PiicoDev_RFID import PiicoDev_RFID
from PiicoDev_Buzzer import PiicoDev_Buzzer

# I2C0: SDA = GP16 (physical pin 21), SCL = GP17 (physical pin 22).
# Over the 200 mm prototyping cable the RFID module sometimes NAKs the
# first reset() right after power-up (EIO). Let it settle, then retry.
#
# Do not construct a second machine.I2C() on GP16/GP17: that re-inits I2C0
# (duplicate "create machine.I2C()" / OLED-freq warnings) and often yields
# EIO at 0x5C on Pico 2 W. Share one PiicoDev I2C wrapper instead.
# Factory buzzer address is 0x5C with all ID switches OFF; any switch ON
# moves it to 0x09â€“0x17, and setI2Caddr() can persist a custom addr.
_I2C_BUS = 0
_I2C_SDA = Pin(16)
_I2C_SCL = Pin(17)
_I2C_FREQ = 100_000
_RFID_DEFAULT = 0x2C
_BUZZ_DEFAULT = 0x5C

_shared_i2c = None
_orig_create_i2c = _uni.create_unified_i2c

def _create_shared_i2c(bus=None, freq=None, sda=None, scl=None, suppress_warnings=True):
    global _shared_i2c
    if _shared_i2c is None:
        _shared_i2c = _orig_create_i2c(
            bus=_I2C_BUS, freq=_I2C_FREQ, sda=_I2C_SDA, scl=_I2C_SCL
        )
    return _shared_i2c

_uni.create_unified_i2c = _create_shared_i2c
_rfid_mod.create_unified_i2c = _create_shared_i2c
_buzz_mod.create_unified_i2c = _create_shared_i2c

sleep_ms(200)

rfid = None
for attempt in range(5):
    try:
        rfid = PiicoDev_RFID(bus=_I2C_BUS, sda=_I2C_SDA, scl=_I2C_SCL, freq=_I2C_FREQ)
        break
    except OSError as err:
        print('RFID init attempt {} failed ({}); retrying...'.format(attempt + 1, err))
        sleep_ms(200)
if rfid is None:
    raise SystemExit('RFID init failed after retries - check wiring/pull-ups')

# Buzzer is daisy-chained on the same I2C0 bus via the RFID module's
# PiicoDev connector.
_rfid_addr = getattr(rfid, 'address', _RFID_DEFAULT)
buzz = None
_last_buzz_err = None
sleep_ms(50)
for attempt in range(5):
    found = list(rfid.i2c.i2c.scan())
    print('I2C scan: {}'.format([hex(a) for a in found]))
    candidates = []
    if _BUZZ_DEFAULT in found:
        candidates.append(_BUZZ_DEFAULT)
    for addr in found:
        if addr != _rfid_addr and addr not in candidates:
            candidates.append(addr)
    if not candidates:
        print(
            'No buzzer on the bus (RFID is {}). Check the daisy-chain '
            'PiicoDev cable, 3V3/GND, and that ID switches are all OFF '
            '(addr 0x5C).'.format(hex(_rfid_addr))
        )
        _last_buzz_err = OSError('buzzer missing from I2C scan')
        sleep_ms(200)
        continue
    for addr in candidates:
        try:
            buzz = PiicoDev_Buzzer(
                bus=_I2C_BUS, sda=_I2C_SDA, scl=_I2C_SCL, freq=_I2C_FREQ,
                addr=addr, volume=2,
            )
            print('PiicoDev Buzzer ready at {}'.format(hex(addr)))
            break
        except OSError as err:
            print('Buzzer init at {} failed ({}); retrying...'.format(hex(addr), err))
            _last_buzz_err = err
    if buzz is not None:
        break
    sleep_ms(200)
if buzz is None:
    raise SystemExit(
        'Buzzer init failed after retries - check wiring/ID switches ({})'.format(
            _last_buzz_err
        )
    )

print('Place tag near the PiicoDev RFID Module')
print(rfid)


# â”€â”€ beat sequencer state â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€
_beat_step    = 0
_beat_step_ts = ticks_ms()
_beat_note_on = False
_beat_enabled = True
_beat_loops   = 0

# Fire the very first note immediately so the beat starts on time.
_f0, _d0 = BEAT[0]
if _f0 > 0:
    buzz.tone(_f0)
    _beat_note_on = True


def _beat_tick():
    """Advance the beat sequencer. Must be called on every main-loop iteration."""
    global _beat_step, _beat_step_ts, _beat_note_on, _beat_enabled, _beat_loops
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
        if _beat_step == 0:
            _beat_loops += 1
            if _beat_loops >= BEAT_REPEATS:
                if _beat_note_on:
                    buzz.noTone()
                    _beat_note_on = False
                _beat_enabled = False
                return
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


def _restart_beat():
    """Replay the beat from the first step for another BEAT_REPEATS passes."""
    global _beat_enabled, _beat_step, _beat_step_ts, _beat_note_on, _beat_loops
    _beat_step    = 0
    _beat_loops   = 0
    _beat_enabled = True
    _beat_step_ts = ticks_ms()
    freq, note_dur = BEAT[_beat_step]
    if freq > 0:
        buzz.tone(freq)
        _beat_note_on = True


# â”€â”€ display helpers â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€

def draw_red_cross():
    """Draw a red 'âœ•' (diagonal cross) on the 8Ã—8 matrix.

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
    """Draw a '?' glyph on the 8Ã—8 matrix in white.

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
    """Rising xylophone arpeggio: C5 â†’ E5 â†’ G5 â†’ C6.

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


# â”€â”€ main â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€

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
            _restart_beat()
        elif id == "DB:93:B7:08":
            print("W3 - Clown")
            _pause_beat()
            draw_red_cross()
            play_jingle()
            time.sleep(CARD_DISPLAY_S)
            draw_question_mark()
            _restart_beat()
        else:
            print(id)
            _pause_beat()
            buzz.tone(600)
            sleep_ms(100)
            buzz.noTone()
            _restart_beat()

    sleep_ms(5)
