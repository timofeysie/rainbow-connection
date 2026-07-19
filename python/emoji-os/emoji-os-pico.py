# emoji os pico - Startup/connection indicator; white 5s then blue; red on BLE error
VERSION = "0.5.1"

# === Multiplayer Pairing ===
# PAIR_NAME identifies this controller/badge pair. The matching emoji-os-zero.py
# must use the same PAIR_NAME or the badge will refuse its commands. Override by
# creating a small `pair_config.py` next to this file on the Pico containing
# e.g. `PAIR_NAME = "living-room"`. See python/emoji-os/project/multiplayer-mode.md.
try:
    from pair_config import PAIR_NAME  # type: ignore  # noqa: F401
except Exception:
    PAIR_NAME = "default"

import glowbit
from machine import Pin
import time
from emojis import (
    regular,
    happy,
    wry,
    sadWry,
    crossboneEyes,
    heartEyes,
    thickLips,
    sad,
    angry,
    greenMonster,
    chakana,
    scroll_large_image,
    heartBounce,
    finn,
    pikachu,
    crab,
    frog,
    bald,
    surprise,
    draw_question_mark,
    draw_red_cross,
)

# === BLE Imports ===
import bluetooth
from ble_advertising import advertising_payload
from micropython import const

# === BLE Constants ===
_IRQ_CENTRAL_CONNECT = const(1)
_IRQ_CENTRAL_DISCONNECT = const(2)
_IRQ_GATTS_WRITE = const(3)

_FLAG_READ = const(0x0002)
_FLAG_WRITE_NO_RESPONSE = const(0x0004)
_FLAG_WRITE = const(0x0008)
_FLAG_NOTIFY = const(0x0010)

# BLE advertising data type for "Complete Local Name" (used in scan response).
_ADV_TYPE_COMPLETE_NAME = const(0x09)

# Nordic UART Service UUIDs
_UART_UUID = bluetooth.UUID("6E400001-B5A3-F393-E0A9-E50E24DCCA9E")
_UART_TX = (
    bluetooth.UUID("6E400003-B5A3-F393-E0A9-E50E24DCCA9E"),
    _FLAG_READ | _FLAG_NOTIFY,
)
_UART_RX = (
    bluetooth.UUID("6E400002-B5A3-F393-E0A9-E50E24DCCA9E"),
    _FLAG_WRITE | _FLAG_WRITE_NO_RESPONSE,
)
_UART_SERVICE = (
    _UART_UUID,
    (_UART_TX, _UART_RX),
)


def _build_name_scan_response(name):
    """Encode just the Complete Local Name AD structure for use as scan response.

    Putting the name in scan response (rather than the main adv packet) frees
    up enough room in the 31-byte adv packet for the 128-bit UART service UUID,
    while still letting BLE centrals see the name during an active scan.
    """
    name_bytes = name.encode("utf-8") if isinstance(name, str) else bytes(name)
    # 31-byte BLE packet, minus 2 bytes for the AD length+type header.
    if len(name_bytes) > 29:
        print(f"⚠ PAIR_NAME-derived BLE name is too long ({len(name_bytes)} > 29); truncating")
        name_bytes = name_bytes[:29]
    return bytes((len(name_bytes) + 1, _ADV_TYPE_COMPLETE_NAME)) + name_bytes

# === NFC Imports ===
from PiicoDev_RFID import PiicoDev_RFID
from PiicoDev_Unified import sleep_ms

# === Hardware Setup ===
matrix = glowbit.matrix8x8()
matrix.pixelsFill(matrix.black())

# Status indicator colours (pale white, pale blue, light green, pale red for error)
PALE_WHITE = (80, 80, 80)
PALE_BLUE = (60, 60, 140)
LIGHT_GREEN = (100, 220, 100)
PALE_RED = (180, 60, 60)


def draw_center_indicator(rgb_tuple):
    """Draw a 2x2 square in the centre of the matrix with the given (R,G,B) colour."""
    matrix.pixelsFill(matrix.black())
    r, g, b = rgb_tuple
    colour = matrix.rgbColour(r, g, b)
    matrix.drawRectangleFill(3, 3, 4, 4, colour)
    matrix.pixelsShow()


# === NFC Setup ===
# I2C0: SDA = GP16 (physical pin 21), SCL = GP17 (physical pin 22).
# Uses the PiicoDev Prototyping Cable (Male). Over the 200mm cable the module
# sometimes NAKs the first reset right after power-up — let it settle and retry.
# rfid is None when the module is absent or wiring fails; NFC mode is a no-op.
sleep_ms(200)
rfid = None
for _nfc_attempt in range(5):
    try:
        rfid = PiicoDev_RFID(bus=0, sda=Pin(16), scl=Pin(17), freq=100_000)
        print('NFC RFID module ready')
        break
    except OSError as _nfc_err:
        print('RFID init attempt {} failed ({}); retrying...'.format(_nfc_attempt + 1, _nfc_err))
        sleep_ms(200)
if rfid is None:
    print('RFID init failed after retries — NFC mode will be unavailable (check wiring/pull-ups)')

# How long the NFC result (circle / cross) is held on the Pico matrix before
# reverting to the question-mark waiting state.
NFC_PICO_RESULT_DISPLAY_S = 5

# Platform icon / display reference — shared state ids + labels (multiplayer-mode.md).
# Log format: [GAME] pico | <state_id> | <label> | <detail>
_GAME_STATE_LABELS = {
    "mode": "Game mode standby",
    "lobby": "Lobby — not yet joined",
    "lobby_joined": "Lobby — joined, waiting",
    "active": "Game started / active",
    "question_open": "Question open",
    "card_scanned": "Card scanned",
    "correct": "Correct answer",
    "wrong": "Wrong answer",
    "question_closed": "Question closed",
    "game_ended": "Game ended",
    "winner": "Game winner",
    "loser": "Game loser",
}

# BLE GAME:<subcommand> → Platform icon state id (wire name may differ).
_GAME_CMD_TO_STATE = {
    "mode": "mode",
    "lobby": "lobby",
    "lobby_joined": "lobby_joined",
    "active": "active",
    "question_open": "question_open",
    "correct": "correct",
    "wrong": "wrong",
    "question_close": "question_closed",
    "ended": "game_ended",
    "winner": "winner",
    "loser": "loser",
}

# Capital 'G' — matches Zero game_mode_matrix (standby before lobby).
_GAME_MODE_G = [
    [0, 0, 1, 1, 1, 1, 0, 0],
    [0, 1, 0, 0, 0, 0, 1, 0],
    [1, 0, 0, 0, 0, 0, 0, 0],
    [1, 0, 0, 0, 1, 1, 1, 0],
    [1, 0, 0, 0, 0, 0, 1, 0],
    [0, 1, 0, 0, 0, 0, 1, 0],
    [0, 0, 1, 1, 1, 1, 0, 0],
    [0, 0, 0, 0, 0, 0, 0, 0],
]


def _log_game_state(state_id, detail=""):
    """Emit a narrative game-state line (see multiplayer-mode.md logging section)."""
    label = _GAME_STATE_LABELS.get(state_id, state_id)
    if detail:
        print("[GAME] pico | {} | {} | {}".format(state_id, label, detail))
    else:
        print("[GAME] pico | {} | {}".format(state_id, label))


def _show_game_mode():
    """Capital 'G': Zero entered game mode; waiting for lobby / game events."""
    matrix.pixelsFill(matrix.black())
    colour = matrix.white()
    for row, r in enumerate(_GAME_MODE_G):
        for col, c in enumerate(r):
            if c:
                matrix.pixelSetXY(col, row, colour)
    matrix.pixelsShow()


def _show_game_lobby():
    """Solid yellow 4×4 centre: lobby open, not yet joined."""
    matrix.pixelsFill(matrix.black())
    matrix.drawRectangleFill(2, 2, 5, 5, matrix.yellow())
    matrix.pixelsShow()


def _show_game_lobby_joined():
    """White 4×4 outline: joined lobby, waiting for game start."""
    matrix.pixelsFill(matrix.black())
    matrix.drawRectangle(2, 2, 5, 5, matrix.white())
    matrix.pixelsShow()


def _show_game_active():
    """Solid green 4×4 centre square: game is live, waiting for a question."""
    matrix.pixelsFill(matrix.black())
    matrix.drawRectangleFill(2, 2, 5, 5, matrix.green())
    matrix.pixelsShow()


def _show_question_open():
    """Question mark glyph: a question is open — scan ready."""
    draw_question_mark()


def _show_tap_ack():
    """Green 4×4 outline: NFC tap acknowledged (awaiting correct/wrong)."""
    matrix.pixelsFill(matrix.black())
    matrix.drawRectangle(2, 2, 5, 5, matrix.green())
    matrix.pixelsShow()


def _show_correct():
    """Blue filled circle: this pair answered correctly."""
    matrix.pixelsFill(matrix.black())
    colour = matrix.blue()
    cx, cy = 3, 3
    # Disk of radius ~3 on the 8×8 grid.
    for y in range(8):
        for x in range(8):
            dx = x - cx
            dy = y - cy
            if dx * dx + dy * dy <= 10:
                matrix.pixelSetXY(x, y, colour)
    matrix.pixelsShow()


def _show_wrong():
    """Red X: this pair answered incorrectly (or no answer)."""
    draw_red_cross()


def _show_question_close():
    """Small white 2×2 dot: between questions, game still active."""
    matrix.pixelsFill(matrix.black())
    matrix.drawRectangleFill(3, 3, 4, 4, matrix.white())
    matrix.pixelsShow()


def _show_game_ended():
    """Scroll 'DONE' across the matrix then go dark."""
    _m = glowbit.matrix8x8(rateLimitCharactersPerSecond=0.7)
    _m.addTextScroll("DONE")
    while _m.scrollingText:
        _m.updateTextScroll()
        _m.pixelsShow()
    matrix.pixelsFill(matrix.black())
    matrix.pixelsShow()


def _show_winner():
    """Fireworks animation (animations menu — positive 1)."""
    matrix.fireworks()


def _show_loser():
    """Rain animation (animations menu)."""
    matrix.rain()


def _handle_game_command(subcommand: str):
    """Dispatch a GAME:<subcommand> received from the Zero via BLE."""
    global _game_state, _game_nfc_display_until_ms

    state_id = _GAME_CMD_TO_STATE.get(subcommand)
    if state_id is None:
        print("[GAME] pico | unknown | unknown GAME command | {!r}".format(subcommand))
        return

    _game_nfc_display_until_ms = 0
    detail_by_cmd = {
        "mode": "G glyph; BLE GAME:mode",
        "lobby": "yellow 4×4; BLE GAME:lobby",
        "lobby_joined": "white 4×4 outline; BLE GAME:lobby_joined",
        "active": "green 4×4; BLE GAME:active",
        "question_open": "? glyph; NFC on; BLE GAME:question_open",
        "correct": "blue filled circle; BLE GAME:correct",
        "wrong": "red X; BLE GAME:wrong",
        "question_close": "white 2×2 dot; BLE GAME:question_close",
        "ended": "DONE scroll; BLE GAME:ended",
        "winner": "fireworks; BLE GAME:winner",
        "loser": "rain; BLE GAME:loser",
    }
    _log_game_state(state_id, detail_by_cmd.get(subcommand, "BLE GAME:" + subcommand))

    if subcommand == "mode":
        _game_state = "mode"
        _show_game_mode()

    elif subcommand == "lobby":
        _game_state = "lobby"
        _show_game_lobby()

    elif subcommand == "lobby_joined":
        _game_state = "lobby_joined"
        _show_game_lobby_joined()

    elif subcommand == "active":
        _game_state = "active"
        _show_game_active()

    elif subcommand == "question_open":
        _game_state = "question_open"
        _show_question_open()

    elif subcommand == "correct":
        _game_state = "correct"
        _show_correct()

    elif subcommand == "wrong":
        _game_state = "wrong"
        _show_wrong()

    elif subcommand == "question_close":
        _game_state = "question_close"
        _show_question_close()

    elif subcommand == "ended":
        _game_state = "ended"
        _show_game_ended()

    elif subcommand == "winner":
        _game_state = "winner"
        _show_winner()

    elif subcommand == "loser":
        _game_state = "loser"
        _show_loser()



button1 = Pin(22, Pin.IN, Pin.PULL_DOWN)
button2 = Pin(21, Pin.IN, Pin.PULL_DOWN)
button3 = Pin(20, Pin.IN, Pin.PULL_DOWN)
buzzer = Pin(11, Pin.OUT)
led_onboard = Pin("LED", Pin.OUT)

# === State Variables ===
# Display indicator states (centre 2x2): startup (white 5s) -> advertising (blue) -> connected
# (green 5s) -> waiting (blank). Red square = BLE init/connect problem (no new state variable).
# Menu/button states (other than choosing emoji): state in ("none", "start", "choosing");
# prev_state in ("none", "done"); menu 0..3; pos/neg 0..4; prev_menu, prev_pos, prev_neg.
menu = 0
pos = 0
neg = 0
state = "none"  # start end or none
# preserve the previous state for pos/neg flipping
prev_menu = 0
prev_pos = 0
prev_neg = 0
prev_state = "none"  # or done
pause = 0.2

# === NFC State ===
# True while the Zero has selected legacy NFC mode (menu 3, neg 4).
nfc_mode_active = False
# "question" = waiting, "circle" = blue circle shown, "x" = red cross shown
nfc_display_state = "question"
# Monotonic timestamp (time.ticks_ms) at which to revert from circle/x to question mark.
nfc_display_until_ms = 0

# === Game State (driven by GAME:* commands from the Zero) ===
# None             — no game in progress / idle
# "lobby"          — open for joining; not yet joined
# "lobby_joined"   — joined; waiting for start
# "active"         — game started, no open question yet
# "question_open"  — NFC scanning active; TAG: notifies sent on card read
# "correct"        — answered correctly this question
# "wrong"          — answered incorrectly this question
# "question_close" — between questions
# "ended"          — game finished (generic DONE scroll)
# "winner" / "loser" — end-of-game celebration / consolation
_game_state = None
# Monotonic ms timestamp; when elapsed, revert game-mode NFC display to question mark.
_game_nfc_display_until_ms = 0

# === Helper Functions ===
def check_menu():
    global menu
    if menu > 3:
        menu = 0
    if menu < 0:
        menu = 3

def check_pos():
    global pos
    if pos > 4:
        pos = 1

def check_neg():
    global neg
    if neg > 4:
        neg = 1

# drawing the menu could be considered a training mode
def draw_menu():
    global menu
    global pause
    if menu == 0:
        matrix.drawRectangleFill(3,0, 4,1, matrix.white()) # 1 center square
        matrix.pixelsShow()
        time.sleep(pause)
    if menu == 1:
        matrix.drawRectangleFill(3,2, 4,3, matrix.white()) # 1 center square
        matrix.pixelsShow()
        time.sleep(pause)
    if menu == 2:
        matrix.drawRectangleFill(3,4, 4,5, matrix.white()) # 1 center square
        matrix.pixelsShow()
        time.sleep(pause)
    if menu == 3:
        matrix.drawRectangleFill(3,6, 4,7, matrix.white()) # 1 center square
        matrix.pixelsShow()
        time.sleep(pause)

# draw the positive state value.  possibly we will hide these
# pos & neg start at 1.  0 means either one has not been selected
def draw_pos():
    global pos
    if pos == 1:
        matrix.drawRectangleFill(0,0, 1,1, matrix.green()) # 1 center square
        matrix.pixelsShow()
        time.sleep(pause)
    if pos == 2:
        matrix.drawRectangleFill(0,2, 1,3, matrix.green()) # 1 center square
        matrix.pixelsShow()
        time.sleep(pause)
    if pos == 3:
        matrix.drawRectangleFill(0,4, 1,5, matrix.green()) # 1 center square
        matrix.pixelsShow()
        time.sleep(pause)
    if pos == 4:
        matrix.drawRectangleFill(0,6, 1,7, matrix.green()) # 1 center square
        matrix.pixelsShow()
        time.sleep(pause)

def draw_neg():
    global neg
    if neg == 1:
        matrix.drawRectangleFill(5,0, 6,1, matrix.red()) # 1 center square
        matrix.pixelsShow()
        # time.sleep(0.5)
    if neg == 2:
        matrix.drawRectangleFill(5,2, 6,3, matrix.red()) # 1 center square
        matrix.pixelsShow()
        # time.sleep(0.5)
    if neg == 3:
        matrix.drawRectangleFill(5,4, 6,5, matrix.red()) # 1 center square
        matrix.pixelsShow()
        # time.sleep(0.5)
    if neg == 4:
        matrix.drawRectangleFill(5,6, 6,7, matrix.red()) # 1 center square
        matrix.pixelsShow()
        # time.sleep(0.5)

def reset_state():
    global state
    global menu
    global pos
    global neg
    global prev_state
    global prev_menu
    global prev_pos
    global prev_neg
    prev_state = "done"
    prev_menu = menu
    prev_pos = pos
    prev_neg = neg
    state = "none"
    menu = 0
    pos = 0
    neg = 0

def reset_prev():
    global prev_state
    global prev_menu
    global prev_pos
    global prev_neg
    prev_state = "none"
    prev_menu = 0
    prev_pos = 0
    prev_neg = 0
    
def buzz():
    buzzer.value(1)
    time.sleep(0.1)
    buzzer.value(0)

# draw the chosen emoji and reset values
def draw_emoji():
    global state
    global menu
    global pos
    global neg
    print("draw emoji menu at", menu, "pos at", pos, "neg at", neg, "state", state)
    matrix = glowbit.matrix8x8(rateLimitCharactersPerSecond=0.7)
    #==========
    #POSITIVE 0
    # regular
    if (menu == 0 and pos == 1):
        print("menu 0 pos 1 normal")
        regular()
    # happy
    if (menu == 0 and pos == 2):
        print("menu 0 pos 3 wry")
        wry()
    # wry
    if (menu == 0 and pos == 3):
        print("menu 0 pos 2 happy")
        happy()
    # heart eyes
    if (menu == 0 and pos == 4):
        print("menu 0 pos 4 heart eyes")
        heartEyes()
    # NEGATIVE 0
    # thick lips
    if (menu == 0 and neg == 1):
        print("menu 0 neg 1 thick lips")
        thickLips()
     # sad wry
    if (menu == 0 and neg == 2):
        print("menu 0 neg 2 sad wry")
        sadWry()
    # sad
    if (menu == 0 and neg == 3):
        print("menu 0 neg 3 sad")
        sad()
    # crossbone eyes
    if (menu == 0 and neg == 4):
        print("menu 0 neg 4 crossbone eyes")
        crossboneEyes()
    #==========
    #POSITIVE 1
    # fireworks
    if (menu == 1 and pos == 1):
        print("menu 1 pos 1 fireworks " + state)
        matrix = glowbit.matrix8x8(rateLimitCharactersPerSecond=1)
        matrix.fireworks()
    # circularRainbow
    if (menu == 1 and pos == 2):
        print("menu 1 pos 2 circularRainbow")
        matrix = glowbit.matrix8x8(rateLimitCharactersPerSecond=20)
        matrix.circularRainbow()
    # chakana
    if (menu == 1 and pos == 3):
        print("menu 1 pos 3 chakana")
        chakana()
    # heart bounce
    if (menu == 1 and pos == 4):
        print("menu 1 pos 4 heart bounce")
        heartBounce()
    # NEGATIVE 1
    # rain
    if (menu == 1 and neg == 1):
        print("menu 1 neg 1 rain")
        matrix = glowbit.matrix8x8(rateLimitCharactersPerSecond=5)
        matrix.rain()
    # scroll large image (panorama from large_image)
    if (menu == 1 and neg == 2):
        print("menu 1 neg 2 scroll_large_image")
        scroll_large_image()
    # ??
    if (menu == 1 and neg == 3):
        print("menu 1 neg 3")
        # angry()
    # ??
    if (menu == 1 and neg == 4):
        print("menu 1 neg 4 green monster")
        #greenMonster()
    #==========
    #POSITIVE 2
    # finn
    if (menu == 2 and pos == 1):
        print("menu 2 pos 1 finn")
        finn()
    # pikachu
    if (menu == 2 and pos == 2):
        print("menu 2 pos 2 pikachu")
        pikachu()
    # crab
    if (menu == 2 and pos == 3):
        print("menu 2 pos 2 crab")
        crab()
    # frog
    if (menu == 2 and pos == 4):
        print("menu 2 pos 2 frog")
        frog()
    # NEGATIVE 2
    # bald
    if (menu == 2 and neg == 1):
        print("menu 2 neg 1 bald")
        bald()
    # surprise
    if (menu == 2 and neg == 2):
        print("menu 2 neg 2 surprise")
        surprise()
    if (menu == 2 and neg == 3):
        print("menu 2 neg 3 green monster")
        greenMonster()
    if (menu == 2 and neg == 4):
        print("menu 2 neg 4 angry")
        angry()
    #==========
    #POSITIVE 3
    # circle
    if (menu == 3 and pos == 1):
        print("menu 3 pos 1 circle")
        matrix.drawCircle(3, 3, 3, matrix.blue())
        matrix.pixelsShow()
    # yes
    if (menu == 3 and pos == 2):
        print("menu 3 pos 2 Yes")
        matrix.addTextScroll("YES")
        while matrix.scrollingText == True:
            matrix.updateTextScroll()
            matrix.pixelsShow()
    # Somi
    if (menu == 3 and pos == 3):
        print("menu 3 pos 3 Somi")
        matrix.addTextScroll("Somi")
        while matrix.scrollingText == True:
            matrix.updateTextScroll()
            matrix.pixelsShow()
    # NEGATIVE 3
    # X
    if (menu == 3 and neg == 1):
        print("menu 3 neg 1")
        matrix.drawLine(0, 0, 7, 7, matrix.red())
        matrix.drawLine(0, 7, 7, 0, matrix.red())
        matrix.pixelsShow()
    # no
    if (menu == 3 and neg == 2):
        print("menu 3 neg 2")
        matrix.addTextScroll("NO")
        while matrix.scrollingText == True:
            matrix.updateTextScroll()
            matrix.pixelsShow()
    # Tim
    if (menu == 3 and pos == 3):
        print("menu 3 neg 3 Tim")
        matrix.addTextScroll("Tim")
        while matrix.scrollingText == True:
            matrix.updateTextScroll()
            matrix.pixelsShow()
    else:
        # do we need this in scrolling mode?
        reset_state()

# === BLE Classes ===
class BLESimplePeripheral:
    """BLE Peripheral that advertises UART service and receives emoji commands
    Enhanced version with MAC address logging and proper BLE stack reset
    """
    
    def __init__(self, ble, name="Pico-Client"):
        self._ble = ble
        # Force BLE stack reset to clear cached name
        self._ble.active(False)
        time.sleep(0.1)
        self._ble.active(True)
        time.sleep(0.1)
        # Set the GAP device name so it's also reachable via the GAP service after
        # connect (defaults to "MPY BTSTACK" otherwise).
        try:
            self._ble.config(gap_name=name)
        except Exception as e:
            print(f"Could not set gap_name: {e}")
        self._ble.irq(self._irq)
        
        # Get and log the BLE MAC address
        mac_str = "Unknown"
        try:
            mac_data = self._ble.config('mac')
            
            # Handle tuple format: (addr_type, mac_bytes)
            # The MAC address is in the second element as bytes
            if isinstance(mac_data, tuple) and len(mac_data) >= 2:
                # Extract the bytes object from the tuple
                mac_bytes = mac_data[1]
                if isinstance(mac_bytes, bytes) and len(mac_bytes) == 6:
                    # Convert bytes to list of integers
                    mac_ints = [b for b in mac_bytes]
                    # Format MAC address as XX:XX:XX:XX:XX:XX
                    mac_parts = [f'{b:02X}' for b in mac_ints]
                    mac_str = ':'.join(mac_parts)
                    print(f"BLE MAC Address: {mac_str}")
                else:
                    mac_str = "Unknown"
            elif isinstance(mac_data, bytes) and len(mac_data) == 6:
                # Direct bytes object
                mac_ints = [b for b in mac_data]
                mac_parts = [f'{b:02X}' for b in mac_ints]
                mac_str = ':'.join(mac_parts)
                print(f"BLE MAC Address: {mac_str}")
            elif isinstance(mac_data, (tuple, list)) and len(mac_data) == 6:
                # Already a sequence of 6 integers
                mac_ints = [int(x) if not isinstance(x, int) else x for x in mac_data]
                mac_parts = [f'{b:02X}' for b in mac_ints]
                mac_str = ':'.join(mac_parts)
                print(f"BLE MAC Address: {mac_str}")
        except Exception as e:
            print(f"Could not retrieve MAC address (method 1): {e}")
            # Try alternative method
            try:
                # Some MicroPython versions use 'addr' instead of 'mac'
                mac_data = self._ble.config('addr')
                # Handle tuple format: (addr_type, mac_bytes)
                if isinstance(mac_data, tuple) and len(mac_data) >= 2:
                    mac_bytes = mac_data[1]
                    if isinstance(mac_bytes, bytes) and len(mac_bytes) == 6:
                        mac_ints = [b for b in mac_bytes]
                        mac_parts = [f'{b:02X}' for b in mac_ints]
                        mac_str = ':'.join(mac_parts)
                        print(f"BLE MAC Address (via 'addr'): {mac_str}")
                    else:
                        mac_str = "Unknown"
                elif isinstance(mac_data, bytes) and len(mac_data) == 6:
                    mac_ints = [b for b in mac_data]
                    mac_parts = [f'{b:02X}' for b in mac_ints]
                    mac_str = ':'.join(mac_parts)
                    print(f"BLE MAC Address (via 'addr'): {mac_str}")
                else:
                    mac_str = "Unknown"
            except Exception as e2:
                mac_str = "Unknown"
        
        # Register the UART service
        ((self._handle_tx, self._handle_rx),) = self._ble.gatts_register_services((_UART_SERVICE,))
        
        self._connections = set()
        # Per-connection pairing state: conn_handle -> True once PAIR:<PAIR_NAME>
        # has been received. Until then, writes to RX are not forwarded to the
        # command handler so a wrong-pair Zero cannot drive this badge.
        self._authenticated = {}
        self._pair_name = PAIR_NAME
        self._write_callback = None
        self._display_callback = None  # called with "advertising" when we start/restart advertising
        self._just_connected = False
        # Split the advertising data so a long name like "Pico-Client-<PAIR_NAME>"
        # plus the 128-bit UART UUID (which alone is 18 bytes) fits within the
        # BLE 31-byte adv-packet limit. Service UUIDs go in adv data; the local
        # name goes in the scan response. Bleak combines both for `device.name`.
        self._payload = advertising_payload(services=[_UART_UUID])
        self._resp_payload = _build_name_scan_response(name)
        self._mac_address = mac_str
        self._advertise()

    def _irq(self, event, data):
        """Handle BLE events"""
        if event == _IRQ_CENTRAL_CONNECT:
            conn_handle, _, _ = data
            print(f"✓ Connected: {conn_handle}")
            self._connections.add(conn_handle)
            self._authenticated[conn_handle] = False
            self._just_connected = True
        elif event == _IRQ_CENTRAL_DISCONNECT:
            conn_handle, _, _ = data
            print(f"✗ Disconnected: {conn_handle}")
            self._connections.discard(conn_handle)
            self._authenticated.pop(conn_handle, None)
            # Restart advertising after disconnect
            self._advertise()
            if self._display_callback:
                self._display_callback("advertising")
        elif event == _IRQ_GATTS_WRITE:
            conn_handle, value_handle = data
            value = self._ble.gatts_read(value_handle)
            if value_handle != self._handle_rx:
                return
            if not self._authenticated.get(conn_handle, False):
                self._handle_pair_attempt(conn_handle, value)
                return
            if self._write_callback:
                self._write_callback(value)

    def _handle_pair_attempt(self, conn_handle, value):
        """Validate the first write on a new connection against PAIR_NAME.

        Replies on the TX notify characteristic with PAIR_OK or PAIR_FAIL.
        Until PAIR_OK is sent, the command handler is bypassed entirely.
        """
        try:
            text = value.decode('utf-8').strip()
        except Exception:
            text = ""
        expected = "PAIR:" + self._pair_name
        if text == expected:
            self._authenticated[conn_handle] = True
            print(f"✓ Paired conn={conn_handle} PAIR_NAME='{self._pair_name}'")
            try:
                reply = f"PAIR_OK:{VERSION}".encode("utf-8")
                self._ble.gatts_notify(conn_handle, self._handle_tx, reply)
            except Exception as e:
                print(f"✗ Failed to send PAIR_OK: {e}")
        else:
            print(f"✗ Pair attempt failed conn={conn_handle} got={text!r} expected={expected!r}")
            try:
                self._ble.gatts_notify(conn_handle, self._handle_tx, b"PAIR_FAIL")
            except Exception:
                pass

    def send(self, data):
        """Send data to connected central devices"""
        for conn_handle in self._connections:
            self._ble.gatts_notify(conn_handle, self._handle_tx, data)

    def is_connected(self):
        """Check if any central device is connected"""
        return len(self._connections) > 0

    def _advertise(self, interval_us=500000):
        """Start advertising the BLE service"""
        print("Starting advertising...")
        self._ble.gap_advertise(
            interval_us,
            adv_data=self._payload,
            resp_data=self._resp_payload,
        )
        if self._display_callback:
            self._display_callback("advertising")

    def did_just_connect(self):
        """Return True once after a connection, then clear the flag."""
        if self._just_connected:
            self._just_connected = False
            return True
        return False

    def set_display_callback(self, callback):
        """Set callback(state) for display updates: state is 'advertising'."""
        self._display_callback = callback

    def on_write(self, callback):
        """Set callback for when data is written to RX characteristic"""
        self._write_callback = callback

# === BLE Command Handlers ===
def handle_command(command_data):
    """Handle incoming commands from central device"""
    try:
        # Decode the command
        command = command_data.decode('utf-8').strip()
        print(f"✓ Received command: '{command}'")
        
        if ':' in command:
            # Game lifecycle commands: GAME:<subcommand>
            if command.startswith("GAME:"):
                _handle_game_command(command[5:])
                return

            # NFC result from Zero: show circle or cross on the matrix
            if command.startswith("NFC_RESULT:"):
                _handle_nfc_result(command[11:])
                return

            # Emoji command (format: "MENU:POS:NEG")
            try:
                parts = command.split(':')
                if len(parts) == 3:
                    menu_val = int(parts[0])
                    pos_val = int(parts[1])
                    neg_val = int(parts[2])

                    print(f"Emoji Command - Menu: {menu_val}, Pos: {pos_val}, Neg: {neg_val}")
                    handle_emoji_selection(menu_val, pos_val, neg_val)
                    return
            except ValueError:
                print(f"Invalid emoji command format: '{command}'")

        # Process legacy commands
        if command == "ON":
            print("Command: Turning ON")
            led_onboard.on()
        elif command == "OFF":
            print("Command: Turning OFF")
            led_onboard.off()
        elif command == "STATUS":
            print("Command: STATUS requested")
            print(f"LED is {'ON' if led_onboard.value() else 'OFF'}")
        elif command == "BLINK":
            print("Command: BLINK")
            for _ in range(3):
                led_onboard.on()
                time.sleep(0.2)
                led_onboard.off()
                time.sleep(0.2)
        else:
            print(f"Unknown command: '{command}'")
            
    except Exception as e:
        print(f"✗ Error processing command: {e}")


def _handle_nfc_result(result: str):
    """Handle an NFC_RESULT:<circle|x> command sent by the Zero.

    Updates the matrix immediately and sets a timer so the main loop can
    revert to the question-mark waiting state after NFC_PICO_RESULT_DISPLAY_S.
    Called from the BLE IRQ handler — must not block.
    """
    global nfc_display_state, nfc_display_until_ms
    print(f"NFC result from Zero: {result!r}")
    if result == "circle":
        nfc_display_state = "circle"
        nfc_display_until_ms = time.ticks_add(time.ticks_ms(), NFC_PICO_RESULT_DISPLAY_S * 1000)
        matrix.pixelsFill(matrix.black())
        matrix.drawCircle(3, 3, 3, matrix.blue())
        matrix.pixelsShow()
    elif result == "x":
        nfc_display_state = "x"
        nfc_display_until_ms = time.ticks_add(time.ticks_ms(), NFC_PICO_RESULT_DISPLAY_S * 1000)
        draw_red_cross()
    else:
        print(f"Unknown NFC result: {result!r}")


def handle_emoji_selection(menu_val, pos_val, neg_val):
    """Handle emoji selection from the Pi Zero"""
    global menu, pos, neg, state
    global nfc_mode_active, nfc_display_state, nfc_display_until_ms

    print(f"Processing emoji selection:")
    print(f"  Menu: {menu_val} ({get_menu_name(menu_val)})")
    print(f"  Position: {pos_val}")
    print(f"  Negative: {neg_val}")

    # Legacy NFC mode: menu 3, neg 4 only.
    # (pos 4 is the game mode slot on the Zero and is never sent to the Pico.)
    if menu_val == 3 and neg_val == 4:
        nfc_mode_active = True
        nfc_display_state = "question"
        nfc_display_until_ms = 0
        menu = menu_val
        pos = pos_val
        neg = neg_val
        state = "choosing"
        print("NFC mode activated — showing question mark, waiting for card")
        draw_question_mark()
        return

    # Any other selection exits NFC mode
    nfc_mode_active = False
    nfc_display_state = "question"

    # Set the global state variables
    menu = menu_val
    pos = pos_val
    neg = neg_val
    state = "choosing"

    # Visual feedback with LED
    for _ in range(2):
        led_onboard.on()
        time.sleep(0.1)
        led_onboard.off()
        time.sleep(0.1)

    # Display the emoji immediately
    matrix.pixelsFill(matrix.black())
    draw_emoji()


def get_menu_name(menu_val):
    """Get the name of the menu"""
    menu_names = ["Emojis", "Animations", "Characters", "Other"]
    if 0 <= menu_val < len(menu_names):
        return menu_names[menu_val]
    return "Unknown"

# === Startup: pale white 2x2 centre for 5s, then same position turns pale blue (advertising) ===
draw_center_indicator(PALE_WHITE)
time.sleep(5)
draw_center_indicator(PALE_BLUE)

# === Initialize BLE ===
DEVICE_NAME = "Pico-Client-" + PAIR_NAME
try:
    ble = bluetooth.BLE()
    p = BLESimplePeripheral(ble, DEVICE_NAME)

    # Set up command handler and display callback (advertising -> pale blue)
    p.on_write(handle_command)

    def on_advertising(_state=None):
        draw_center_indicator(PALE_BLUE)

    p.set_display_callback(on_advertising)
except Exception as e:
    print(f"BLE init/connect problem: {e}")
    draw_center_indicator(PALE_RED)
    # Re-raise or enter a loop so script doesn't continue with undefined p
    raise

print("Emoji OS Pico " + VERSION + " - Startup/connection indicator; red = BLE error")
print("Device Name: " + DEVICE_NAME)
print("PAIR_NAME: " + PAIR_NAME)
print("Pairing: expects first write 'PAIR:" + PAIR_NAME + "', replies PAIR_OK:<version>/PAIR_FAIL on TX notify")
print("Supports emoji commands in format: 'MENU:POS:NEG' (after PAIR_OK)")
print(
    "Game commands: GAME:mode/lobby/lobby_joined/active/question_open/"
    "correct/wrong/question_close/ended/winner/loser — drives matrix display"
)
print("NFC game mode: GAME:question_open activates TAG:<cardUid> notifies on NFC read")
print("NFC legacy mode: menu=3 neg=4 — sends 'NFC:<card_id>' to Zero via BLE notify")
print("Legacy commands: ON, OFF, STATUS, BLINK (after PAIR_OK)")

# === Main Loop ===
while True:
    # On first connection: light green 5s then blank (waiting for command)
    if p.did_just_connect():
        draw_center_indicator(LIGHT_GREEN)
        time.sleep(5)
        matrix.pixelsFill(matrix.black())
        matrix.pixelsShow()

    # blocks need to be in reverse order to stop the cascade through the conditions
    if button1.value():
        print('debug btn 1 menu ', menu, "pos", pos, "neg", neg, "state", state, "prev_pos", prev_pos, "prev_neg", prev_neg, "prev_state", prev_state)
        if state == "choosing":
            buzz()
            # increment positive choice
            pos = pos + 1
            neg = 0  # reset any negative value
            check_pos()
            print('button 1 pressed, menu ', menu, "pos", pos, "state", state)
            matrix.pixelsFill(matrix.black())
            draw_menu()
            draw_pos()
        if state == "start":
            buzz()
            # increment positive choice
            state = "choosing"
            pos = pos + 1
            check_pos()
            print('button 1 pressed, menu ', menu, "pos", pos, "state", state)
            matrix.pixelsFill(matrix.black())
            draw_menu()
            draw_pos()
        if prev_state == "done":
            if (prev_neg > 0):
                # reverse previous neg choice
                buzz()
                matrix.pixelsFill(matrix.black())
                pos = prev_neg
                neg = 0
                menu = prev_menu
                print('button 1 pressed again, menu ', menu, "pos", pos, "neg", neg, "state", state)
                draw_emoji()
            if (prev_pos > 0):
                # play last pos
                buzz()
                matrix.pixelsFill(matrix.black())
                pos = prev_pos
                neg = 0
                menu = prev_menu
                print('button 3 pressed again, menu ', menu, "pos", pos, "neg", neg, "state", state)
                draw_emoji()
    if button2.value():
        reset_prev()
        print('debug btn 2 menu ', menu, "pos", pos, "neg", neg, "state", state, "prev_pos", prev_pos, "prev_neg", prev_neg, "prev_state", prev_state)
        buzz()
        if state == "start":
            # start or increment main menu
            menu = menu + 1
            check_menu()
            matrix.pixelsFill(matrix.black())
            draw_menu()
            print('button 2 pressed, menu ', menu, "state", state)
        if state == "none":
            buzz()
            # start or increment main menu
            state = "start"
            check_menu()
            matrix.pixelsFill(matrix.black())
            draw_menu()
            print('button 2 pressed, menu ', menu, "state", state)
        if state == "choosing":
            buzz()
            # done choosing, draw emoji
            print("finshed, draw emoji")
            matrix.pixelsFill(matrix.black())
            draw_emoji()
    if button3.value():
        print('debug btn 3 menu ', menu, "pos", pos, "neg", neg, "state", state, "prev_pos", prev_pos, "prev_neg", prev_neg, "prev_state", prev_state)
        buzz()
        if state == "choosing":
            # increment negative choice
            neg = neg + 1
            pos = 0  # reset positive
            check_neg()
            print('button 3 pressed, menu ', menu, "neg", neg, "state", state)
            matrix.pixelsFill(matrix.black())
            draw_menu()
            draw_neg()
        if state == "start":
            buzz()
            # increment negative choice
            state = "choosing"
            neg = neg + 1
            check_neg()
            print('button 3 pressed, menu ', menu, "neg", neg, "state", state)
            matrix.pixelsFill(matrix.black())            
            draw_menu()
            draw_neg()
        if prev_state == "done":
            print("prev_pos", prev_pos)
            if (prev_pos > 0):
                # toggle pos to neg response
                buzz()
                matrix.pixelsFill(matrix.black())
                neg = prev_pos
                pos = 0
                menu = prev_menu
                print('button 3 pressed again, menu ', menu, "pos", pos, "neg", neg, "state", state)
                draw_emoji()
            if (prev_neg > 0):
                # play last neg
                buzz()
                matrix.pixelsFill(matrix.black())
                neg = prev_neg
                pos = 0
                menu = prev_menu
                print('button 3 pressed again, menu ', menu, "pos", pos, "neg", neg, "state", state)
                draw_emoji()

    # === Legacy NFC polling (Zero sends menu 3, neg 4) — sends NFC: prefix ===
    if nfc_mode_active and rfid is not None:
        # Revert from circle/cross back to question mark after the display timer expires
        if nfc_display_state != "question" and time.ticks_diff(time.ticks_ms(), nfc_display_until_ms) >= 0:
            nfc_display_state = "question"
            draw_question_mark()

        # Poll for a new tag only while in the question-mark waiting state to avoid
        # re-sending the same card ID repeatedly while it stays on the reader.
        if nfc_display_state == "question":
            try:
                if rfid.tagPresent():
                    card_id = rfid.readID()
                    print('NFC (legacy) tag:', card_id)
                    if p.is_connected():
                        p.send(('NFC:' + card_id).encode())
                    else:
                        print('NFC: not connected to Zero — card ID not sent')
            except Exception as _nfc_poll_err:
                print('NFC poll error:', _nfc_poll_err)

    # === Game mode NFC polling (GAME:question_open active) — sends TAG: prefix ===
    if _game_state == "question_open" and rfid is not None:
        # Revert the scan-feedback indicator back to question mark after the timer.
        if _game_nfc_display_until_ms and \
                time.ticks_diff(time.ticks_ms(), _game_nfc_display_until_ms) >= 0:
            _game_nfc_display_until_ms = 0
            draw_question_mark()

        # Send TAG: only while showing the question mark (gate prevents duplicate sends
        # while the same card stays on the reader during the display-hold period).
        if _game_nfc_display_until_ms == 0:
            try:
                if rfid.tagPresent():
                    card_id = rfid.readID()
                    if p.is_connected():
                        p.send(('TAG:' + card_id).encode())
                        _log_game_state(
                            "card_scanned",
                            "TAG:{}; green 4×4 outline".format(card_id),
                        )
                    else:
                        _log_game_state(
                            "card_scanned",
                            "TAG:{} not sent — BLE disconnected".format(card_id),
                        )
                    # Green 4×4 outline = tap acknowledged; Zero follows with
                    # GAME:correct / GAME:wrong. Revert to ? if no follow-up.
                    _show_tap_ack()
                    _game_nfc_display_until_ms = time.ticks_add(
                        time.ticks_ms(), NFC_PICO_RESULT_DISPLAY_S * 1000
                    )
            except Exception as _nfc_game_err:
                print('NFC game poll error:', _nfc_game_err)

    sleep_ms(100)
