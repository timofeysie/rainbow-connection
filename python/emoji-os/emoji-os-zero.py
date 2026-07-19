# -*- coding:utf-8 -*-
# Emoji OS Zero
VERSION = " v0.7.1"
# Normalized version string sent to the server (strip leading space / 'v').
_CONTROLLER_VERSION = VERSION.strip().lstrip("v")
# Pico badge version learned from the PAIR_OK:<version> handshake reply.
# Updated in _do_pair_handshake; "unknown" when the Pico replies a bare PAIR_OK
# (pre-v0.3.2 firmware) or when no pairing has happened yet.
_pico_version = "unknown"
# When stdout is redirected (e.g. rc.local >> log), Python buffers unless run with
# `python -u` or PYTHONUNBUFFERED=1 — use flush=True on early prints so the log updates.
print(f"emoji-os-zero{VERSION} starting", flush=True)

import LCD_1in44
import time
import threading
import asyncio
import warnings
import subprocess
import requests
from datetime import datetime, timezone
from bleak import BleakScanner, BleakClient
from bleak.backends.characteristic import BleakGATTCharacteristic
import RPi.GPIO as GPIO

from PIL import Image,ImageDraw,ImageFont,ImageColor
from emojis_zero import *
from animations_zero import fireworks_animation as fw_anim_func, rain_animation as rain_anim_func
from emojis_zero import fireworks_animation, rain_animation, connecting_matrix, connected_matrix, not_connected_matrix

# === Battery Monitoring (Waveshare UPS HAT C — INA219 at I2C 0x43) ===
# Reads bus voltage once per minute in a daemon thread.
# Gracefully no-ops when the HAT or smbus library is absent.
_battery_percent = None   # 0–100, or None when INA219 is unreachable
_battery_voltage = None   # float volts, or None

_INA219_ADDR = 0x43       # Waveshare UPS HAT C default I2C address
_INA219_BUS  = 1          # Standard Raspberry Pi I2C bus number


def _read_ina219_voltage():
    """Return bus voltage in V from the INA219, or None on any error."""
    bus = None
    try:
        try:
            import smbus2
            bus = smbus2.SMBus(_INA219_BUS)
        except ImportError:
            import smbus
            bus = smbus.SMBus(_INA219_BUS)
        # Register 0x02 = bus voltage (16-bit, big-endian from chip)
        raw = bus.read_word_data(_INA219_ADDR, 0x02)
        # smbus returns little-endian on Linux — swap bytes to match INA219 big-endian
        raw = ((raw & 0xFF) << 8) | ((raw >> 8) & 0xFF)
        return (raw >> 3) * 0.004   # bits [15:3], 4 mV per LSB
    except Exception as exc:
        print(f"[BATT] INA219 read error: {exc}", flush=True)
        return None
    finally:
        if bus is not None:
            try:
                bus.close()
            except Exception:
                pass


def _voltage_to_percent(v):
    """Map LiPo voltage (3.0 V – 4.2 V) to 0 – 100 %."""
    if v is None:
        return None
    return max(0, min(100, int((v - 3.0) / 1.2 * 100)))


def _battery_monitor():
    """Background daemon thread: poll INA219 every 60 s."""
    global _battery_percent, _battery_voltage
    while True:
        v = _read_ina219_voltage()
        _battery_voltage = v
        _battery_percent = _voltage_to_percent(v)
        if v is not None:
            print(f"[BATT] {v:.3f} V  {_battery_percent}%", flush=True)
        time.sleep(60)


threading.Thread(target=_battery_monitor, daemon=True).start()

# === Server Configuration ===
# Set SERVER_URL to enable reporting to the emoji server dashboard.
# Leave empty to disable (safe default — server is not required to run).
# no trailing slash please
# deployed server
# SERVER_URL = "https://emoji-staging.kogs.link"
# Local server for testing
SERVER_URL = "http://192.168.68.54:3000"
# Logical Pi Zero id (POST /api/status and /api/emoji).
CONTROLLER_ID = "raspberry-pi-zero"
# If non-empty, used as badgeId for all API posts. If empty, badgeId is derived from
# the BLE address of the connected Pico (see _resolve_badge_id).
BADGE_ID = ""
# Optional extra headers, e.g. {"x-api-key": "..."} — leave empty if unused.
API_HEADERS = {}

if SERVER_URL:
    print(f"[API] SERVER_URL is set — POSTs go to {SERVER_URL}", flush=True)
else:
    print(
        "[API] SERVER_URL is empty — no requests to AWS/dashboard. "
        "Set SERVER_URL in emoji-os-zero.py (HTTPS base, no trailing slash).",
        flush=True,
    )

# === WebSocket URL (derived from SERVER_URL) ===
if SERVER_URL.startswith("https://"):
    _WS_URL = "wss://" + SERVER_URL[len("https://"):]
elif SERVER_URL.startswith("http://"):
    _WS_URL = "ws://" + SERVER_URL[len("http://"):]
else:
    _WS_URL = ""

# === WebSocket / Game state ===
# Updated by the WS client as events arrive.
_ws_game_id       = None   # str | None — current bound game
_ws_game_state    = None   # "draft"|"lobby"|"active"|"completed"|None
_ws_question_id   = None   # str | None — currently open question
_ws_joined        = False  # True once join POST has been sent this session
_join_pending     = False  # True after game.opened arrives; cleared by KEY2 join
_ws_connected     = False  # True while the WS socket is open
# Question phase within an active game (drives Platform icon glyphs).
# None = game active, no question opened yet; "open" / "closed" after first Q.
_ws_question_phase = None  # None | "open" | "closed"
# Per-question answer shown until question_closed (immediate guess feedback).
_game_pair_result = None   # None | "correct" | "wrong"
# True once this pair has shown correct/wrong for the open question (scan or
# question.result). Survives question.closed so a late question.result does not
# re-animate over the white 2×2 "Question closed" glyph.
_game_answered_this_question = False
# End-of-game outcome for LCD (winner/loser animations + glyph).
_game_end_outcome = None   # None | "winner" | "loser" | "ended"

# Reconnect backoff bounds (seconds)
_WS_BACKOFF_MIN_S = 2.0
_WS_BACKOFF_MAX_S = 60.0

# HTTP fallback: poll GET /api/pairs/:pairName when WS is down
_WS_FALLBACK_POLL_S    = 30.0
_last_ws_fallback_poll = 0.0

# === Game mode state ===
# True while the player has selected menu 3 · pos 4 (game mode slot).
game_mode_active = False

# Platform icon / display reference — shared state ids + labels (multiplayer-mode.md).
# Log format: [GAME] zero | <state_id> | <label> | <detail>
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

# BLE GAME:<cmd> → Platform icon state id (wire name may differ from state id).
_GAME_CMD_TO_STATE = {
    "GAME:mode": "mode",
    "GAME:lobby": "lobby",
    "GAME:lobby_joined": "lobby_joined",
    "GAME:active": "active",
    "GAME:question_open": "question_open",
    "GAME:correct": "correct",
    "GAME:wrong": "wrong",
    "GAME:question_close": "question_closed",
    "GAME:ended": "game_ended",
    "GAME:winner": "winner",
    "GAME:loser": "loser",
}


def _log_game_state(state_id: str, detail: str = "") -> None:
    """Emit a narrative game-state line (see multiplayer-mode.md logging section)."""
    label = _GAME_STATE_LABELS.get(state_id, state_id)
    if detail:
        print(f"[GAME] zero | {state_id} | {label} | {detail}", flush=True)
    else:
        print(f"[GAME] zero | {state_id} | {label}", flush=True)

# === NFC Card Mapping ===
# Each entry maps a card ID to a display name (printed to log) and a display
# result ("circle" = blue circle, "x" = red X).
#
# The authoritative mapping is fetched from the server at startup
# (GET /api/nfc-cards, see load_nfc_card_map). NFC_CARD_MAP_FALLBACK is the
# built-in copy used when SERVER_URL is empty or the server is unreachable, so
# the badge still works offline.
NFC_CARD_MAP_FALLBACK = {
    "5B:6F:B8:08": {"name": "R12 - Monkey", "display": "circle", "slotLabel": "A"},
    "DB:93:B7:08": {"name": "W3 - Clown",   "display": "x",      "slotLabel": "B"},
}
# Populated from the server at startup; starts as a copy of the fallback.
NFC_CARD_MAP = dict(NFC_CARD_MAP_FALLBACK)
# How long (seconds) to hold the NFC result on screen before returning to '?'
NFC_RESULT_DISPLAY_S = 5

# === BLE Configuration ===
# Nordic UART Service UUIDs
UART_SERVICE_UUID = "6E400001-B5A3-F393-E0A9-E50E24DCCA9E"
UART_RX_CHAR_UUID = "6E400002-B5A3-F393-E0A9-E50E24DCCA9E"  # Write characteristic
UART_TX_CHAR_UUID = "6E400003-B5A3-F393-E0A9-E50E24DCCA9E"  # Notify characteristic

# === Multiplayer Pairing ===
# PAIR_NAME identifies this controller/badge pair. The matching
# emoji-os-pico-*.py running on the badge must use the same PAIR_NAME.
#
# pair_config.py must live in the directory ABOVE the repo root, e.g.
#   /home/<user>/repos/pair_config.py
# given this script lives at
#   /home/<user>/repos/rainbow-connection/python/emoji-os/emoji-os-zero.py
# The path is resolved relative to this file so it is not tied to any
# specific username. If the file is absent or unreadable, PAIR_NAME
# falls back to "default". See python/emoji-os/project/multiplayer-mode.md.
import os as _os
import importlib.util as _imp_util

_HERE = _os.path.dirname(_os.path.abspath(__file__))
# python/emoji-os/  ->  python/  ->  <repo>/  ->  <repo_parent>/
_PAIR_CONFIG_DIR = _os.path.normpath(_os.path.join(_HERE, "..", "..", ".."))
_PAIR_CONFIG_PATH = _os.path.join(_PAIR_CONFIG_DIR, "pair_config.py")

try:
    if not _os.path.isfile(_PAIR_CONFIG_PATH):
        raise FileNotFoundError(f"not found: {_PAIR_CONFIG_PATH}")
    _spec = _imp_util.spec_from_file_location("pair_config", _PAIR_CONFIG_PATH)
    _pair_mod = _imp_util.module_from_spec(_spec)
    _spec.loader.exec_module(_pair_mod)
    PAIR_NAME = _pair_mod.PAIR_NAME
    if hasattr(_pair_mod, "NFC_CARD_MAP_LOCAL") and isinstance(_pair_mod.NFC_CARD_MAP_LOCAL, dict):
        NFC_CARD_MAP_FALLBACK = _pair_mod.NFC_CARD_MAP_LOCAL
        NFC_CARD_MAP = dict(NFC_CARD_MAP_FALLBACK)
        print(f"[NFC] local card map: {len(NFC_CARD_MAP_FALLBACK)} card(s) from pair_config.py", flush=True)
    _PAIR_CONFIG_SOURCE = _PAIR_CONFIG_PATH
except Exception as _pair_exc:
    PAIR_NAME = "default"
    _PAIR_CONFIG_SOURCE = f"fallback 'default' ({_pair_exc})"

# Target BLE name advertised by the paired Pico (see emoji-os-pico-*.py).
TARGET_DEVICE_NAME = f"Pico-Client-{PAIR_NAME}"
PAIR_HANDSHAKE_TIMEOUT_S = 5.0

print(f"[PAIR] config file : {_PAIR_CONFIG_SOURCE}", flush=True)
print(f"[PAIR] PAIR_NAME   : '{PAIR_NAME}'", flush=True)
print(f"[PAIR] looking for : '{TARGET_DEVICE_NAME}'", flush=True)


def _log_bt_adapter_info():
    """Log Bluetooth adapter status to help diagnose BLE scan failures.

    Runs three quick shell commands and prints their output:
      hciconfig -a  — adapter presence, type, and UP/DOWN state
      bluetoothctl show  — BlueZ adapter info including Powered flag
      rfkill list bluetooth  — whether the adapter is hard/soft-blocked
    All commands run with a 5-second timeout so a missing binary never hangs.
    """
    cmds = [
        ("hciconfig -a",          ["hciconfig", "-a"]),
        ("bluetoothctl show",     ["bluetoothctl", "show"]),
        ("rfkill list bluetooth", ["rfkill", "list", "bluetooth"]),
    ]
    print("[BT-DIAG] ── Bluetooth adapter diagnostics ──", flush=True)
    for label, args in cmds:
        try:
            result = subprocess.run(
                args,
                capture_output=True, text=True, timeout=5
            )
            output = (result.stdout + result.stderr).strip()
            if output:
                for line in output.splitlines():
                    print(f"[BT-DIAG] {label}: {line}", flush=True)
            else:
                print(f"[BT-DIAG] {label}: (no output)", flush=True)
        except FileNotFoundError:
            print(f"[BT-DIAG] {label}: command not found", flush=True)
        except subprocess.TimeoutExpired:
            print(f"[BT-DIAG] {label}: timed out after 5s", flush=True)
        except Exception as _e:
            print(f"[BT-DIAG] {label}: error — {_e}", flush=True)
    print("[BT-DIAG] ── end of adapter diagnostics ──", flush=True)


def _scan_device_service_uuids(device):
    """Service UUIDs from a scan result; prefers non-deprecated Bleak fields."""
    uuids = getattr(device, "service_uuids", None)
    if uuids:
        return list(uuids)
    with warnings.catch_warnings():
        warnings.simplefilter("ignore", FutureWarning)
        meta = getattr(device, "metadata", None)
        if meta:
            return list(meta.get("uuids", []) or [])
    return []


# === Game mode glyphs (Platform icon / display reference) ===
# Fallback 'G' while waiting for a server snapshot in game mode.
game_mode_matrix = [
    [' ', ' ', 'G', 'G', 'G', 'G', ' ', ' '],
    [' ', 'G', ' ', ' ', ' ', ' ', 'G', ' '],
    ['G', ' ', ' ', ' ', ' ', ' ', ' ', ' '],
    ['G', ' ', ' ', ' ', 'G', 'G', 'G', ' '],
    ['G', ' ', ' ', ' ', ' ', ' ', 'G', ' '],
    [' ', 'G', ' ', ' ', ' ', ' ', 'G', ' '],
    [' ', ' ', 'G', 'G', 'G', 'G', ' ', ' '],
    [' ', ' ', ' ', ' ', ' ', ' ', ' ', ' '],
]

# Lobby — not yet joined: solid yellow 4×4 centre
game_lobby_matrix = [
    [' ', ' ', ' ', ' ', ' ', ' ', ' ', ' '],
    [' ', ' ', ' ', ' ', ' ', ' ', ' ', ' '],
    [' ', ' ', 'Y', 'Y', 'Y', 'Y', ' ', ' '],
    [' ', ' ', 'Y', 'Y', 'Y', 'Y', ' ', ' '],
    [' ', ' ', 'Y', 'Y', 'Y', 'Y', ' ', ' '],
    [' ', ' ', 'Y', 'Y', 'Y', 'Y', ' ', ' '],
    [' ', ' ', ' ', ' ', ' ', ' ', ' ', ' '],
    [' ', ' ', ' ', ' ', ' ', ' ', ' ', ' '],
]

# Lobby — joined, waiting: white 4×4 outline
game_lobby_joined_matrix = [
    [' ', ' ', ' ', ' ', ' ', ' ', ' ', ' '],
    [' ', ' ', ' ', ' ', ' ', ' ', ' ', ' '],
    [' ', ' ', 'W', 'W', 'W', 'W', ' ', ' '],
    [' ', ' ', 'W', ' ', ' ', 'W', ' ', ' '],
    [' ', ' ', 'W', ' ', ' ', 'W', ' ', ' '],
    [' ', ' ', 'W', 'W', 'W', 'W', ' ', ' '],
    [' ', ' ', ' ', ' ', ' ', ' ', ' ', ' '],
    [' ', ' ', ' ', ' ', ' ', ' ', ' ', ' '],
]

# Game started / active: solid green 4×4 centre
game_active_matrix = [
    [' ', ' ', ' ', ' ', ' ', ' ', ' ', ' '],
    [' ', ' ', ' ', ' ', ' ', ' ', ' ', ' '],
    [' ', ' ', 'G', 'G', 'G', 'G', ' ', ' '],
    [' ', ' ', 'G', 'G', 'G', 'G', ' ', ' '],
    [' ', ' ', 'G', 'G', 'G', 'G', ' ', ' '],
    [' ', ' ', 'G', 'G', 'G', 'G', ' ', ' '],
    [' ', ' ', ' ', ' ', ' ', ' ', ' ', ' '],
    [' ', ' ', ' ', ' ', ' ', ' ', ' ', ' '],
]

# Question closed: small white 2×2 centre dot
game_question_closed_matrix = [
    [' ', ' ', ' ', ' ', ' ', ' ', ' ', ' '],
    [' ', ' ', ' ', ' ', ' ', ' ', ' ', ' '],
    [' ', ' ', ' ', ' ', ' ', ' ', ' ', ' '],
    [' ', ' ', ' ', 'W', 'W', ' ', ' ', ' '],
    [' ', ' ', ' ', 'W', 'W', ' ', ' ', ' '],
    [' ', ' ', ' ', ' ', ' ', ' ', ' ', ' '],
    [' ', ' ', ' ', ' ', ' ', ' ', ' ', ' '],
    [' ', ' ', ' ', ' ', ' ', ' ', ' ', ' '],
]

# Correct answer: blue filled circle (U = blue in color_map)
game_correct_matrix = [
    [' ', ' ', ' ', 'U', 'U', ' ', ' ', ' '],
    [' ', ' ', 'U', 'U', 'U', 'U', ' ', ' '],
    [' ', 'U', 'U', 'U', 'U', 'U', 'U', ' '],
    ['U', 'U', 'U', 'U', 'U', 'U', 'U', 'U'],
    ['U', 'U', 'U', 'U', 'U', 'U', 'U', 'U'],
    [' ', 'U', 'U', 'U', 'U', 'U', 'U', ' '],
    [' ', ' ', 'U', 'U', 'U', 'U', ' ', ' '],
    [' ', ' ', ' ', 'U', 'U', ' ', ' ', ' '],
]

# BLE Controller class - from working controller-1.3.py
class BLEController:
    """BLE Central controller that connects to Pico and sends emoji commands
    Enhanced with better device discovery using test write method
    """
    
    def __init__(self):
        self.client = None
        self.device_address = None
        self.connected = False
        self._pair_event = None
        self._pair_response = None
        
    async def scan_for_device(self, timeout=10):
        """Scan for the target Pico device by name or service UUID"""
        global ble_connection_status
        ble_connection_status = "scanning"
        # Update display to show scanning indicator
        draw_connection_indicator()
        disp.LCD_ShowImage(image,0,0)
        print("[BLE] scanning — queueing POST /api/status", flush=True)
        post_to_server("/api/status", _status_payload("scanning"))

        print(f"Scanning for Pico device (target name: '{TARGET_DEVICE_NAME}')...")
        print("Multiplayer pairing is strict: only the device advertising the")
        print(f"name '{TARGET_DEVICE_NAME}' (PAIR_NAME='{PAIR_NAME}') will be selected.")
        
        # First, try scanning by service UUID, but only accept exact-name matches
        # so multi-pair environments don't grab the wrong badge.
        print(f"\nAttempting to scan by service UUID (filtered by name) — timeout={timeout}s ...", flush=True)
        _t0 = time.monotonic()
        try:
            devices = await BleakScanner.discover(
                timeout=timeout,
                service_uuids=[UART_SERVICE_UUID]
            )
            print(f"[BLE] UUID scan returned {len(devices)} device(s) in {time.monotonic()-_t0:.1f}s", flush=True)
            if devices:
                print(f"✓ Found {len(devices)} device(s) advertising Nordic UART Service:")
                for device in devices:
                    name = device.name or "(No Name)"
                    print(f"  - {name:<24} | {device.address}")
                for device in devices:
                    if device.name == TARGET_DEVICE_NAME:
                        self.device_address = device.address
                        print(f"✓ Selected device by name: {device.name} at {self.device_address}")
                        return True
                print(f"  No advertisement matched '{TARGET_DEVICE_NAME}'; trying general scan.")
        except Exception as e:
            print(f"[BLE] UUID scan failed after {time.monotonic()-_t0:.1f}s: {e}", flush=True)

        # Fallback: General scan and check for name match or verify service
        print(f"\nPerforming general scan for {timeout} seconds...", flush=True)
        _t1 = time.monotonic()
        try:
            devices = await BleakScanner.discover(timeout=timeout)
        except Exception as e:
            print(f"[BLE] General scan failed after {time.monotonic()-_t1:.1f}s: {e}", flush=True)
            devices = []
        print(f"[BLE] General scan returned {len(devices)} device(s) in {time.monotonic()-_t1:.1f}s", flush=True)

        print(f"Found {len(devices)} BLE devices:")
        print("-" * 50)
        
        # First, check for exact name match
        for i, device in enumerate(devices, 1):
            name = device.name or "(No Name)"
            print(f"{i:2d}. {name:<20} | {device.address}")
            
            if device.name == TARGET_DEVICE_NAME:
                print(f"    *** FOUND TARGET DEVICE BY NAME! ***")
                self.device_address = device.address
                print("-" * 50)
                print(f"✓ Found {TARGET_DEVICE_NAME} at address: {self.device_address}")
                return True
        
        print("-" * 50)
        
        # If no name match, try to find by service UUID by connecting to candidates
        # whose name matches TARGET_DEVICE_NAME. Strict pairing means we never
        # select a device with a different advertised name.
        print("\nNo exact name match yet. Checking name-matched UART candidates...")
        candidate_devices = []
        for device in devices:
            if device.name != TARGET_DEVICE_NAME:
                continue
            adv_uuids = _scan_device_service_uuids(device)
            if UART_SERVICE_UUID.lower() in [s.lower() for s in adv_uuids]:
                candidate_devices.append(device)
                print(f"  Candidate: {device.name} ({device.address}) - UART service in advertisement")
        
        if candidate_devices:
            device = candidate_devices[0]
            self.device_address = device.address
            print(f"✓ Selected candidate device: {device.name} at {self.device_address}")
            return True
        
        # Last resort: try connecting to devices and test write (avoids service discovery issues)
        print("\nTesting devices by attempting connection and test write...")
        print("(This may take a moment - checking up to 15 devices)...")
        
        # Known Pico MAC addresses from previous successful connections (for priority)
        known_pico_addresses = ["28:CD:C1:05:AB:A4", "28:CD:C1:07:2C:E8", "2C:CF:67:05:A4:F4"]
        
        # First, check known addresses (faster)
        for known_addr in known_pico_addresses:
            for device in devices:
                if device.address.upper() == known_addr.upper():
                    name = device.name or "(No Name)"
                    print(f"\n  Testing known address: {name} ({device.address})...", end=" ")
                    if await self._test_device_connection(device.address):
                        self.device_address = device.address
                        print(f"✓ FOUND!")
                        print(f"\n✓ Found Pico device (known address):")
                        print(f"  Name: {name}")
                        print(f"  Address: {self.device_address}")
                        return True
                    break
        
        # Then test all other devices
        for device in devices[:15]:  # Check up to 15 devices
            # Skip if we already checked this as a known address
            if device.address.upper() in [a.upper() for a in known_pico_addresses]:
                continue
                
            name = device.name or "(No Name)"
            print(f"  Testing {name} ({device.address})...", end=" ")
            if await self._test_device_connection(device.address):
                self.device_address = device.address
                print(f"✓ FOUND!")
                print(f"\n✓ Found Pico device with Nordic UART Service:")
                print(f"  Name: {name}")
                print(f"  Address: {self.device_address}")
                return True
        
        print(f"\n✗ Could not find Pico device matching '{TARGET_DEVICE_NAME}'")
        print("\nTroubleshooting tips:")
        print(f"1. Confirm the badge is running emoji-os-pico-*.py with PAIR_NAME='{PAIR_NAME}'")
        print("2. Check that the Pico console prints 'Starting advertising...'")
        print(f"3. Confirm the Pico's advertised name is exactly '{TARGET_DEVICE_NAME}'")
        print("4. Try moving devices closer together")
        print("5. Restart both devices")
        ble_connection_status = "disconnected"
        draw_connection_indicator()
        disp.LCD_ShowImage(image,0,0)
        post_to_server("/api/status", _status_payload("disconnected"))
        return False
    
    async def _test_device_connection(self, address):
        """Test if a device has the Nordic UART Service by attempting a test write"""
        test_client = None
        try:
            test_client = BleakClient(address)
            await test_client.connect(timeout=3.0)
            
            # Try to write a test command directly to the RX characteristic
            # If this succeeds, we know the device has the UART service
            test_command = b"STATUS"  # Non-destructive test command
            try:
                await test_client.write_gatt_char(UART_RX_CHAR_UUID, test_command)
                # If write succeeded, this is likely our device
                await test_client.disconnect()
                return True
            except Exception as write_error:
                # Write failed - not the right device or characteristic doesn't exist
                await test_client.disconnect()
                return False
                
        except asyncio.TimeoutError:
            if test_client:
                try:
                    await test_client.disconnect()
                except:
                    pass
            return False
        except Exception as e:
            # Connection failed or other error
            if test_client:
                try:
                    await test_client.disconnect()
                except:
                    pass
            return False
    
    async def connect_to_device(self):
        """Connect to the discovered Pico device"""
        global ble_connection_status
        if not self.device_address:
            print("No device address available. Run scan_for_device() first.")
            ble_connection_status = "disconnected"
            draw_connection_indicator()
            disp.LCD_ShowImage(image,0,0)
            return False
            
        try:
            print(f"Connecting to {self.device_address}...")
            ble_connection_status = "connecting"
            draw_connection_indicator()
            disp.LCD_ShowImage(image,0,0)
            print("[BLE] connecting — queueing POST /api/status", flush=True)
            post_to_server("/api/status", _status_payload("connecting"))

            self.client = BleakClient(
                self.device_address,
                disconnected_callback=_on_pico_disconnect,
            )
            await self.client.connect(timeout=10.0)
            
            if self.client.is_connected:
                print("✓ Successfully connected at BLE layer — running pair handshake")
                # Verify the service exists before running the handshake
                try:
                    uart_found = False
                    for service in self.client.services:
                        if service.uuid.lower() == UART_SERVICE_UUID.lower():
                            uart_found = True
                            print(f"✓ Verified Nordic UART Service is available")
                            break
                    if not uart_found:
                        print("⚠ Warning: Connected but Nordic UART Service not found!")
                        print("  This might not be the correct device.")
                except Exception as e:
                    print(f"⚠ Warning: Could not verify services: {e}")
                # Strict multiplayer pairing: only mark connected after PAIR_OK
                if not await self._do_pair_handshake():
                    print("✗ Pair handshake failed — disconnecting", flush=True)
                    self.connected = False
                    try:
                        # Bleak's disconnected_callback (_on_pico_disconnect)
                        # schedules _reconnect for us, so we deliberately do
                        # NOT create another _reconnect task here. Otherwise
                        # two BlueZ scans race and the second one fails with
                        # "Operation already in progress".
                        await self.client.disconnect()
                    except Exception:
                        pass
                    ble_connection_status = "disconnected"
                    draw_connection_indicator()
                    disp.LCD_ShowImage(image, 0, 0)
                    post_to_server("/api/status", _status_payload("disconnected"))
                    return False
                self.connected = True
                ble_connection_status = "connected"
                draw_connection_indicator()
                disp.LCD_ShowImage(image,0,0)
                print("[BLE] connected — queueing POST /api/status", flush=True)
                post_to_server("/api/status", _status_payload("connected"))
                # Set up persistent TX notification handler so the Pico can
                # push async messages (e.g. NFC card IDs) to the Zero.
                try:
                    await self.client.start_notify(UART_TX_CHAR_UUID, _on_pico_tx_notify)
                    print("[BLE] TX notifications enabled — Pico→Zero channel active", flush=True)
                except Exception as _ne:
                    print(f"[BLE] warning: could not enable TX notifications: {_ne}", flush=True)
                # Cancel any previous heartbeat and start a fresh one
                global _heartbeat_task, _last_status_liveness_post
                if _heartbeat_task and not _heartbeat_task.done():
                    _heartbeat_task.cancel()
                _last_status_liveness_post = time.monotonic()
                _heartbeat_task = asyncio.create_task(_heartbeat_loop())
                return True
            else:
                print("✗ Failed to connect (not connected after connect() call)")
                ble_connection_status = "disconnected"
                draw_connection_indicator()
                disp.LCD_ShowImage(image,0,0)
                return False
                
        except asyncio.TimeoutError:
            print(f"✗ Connection timeout - device may not be in range or not advertising")
            ble_connection_status = "disconnected"
            draw_connection_indicator()
            disp.LCD_ShowImage(image,0,0)
            return False
        except Exception as e:
            error_msg = str(e)
            print(f"✗ Connection error: {error_msg}")
            if "not found" in error_msg.lower() or "not available" in error_msg.lower():
                print("  → Device may not be advertising or is out of range")
            elif "timeout" in error_msg.lower():
                print("  → Connection timed out - device may be busy or not responding")
            ble_connection_status = "disconnected"
            draw_connection_indicator()
            disp.LCD_ShowImage(image,0,0)
            return False
    
    async def _do_pair_handshake(self):
        """Send 'PAIR:<PAIR_NAME>' and wait for 'PAIR_OK' over TX notify.

        Returns True on PAIR_OK, False on PAIR_FAIL / timeout / error. The
        connection is left open on success and closed by the caller on failure.
        """
        self._pair_response = None
        self._pair_event = asyncio.Event()

        def _on_notify(_sender: BleakGATTCharacteristic, data: bytearray):
            try:
                text = bytes(data).decode("utf-8", "ignore").strip()
            except Exception:
                text = ""
            print(f"[PAIR] notify from Pico: {text!r}", flush=True)
            self._pair_response = text
            if self._pair_event:
                self._pair_event.set()

        try:
            await self.client.start_notify(UART_TX_CHAR_UUID, _on_notify)
        except Exception as e:
            print(f"[PAIR] start_notify failed: {e}", flush=True)
            return False

        pair_msg = f"PAIR:{PAIR_NAME}".encode("utf-8")
        try:
            await self.client.write_gatt_char(UART_RX_CHAR_UUID, pair_msg)
            print(f"[PAIR] sent {pair_msg!r}", flush=True)
        except Exception as e:
            print(f"[PAIR] write failed: {e}", flush=True)
            try:
                await self.client.stop_notify(UART_TX_CHAR_UUID)
            except Exception:
                pass
            return False

        try:
            await asyncio.wait_for(self._pair_event.wait(), timeout=PAIR_HANDSHAKE_TIMEOUT_S)
        except asyncio.TimeoutError:
            print(f"[PAIR] handshake timed out after {PAIR_HANDSHAKE_TIMEOUT_S}s", flush=True)
            try:
                await self.client.stop_notify(UART_TX_CHAR_UUID)
            except Exception:
                pass
            return False

        try:
            await self.client.stop_notify(UART_TX_CHAR_UUID)
        except Exception:
            pass

        resp = self._pair_response or ""
        if resp == "PAIR_OK" or resp.startswith("PAIR_OK:"):
            global _pico_version
            if ":" in resp:
                _pico_version = resp.split(":", 1)[1].strip() or "unknown"
            else:
                # Bare PAIR_OK — pre-v0.3.2 firmware; version unknown.
                _pico_version = "unknown"
            print(f"[PAIR] OK — paired with PAIR_NAME='{PAIR_NAME}' picoVersion='{_pico_version}'", flush=True)
            return True
        print(f"[PAIR] handshake rejected by Pico: {self._pair_response!r}", flush=True)
        return False

    async def send_emoji_command(self, menu, pos, neg):
        """Send emoji selection command to the connected Pico"""
        if not self.client or not self.client.is_connected:
            print("Not connected to any device — skipping BLE write and /api/emoji", flush=True)
            return False

        command = f"{menu}:{pos}:{neg}"
        try:
            await self.client.write_gatt_char(UART_RX_CHAR_UUID, command.encode("utf-8"))
            print(f"✓ Sent emoji command: '{command}'", flush=True)
            print("[BLE] queueing POST /api/emoji", flush=True)
            post_to_server("/api/emoji", _emoji_payload(menu, pos, neg))
            return True

        except Exception as e:
            print(f"✗ Send failed for '{command}': {e} — marking as disconnected", flush=True)
            self.connected = False
            global ble_connection_status
            ble_connection_status = "disconnected"
            draw_connection_indicator()
            disp.LCD_ShowImage(image, 0, 0)
            post_to_server("/api/status", _status_payload("disconnected"))
            if ble_event_loop and ble_event_loop.is_running():
                asyncio.run_coroutine_threadsafe(_reconnect(), ble_event_loop)
            return False
    
    async def disconnect(self):
        """Disconnect from the device"""
        global ble_connection_status, _heartbeat_task
        if _heartbeat_task and not _heartbeat_task.done():
            _heartbeat_task.cancel()
            _heartbeat_task = None
        if self.client and self.client.is_connected:
            await self.client.disconnect()
            print("Disconnected from Pico")
            self.connected = False
            ble_connection_status = "disconnected"
            draw_connection_indicator()
            disp.LCD_ShowImage(image,0,0)
            post_to_server("/api/status", _status_payload("disconnected"))

# Global BLE controller instance
ble_controller = BLEController()
ble_connection_thread = None
ble_event_loop = None

# Connection status state: "idle", "connecting", "connected", "disconnected"
ble_connection_status = "idle"

# Heartbeat asyncio task — cancelled and replaced on each reconnect
_heartbeat_task = None


def _utc_iso_timestamp():
    # Hint for APIs only — Pi RTC/NTP may be wrong; emoji-app should use server time.
    return datetime.now(timezone.utc).isoformat()


def _resolve_badge_id():
    if BADGE_ID and BADGE_ID.strip():
        return BADGE_ID.strip()
    addr = ble_controller.device_address
    if addr:
        slug = addr.lower().replace(":", "-")
        return f"badge-{slug}"
    return "unknown"


def _emoji_label(menu, pos, neg):
    """Human-readable slug for POST /api/emoji; matches get_main_emoji selections."""
    if menu == 0:
        if pos == 1:
            return "regular"
        if pos == 2:
            return "wry"
        if pos == 3:
            return "happy"
        if pos == 4:
            return "heart_eyes"
        if neg == 1:
            return "thick_lips"
        if neg == 2:
            return "sad_wry"
        if neg == 3:
            return "sad"
        if neg == 4:
            return "crossbone_eyes"
    elif menu == 1:
        if pos == 1:
            return "fireworks"
        if pos == 2:
            return "circular_rainbow"
        if pos == 3:
            return "chakana"
        if pos == 4:
            return "heart"
        if neg == 1:
            return "rain"
    elif menu == 2:
        if pos == 1:
            return "finn"
        if pos == 2:
            return "pikachu"
        if pos == 3:
            return "crab"
        if pos == 4:
            return "frog"
        if neg == 1:
            return "bald"
        if neg == 2:
            return "surprise"
        if neg == 3:
            return "green_monster"
        if neg == 4:
            return "angry"
    elif menu == 3:
        if pos == 1:
            return "others_circle"
        if pos == 2:
            return "others_yes"
        if pos == 3:
            return "others_somi"
        if pos == 4:
            return "others_nfc_pos"
        if neg == 1:
            return "others_x"
        if neg == 2:
            return "others_no"
        if neg == 4:
            return "others_nfc_neg"
    return f"m{menu}-{pos}-{neg}"


def _status_payload(ble_status: str):
    # API: startup | scanning | connecting | connected | disconnected (see server statusBodySchema).
    payload: dict = {
        "controllerId": CONTROLLER_ID,
        "badgeId": _resolve_badge_id(),
        "bleStatus": ble_status,
        "timestamp": _utc_iso_timestamp(),
        "pairName": PAIR_NAME,
        "controllerVersion": _CONTROLLER_VERSION,
        "picoVersion": _pico_version,
    }
    if _battery_percent is not None:
        payload["batteryLevel"] = _battery_percent
    return payload


def _emoji_payload(menu, pos, neg):
    return {
        "controllerId": CONTROLLER_ID,
        "badgeId": _resolve_badge_id(),
        "menu": menu,
        "pos": pos,
        "neg": neg,
        "label": _emoji_label(menu, pos, neg),
        "timestamp": _utc_iso_timestamp(),
        "pairName": PAIR_NAME,
    }


# Log once if posts are disabled so rc.local.log shows why nothing reaches the API.
_api_skip_empty_url_logged = False


def post_to_server(path: str, payload: dict):
    """Fire-and-forget HTTP POST to the emoji server.

    Runs in a daemon thread so a slow or unreachable server never blocks the UI loop.
    No-op when SERVER_URL is empty.
    """
    global _api_skip_empty_url_logged
    if not SERVER_URL:
        if not _api_skip_empty_url_logged:
            print(
                "[API] skip: SERVER_URL is empty — no HTTP posts (set SERVER_URL at top of script)",
                flush=True,
            )
            _api_skip_empty_url_logged = True
        return

    def _post():
        cid = payload.get("controllerId", "?")
        bid = payload.get("badgeId", "?")
        url = f"{SERVER_URL}{path}"
        try:
            kw = {"json": payload, "timeout": 3}
            if API_HEADERS:
                kw["headers"] = API_HEADERS
            print(f"[API] POST {path} controller={cid} badge={bid}", flush=True)
            r = requests.post(url, **kw)
            snippet = (r.text or "").replace("\n", " ").strip()
            if len(snippet) > 100:
                snippet = snippet[:100] + "…"
            print(f"[API] response {path} -> HTTP {r.status_code} {snippet}", flush=True)
        except Exception as e:
            print(f"[API] request failed {path}: {e}", flush=True)

    threading.Thread(target=_post, daemon=True).start()


def fetch_from_server(path: str):
    """Blocking HTTP GET to the emoji server; returns parsed JSON or None.

    Returns None when SERVER_URL is empty or the request fails, so callers can
    fall back to local defaults. Unlike post_to_server this is synchronous,
    because callers (e.g. startup config loads) need the result.
    """
    if not SERVER_URL:
        return None
    url = f"{SERVER_URL}{path}"
    try:
        kw = {"timeout": 3}
        if API_HEADERS:
            kw["headers"] = API_HEADERS
        print(f"[API] GET {path}", flush=True)
        r = requests.get(url, **kw)
        print(f"[API] response {path} -> HTTP {r.status_code}", flush=True)
        if r.status_code == 200:
            return r.json()
    except Exception as e:
        print(f"[API] request failed {path}: {e}", flush=True)
    return None


def load_nfc_card_map():
    """Fetch the NFC card mapping from the server and update NFC_CARD_MAP.

    Transforms the API's ``{"cards": [{"id", "name", "display", "slotLabel"}, ...]}``
    into the in-memory ``{id: {"name", "display", "slotLabel"}}`` shape used by
    _handle_nfc_card and _relay_nfc_tag. On any failure, keeps NFC_CARD_MAP_FALLBACK
    so the badge still works offline.
    """
    global NFC_CARD_MAP
    data = fetch_from_server("/api/nfc-cards")
    cards = data.get("cards") if isinstance(data, dict) else None
    if not cards:
        NFC_CARD_MAP = dict(NFC_CARD_MAP_FALLBACK)
        print(
            f"[NFC] using built-in card map ({len(NFC_CARD_MAP)} cards) — "
            "server unavailable or empty",
            flush=True,
        )
        return

    new_map = {}
    for card in cards:
        try:
            entry = {
                "name":    card["name"],
                "display": card["display"],
            }
            if "slotLabel" in card:
                entry["slotLabel"] = card["slotLabel"]
            new_map[card["id"]] = entry
        except (KeyError, TypeError):
            print(f"[NFC] skipping malformed card entry: {card!r}", flush=True)

    if new_map:
        NFC_CARD_MAP = new_map
        print(f"[NFC] loaded {len(new_map)} card(s) from server", flush=True)
    else:
        NFC_CARD_MAP = dict(NFC_CARD_MAP_FALLBACK)
        print("[NFC] server returned no usable cards; using built-in map", flush=True)


def _on_pico_disconnect(client: BleakClient):
    """Bleak calls this (sync) when the BLE connection is lost unexpectedly."""
    global ble_connection_status
    print("⚠ Pico disconnected unexpectedly")
    ble_controller.connected = False
    ble_connection_status = "disconnected"
    draw_connection_indicator()
    disp.LCD_ShowImage(image, 0, 0)
    post_to_server("/api/status", _status_payload("disconnected"))
    if ble_event_loop and ble_event_loop.is_running():
        asyncio.run_coroutine_threadsafe(_reconnect(), ble_event_loop)


def _relay_nfc_tag(card_uid: str):
    """Relay a TAG:<cardUid> notification from the Pico as POST /api/guesses.

    On a successful response with ``isCorrect``, updates the Zero LCD and sends
    ``GAME:correct`` / ``GAME:wrong`` to the Pico immediately (Platform icon
    Card scanned → Correct/Wrong answer flow).
    """
    if not _ws_game_id or not _ws_question_id:
        print(
            f"[NFC] TAG {card_uid!r} ignored — no active game/question "
            f"(gameId={_ws_game_id} questionId={_ws_question_id})",
            flush=True,
        )
        return
    card_info = NFC_CARD_MAP.get(card_uid, {})
    payload = {
        "gameId":     _ws_game_id,
        "questionId": _ws_question_id,
        "pairName":   PAIR_NAME,
        "badgeId":    _resolve_badge_id(),
        "cardUid":    card_uid,
        "slotLabel":  card_info.get("slotLabel"),
    }
    _log_game_state(
        "card_scanned",
        f"TAG={card_uid!r} slotLabel={payload['slotLabel']!r} → POST /api/guesses",
    )

    def _post_guess_and_apply():
        if not SERVER_URL:
            print("[API] skip guess POST — SERVER_URL empty", flush=True)
            return
        url = f"{SERVER_URL}/api/guesses"
        try:
            kw = {"json": payload, "timeout": 5}
            if API_HEADERS:
                kw["headers"] = API_HEADERS
            r = requests.post(url, **kw)
            snippet = (r.text or "").replace("\n", " ").strip()
            if len(snippet) > 100:
                snippet = snippet[:100] + "…"
            print(f"[API] response /api/guesses -> HTTP {r.status_code} {snippet}", flush=True)
            if not r.ok:
                return
            try:
                data = r.json()
            except Exception:
                data = {}
            is_correct = data.get("isCorrect")
            if is_correct is None:
                print(
                    "[GAME] zero | card_scanned | Card scanned | "
                    "guess OK but no isCorrect in response — waiting for question.result",
                    flush=True,
                )
                return
            if ble_event_loop is None:
                return
            asyncio.run_coroutine_threadsafe(
                _apply_pair_answer(
                    bool(is_correct),
                    f"POST /api/guesses isCorrect={is_correct} slotLabel={data.get('slotLabel')!r}",
                ),
                ble_event_loop,
            )
        except Exception as exc:
            print(f"[API] request failed /api/guesses: {exc}", flush=True)

    threading.Thread(target=_post_guess_and_apply, daemon=True).start()


def _on_pico_tx_notify(_sender: BleakGATTCharacteristic, data: bytearray):
    """Persistent TX notification handler — receives async messages from the Pico.

    Handles two prefixes:
    - ``TAG:<cardUid>``  — new game-mode path (Step 4 Pico firmware); relays
      the UID to the server as a guess via POST /api/guesses.
    - ``NFC:<card_id>``  — legacy path; looks up the card in NFC_CARD_MAP and
      updates the Zero/Pico display (unchanged behaviour).
    """
    try:
        text = bytes(data).decode("utf-8", "ignore").strip()
        print(f"[PICO→ZERO] {text!r}", flush=True)
        if text.startswith("TAG:"):
            card_uid = text[4:]
            _relay_nfc_tag(card_uid)
        elif text.startswith("NFC:"):
            card_id = text[4:]
            _handle_nfc_card(card_id)
    except Exception as e:
        print(f"[BLE] error in TX notify handler: {e}", flush=True)


def _handle_nfc_card(card_id: str):
    """Process an NFC card ID received from the Pico.

    Looks up the card in NFC_CARD_MAP, updates the Zero display, sends
    the result back to the Pico so its matrix shows the same response,
    and POSTs the result to /api/emoji so the dashboard reflects the scan.
    The result is cleared after NFC_RESULT_DISPLAY_S seconds.
    """
    global nfc_last_result, nfc_last_card_name

    if not nfc_mode_active:
        print(f"[NFC] card read ignored (not in NFC mode): {card_id}", flush=True)
        return

    card = NFC_CARD_MAP.get(card_id)
    if card:
        nfc_last_card_name = card["name"]
        nfc_last_result = card["display"]
        print(f"[NFC] known card: {card['name']} → {card['display']}", flush=True)
    else:
        nfc_last_card_name = f"Unknown ({card_id})"
        nfc_last_result = "unknown"
        print(f"[NFC] unknown card: {card_id}", flush=True)

    draw_display()

    # Post the NFC scan result to the server so the dashboard updates.
    # "circle" cards → menu 3 pos 4 neg 0 (others_nfc_pos)
    # "x" / unknown  → menu 3 pos 0 neg 4 (others_nfc_neg)
    if nfc_last_result == "circle":
        post_to_server("/api/emoji", _emoji_payload(3, 4, 0))
    else:
        post_to_server("/api/emoji", _emoji_payload(3, 0, 4))

    # Send result to Pico so its matrix mirrors the Zero's response
    result_symbol = "circle" if nfc_last_result == "circle" else "x"
    nfc_result_cmd = f"NFC_RESULT:{result_symbol}".encode("utf-8")
    if ble_event_loop and ble_controller.client and ble_controller.client.is_connected:
        async def _send_nfc_result():
            try:
                await ble_controller.client.write_gatt_char(UART_RX_CHAR_UUID, nfc_result_cmd)
                print(f"[NFC] sent to Pico: {nfc_result_cmd!r}", flush=True)
            except Exception as exc:
                print(f"[NFC] send to Pico failed: {exc}", flush=True)
        asyncio.run_coroutine_threadsafe(_send_nfc_result(), ble_event_loop)

    # After the display hold period, revert to the waiting question mark
    def _reset_nfc_display():
        global nfc_last_result, nfc_last_card_name
        time.sleep(NFC_RESULT_DISPLAY_S)
        if nfc_mode_active:
            nfc_last_result = None
            nfc_last_card_name = ""
            draw_display()

    threading.Thread(target=_reset_nfc_display, daemon=True).start()


async def _reconnect():
    """Scan and reconnect after an unexpected BLE drop."""
    await asyncio.sleep(2)  # brief back-off before scanning
    if await ble_controller.scan_for_device(timeout=10):
        await ble_controller.connect_to_device()


# === WebSocket client ===

async def _ble_write_game_cmd(cmd: str):
    """Write a GAME:* command to the Pico over BLE. No-op if not connected."""
    state_id = _GAME_CMD_TO_STATE.get(cmd)
    if not (ble_controller.client and ble_controller.client.is_connected):
        if state_id:
            _log_game_state(state_id, f"BLE not connected — skipping {cmd}")
        else:
            print(f"[WS] BLE not connected — skipping {cmd}", flush=True)
        return
    try:
        await ble_controller.client.write_gatt_char(
            UART_RX_CHAR_UUID, cmd.encode("utf-8")
        )
        if state_id:
            _log_game_state(state_id, f"BLE→{cmd}")
        else:
            print(f"[BLE] wrote {cmd!r}", flush=True)
    except Exception as exc:
        if state_id:
            _log_game_state(state_id, f"BLE→{cmd} failed: {exc}")
        else:
            print(f"[BLE] write {cmd!r} failed: {exc}", flush=True)


async def _apply_pair_answer(is_correct: bool, detail: str, *, force: bool = False):
    """Show correct/wrong on Zero LCD and Pico; hold until question_closed."""
    global _game_pair_result, _game_answered_this_question
    state_id = "correct" if is_correct else "wrong"
    if _game_answered_this_question and not force:
        print(
            f"[GAME] zero | {state_id} | {_GAME_STATE_LABELS[state_id]} | "
            f"skip re-animate (already answered); {detail}",
            flush=True,
        )
        return
    # Do not flash correct/wrong after the question has already closed to the
    # white 2×2 glyph — that would fight the Question closed state.
    if _ws_question_phase == "closed" and not force:
        print(
            f"[GAME] zero | {state_id} | {_GAME_STATE_LABELS[state_id]} | "
            f"skip — question already closed; {detail}",
            flush=True,
        )
        _game_answered_this_question = True
        return
    _game_pair_result = state_id
    _game_answered_this_question = True
    _log_game_state(state_id, detail)
    if game_mode_active:
        draw_display()
    await _ble_write_game_cmd("GAME:correct" if is_correct else "GAME:wrong")


def _start_game_outcome_animation(is_winner: bool):
    """Run fireworks (winner) or rain (loser) on the Zero LCD in a daemon thread."""
    global animation_running, stop_animation, fullscreen_mode

    def _run():
        global animation_running, stop_animation, fullscreen_mode
        if animation_running:
            stop_animation = True
            time.sleep(0.3)
        animation_running = True
        stop_animation = False
        fullscreen_mode = True
        scale = 16
        try:
            if is_winner:
                fw_anim_func(
                    draw, image, disp, scale, 0, 0,
                    iters=10,
                    interruption_check=lambda: stop_animation,
                )
            else:
                rain_anim_func(
                    draw, image, disp, scale, 0, 0,
                    iters=80, density=1,
                    interruption_check=lambda: stop_animation,
                )
        except Exception as exc:
            print(f"[GAME] outcome animation error: {exc}", flush=True)
        finally:
            animation_running = False
            if game_mode_active:
                draw_display()

    threading.Thread(target=_run, daemon=True).start()


def _game_mode_display_matrix():
    """Return the 8×8 matrix for the current Platform icon game state."""
    if _game_end_outcome == "winner":
        return fireworks_animation.preview
    if _game_end_outcome == "loser":
        return rain_animation.preview
    if _game_end_outcome == "ended":
        return game_question_closed_matrix
    if _game_pair_result == "correct":
        return game_correct_matrix
    if _game_pair_result == "wrong":
        return others_x_matrix
    if _ws_game_state == "lobby" and not _ws_joined:
        return game_lobby_matrix
    if _ws_game_state == "lobby":
        return game_lobby_joined_matrix
    if _ws_game_state == "active":
        if _ws_question_phase == "open":
            return question_mark_matrix
        if _ws_question_phase == "closed":
            return game_question_closed_matrix
        return game_active_matrix
    if _ws_game_state == "completed":
        return game_question_closed_matrix
    return game_mode_matrix


async def _apply_game_state_to_display():
    """Redraw the Zero display and sync the Pico with the current game state.

    Called after a WS reconnect/welcome snapshot and when the user enters game
    mode locally, so both screens reflect the server-authoritative state.
    """
    global _ws_question_phase
    if _ws_game_state == "active" and _ws_question_id:
        _ws_question_phase = "open"
    elif _ws_game_state == "active" and _ws_question_phase is None:
        pass  # keep None → green active until first question
    if game_mode_active:
        draw_display()
    # Sync Pico with the current known game state so a reconnect or late
    # game-mode entry picks up the right display without waiting for the next
    # server event.
    if _ws_game_state == "lobby" and not _ws_joined:
        await _ble_write_game_cmd("GAME:lobby")
    elif _ws_game_state == "lobby" and _ws_joined:
        await _ble_write_game_cmd("GAME:lobby_joined")
    elif _ws_game_state == "active" and _ws_question_id:
        await _ble_write_game_cmd("GAME:question_open")
    elif _ws_game_state == "active" and _ws_question_phase == "closed":
        await _ble_write_game_cmd("GAME:question_close")
    elif _ws_game_state == "active":
        await _ble_write_game_cmd("GAME:active")
    elif _ws_game_state == "completed":
        if _game_end_outcome == "winner":
            await _ble_write_game_cmd("GAME:winner")
        elif _game_end_outcome == "loser":
            await _ble_write_game_cmd("GAME:loser")
        else:
            await _ble_write_game_cmd("GAME:ended")
    else:
        # draft / None / unknown — show standby 'G' so Pico matches Zero game mode
        await _ble_write_game_cmd("GAME:mode")


async def _ws_handle_event(event: dict):
    """Dispatch a single WebSocket event from the server."""
    global _ws_game_id, _ws_game_state, _ws_question_id, _ws_joined, _join_pending
    global _ws_question_phase, _game_pair_result, _game_answered_this_question
    global _game_end_outcome

    etype = event.get("type")
    print(f"[WS] event: {etype}", flush=True)

    if etype == "controller.welcome":
        # Server WS welcome is a lightweight ack (pairName only). A rich
        # snapshot comes from GET /api/pairs (synthetic welcome) or later
        # game.* events. Do not clear lobby/join state on the empty ack —
        # that races with the post-hello poll and wipes game.opened.
        if "gameId" not in event and "state" not in event:
            print("[WS] welcome ack (no game snapshot)", flush=True)
            return
        _ws_game_id     = event.get("gameId")
        _ws_game_state  = event.get("state")
        _ws_question_id = event.get("openQuestionId")
        _ws_joined      = event.get("joined", False)
        # KEY2 join only works when lobby is open and we have not joined yet.
        _join_pending = bool(
            _ws_game_state == "lobby" and not _ws_joined and _ws_game_id
        )
        _game_pair_result = None
        _game_answered_this_question = False
        _game_end_outcome = None
        if _ws_game_state == "active" and _ws_question_id:
            _ws_question_phase = "open"
        elif _ws_game_state == "active":
            _ws_question_phase = None
        else:
            _ws_question_phase = None
        print(
            f"[WS] welcome: game={_ws_game_id} state={_ws_game_state} "
            f"joined={_ws_joined} join_pending={_join_pending}",
            flush=True,
        )
        await _apply_game_state_to_display()

    elif etype == "game.opened":
        _ws_game_id    = event.get("gameId")
        _ws_game_state = "lobby"
        _ws_joined     = False
        _join_pending  = True
        _ws_question_phase = None
        _game_pair_result = None
        _game_answered_this_question = False
        _game_end_outcome = None
        _log_game_state("lobby", f"WS game.opened gameId={_ws_game_id}")
        if game_mode_active:
            draw_display()
        await _ble_write_game_cmd("GAME:lobby")

    elif etype == "game.started":
        _ws_game_state = "active"
        _ws_question_phase = None
        _game_pair_result = None
        _game_answered_this_question = False
        _game_end_outcome = None
        _log_game_state("active", "WS game.started")
        if game_mode_active:
            draw_display()
        await _ble_write_game_cmd("GAME:active")

    elif etype == "question.opened":
        _ws_question_id = event.get("questionId")
        _ws_question_phase = "open"
        _game_pair_result = None
        _game_answered_this_question = False
        _log_game_state(
            "question_open",
            f"WS question.opened questionId={_ws_question_id}",
        )
        if game_mode_active:
            draw_display()
        await _ble_write_game_cmd("GAME:question_open")

    elif etype == "question.closed":
        _ws_question_id = None
        _ws_question_phase = "closed"
        _game_pair_result = None  # LCD → white 2×2; answered flag kept for skip
        _log_game_state("question_closed", "WS question.closed")
        if game_mode_active:
            draw_display()
        await _ble_write_game_cmd("GAME:question_close")

    elif etype == "game.ended":
        _ws_game_state  = "completed"
        _ws_question_id = None
        _ws_question_phase = None
        _game_pair_result = None
        _game_answered_this_question = False
        # Prefer winner/loser when enriched fields arrive (Step 8); else generic end.
        if "isWinner" in event:
            if event.get("isWinner"):
                _game_end_outcome = "winner"
                _log_game_state(
                    "winner",
                    f"WS game.ended rank={event.get('rank')} score={event.get('score')}",
                )
                if game_mode_active:
                    draw_display()
                await _ble_write_game_cmd("GAME:winner")
                _start_game_outcome_animation(True)
            else:
                _game_end_outcome = "loser"
                _log_game_state(
                    "loser",
                    f"WS game.ended rank={event.get('rank')} score={event.get('score')}",
                )
                if game_mode_active:
                    draw_display()
                await _ble_write_game_cmd("GAME:loser")
                _start_game_outcome_animation(False)
        else:
            _game_end_outcome = "ended"
            _log_game_state("game_ended", "WS game.ended")
            if game_mode_active:
                draw_display()
            await _ble_write_game_cmd("GAME:ended")

    elif etype == "question.result":
        results = event.get("results") or []
        pair_result = next(
            (r for r in results if r.get("pairName") == PAIR_NAME),
            None,
        )
        is_correct = bool(pair_result and pair_result.get("isCorrect"))
        slot = pair_result.get("slotLabel") if pair_result else None
        await _apply_pair_answer(
            is_correct,
            f"WS question.result slotLabel={slot!r}",
        )


async def _ws_connect_loop():
    """Persistent WebSocket client — runs for the lifetime of the process.

    Connects to the server, sends controller.hello, then processes events.
    Reconnects with exponential backoff on any disconnect or error.
    """
    global _ws_connected
    if not _WS_URL:
        print("[WS] _WS_URL is empty — WebSocket client disabled", flush=True)
        return
    import json
    try:
        import websockets as _ws_lib
    except ImportError:
        print(
            "[WS] 'websockets' library not found — install with: "
            "pip3 install websockets --break-system-packages",
            flush=True,
        )
        return

    backoff = _WS_BACKOFF_MIN_S
    while True:
        try:
            uri = f"{_WS_URL}/ws"
            print(f"[WS] connecting to {uri}", flush=True)
            async with _ws_lib.connect(uri, ping_interval=None) as ws:
                _ws_connected = True
                backoff = _WS_BACKOFF_MIN_S   # reset on successful connect
                print("[WS] connected — sending controller.hello", flush=True)
                hello = {
                    "type":              "controller.hello",
                    "pairName":          PAIR_NAME,
                    "controllerId":      CONTROLLER_ID,
                    "controllerVersion": _CONTROLLER_VERSION,
                    "picoVersion":       _pico_version,
                    "token":             None,
                }
                await ws.send(json.dumps(hello))
                # Server welcome is a lightweight ack; load the authoritative
                # pair binding so lobby/join state is correct even if we missed
                # game.opened while disconnected.
                _poll_pair_binding()
                async for raw in ws:
                    try:
                        event = json.loads(raw)
                    except Exception:
                        continue
                    await _ws_handle_event(event)
        except Exception as exc:
            print(
                f"[WS] disconnected: {exc!r}; retry in {backoff:.0f}s",
                flush=True,
            )
        finally:
            _ws_connected = False
        await asyncio.sleep(backoff)
        backoff = min(backoff * 2, _WS_BACKOFF_MAX_S)


_last_status_liveness_post = 0.0
# POST /api/status while connected at least this often so the dashboard can detect power loss.
STATUS_LIVENESS_POST_S = 40.0


def _poll_pair_binding():
    """Fetch GET /api/pairs/:pairName and apply the snapshot as a welcome event.

    Used as the HTTP fallback when the WebSocket is unavailable.
    Runs in a daemon API thread (via post_to_server pattern) so it never
    blocks the asyncio loop; the event is dispatched back via run_coroutine_threadsafe.
    """
    def _fetch():
        import json as _json
        data = fetch_from_server(f"/api/pairs/{PAIR_NAME}")
        if not isinstance(data, dict):
            return
        synthetic_event = {
            "type":           "controller.welcome",
            "gameId":         data.get("gameId"),
            "state":          data.get("state"),
            "joined":         data.get("joined", False),
            "openQuestionId": data.get("openQuestionId"),
        }
        if ble_event_loop and ble_event_loop.is_running():
            asyncio.run_coroutine_threadsafe(
                _ws_handle_event(synthetic_event), ble_event_loop
            )
    threading.Thread(target=_fetch, daemon=True).start()


async def _heartbeat_loop(interval_s: float = 5.0):
    """Periodically write a STATUS ping to detect dropped connections quickly.

    The Pico firmware should silently ignore STATUS messages so they do not
    trigger unintended display changes.

    Also POST ``connected`` to the emoji server on an interval so the UI can
    mark the link offline when the Pi or Pico stops without a disconnect POST.

    When the WebSocket is down, also polls GET /api/pairs/:pairName every
    _WS_FALLBACK_POLL_S seconds so the game state stays fresh.
    """
    global _last_status_liveness_post, _last_ws_fallback_poll
    while True:
        await asyncio.sleep(interval_s)
        if ble_controller.client and ble_controller.client.is_connected:
            try:
                await ble_controller.client.write_gatt_char(UART_RX_CHAR_UUID, b"STATUS")
            except Exception:
                # The disconnected_callback will handle the clean-up;
                # swallow the exception here to keep the loop alive.
                pass
            nowm = time.monotonic()
            if nowm - _last_status_liveness_post >= STATUS_LIVENESS_POST_S:
                _last_status_liveness_post = nowm
                print("[BLE] liveness — queueing POST /api/status connected", flush=True)
                post_to_server("/api/status", _status_payload("connected"))
        # HTTP fallback: poll pair binding when WS is not connected.
        if not _ws_connected:
            nowm = time.monotonic()
            if nowm - _last_ws_fallback_poll >= _WS_FALLBACK_POLL_S:
                _last_ws_fallback_poll = nowm
                print("[WS] fallback — polling GET /api/pairs", flush=True)
                _poll_pair_binding()

# Initialize GPIO before LCD initialization to ensure lgpio allocation works
# LCD_Config.GPIO_Init() will set up the specific pins with initial values
# to avoid the "GPIO not allocated" error with lgpio backend
try:
    GPIO.setmode(GPIO.BCM)
    GPIO.setwarnings(False)
except:
    pass  # Ignore if already set

# 240x240 display with hardware SPI:
disp = LCD_1in44.LCD()
Lcd_ScanDir = LCD_1in44.SCAN_DIR_DFT  #SCAN_DIR_DFT = D2U_L2R
disp.LCD_Init(Lcd_ScanDir)
disp.LCD_Clear()

# Create blank image for drawing.
# Make sure to create image with mode '1' for 1-bit color.
image = Image.new('RGB', (disp.width, disp.height))

# Get drawing object to draw on image.
draw = ImageDraw.Draw(image)

# Draw a black filled box to clear the image.
draw.rectangle((0,0,disp.width,disp.height), outline=0, fill=0)
disp.LCD_ShowImage(image,0,0)

# === State Machine Variables ===
menu = 0  # Main menu selection (0-3)
pos = 0   # Positive selection (left side emojis)
neg = 0   # Negative selection (right side emojis)
state = "none"  # State: "none", "start", "choosing"
is_winking = False  # Flag to control winking animation
is_animating = False  # Flag to control main emoji animation
animation_running = False  # Flag to prevent multiple animation threads
stop_animation = False  # Flag to interrupt procedural animations
# After confirm: True = selected emoji fills the whole LCD; KEY2 exits to the
# menu + status layout (top menu, bottom emoji, BLE/battery indicators).
fullscreen_mode = False

# Previous state tracking for emoji toggling
prev_menu = 0
prev_pos = 0
prev_neg = 0
prev_state = "none"  # or "done"

# === NFC Mode State ===
# Active when the user has selected menu 3 pos 4 (NFC pos) or neg 4 (NFC neg).
nfc_mode_active = False
nfc_last_result = None       # None, "circle", or "x" / "unknown"
nfc_last_card_name = ""      # human-readable name from NFC_CARD_MAP

# === Menu Items ===
menu_items = ["Emojis", "Animations", "Characters", "Other"]

# === Button State Tracking ===
button_states = {
    'up': True,
    'down': True,
    'left': True,
    'right': True,
    'center': True,
    'key1': True,
    'key2': True,
    'key3': True
}

# === Helper Functions ===

def draw_centered_text(draw, text, y_position, font, max_width, text_color="white"):
    try:
        bbox = draw.textbbox((0, 0), text, font=font)
        text_width = bbox[2] - bbox[0]
        text_height = bbox[3] - bbox[1]
    except AttributeError:
        text_width, text_height = draw.textsize(text, font=font)
    
    x_position = (max_width - text_width) // 2
    draw.text((x_position, y_position), text, font=font, fill=text_color)

def draw_menu_row(draw, text, y_position, font, is_selected=False):
    row_height = 14
    row_y = y_position
    
    if is_selected:
        bg_width = 80  # Fixed width for selection background
        bg_x = 24
        draw.rectangle((bg_x, row_y, bg_x + bg_width, row_y + row_height), fill="white")
        draw_centered_text(draw, text, row_y + 2, font, 128, "black")
    else:
        draw_centered_text(draw, text, row_y + 2, font, 128, "white")

def _display_selection():
    """Return (menu, pos, neg) for the main emoji.

    Prefers the live selection; after confirm the code clears pos/neg while
    leaving prev_* set, so fall back to the last confirmed choice.
    """
    if pos > 0 or neg > 0:
        return menu, pos, neg
    if prev_state == "done" and (prev_pos > 0 or prev_neg > 0):
        return prev_menu, prev_pos, prev_neg
    return menu, pos, neg


def get_main_emoji():
    """Get the main emoji matrix based on current menu, pos, and neg selection"""
    # Game mode — Platform icon glyphs (lobby / ? / correct / …).
    if game_mode_active:
        return _game_mode_display_matrix()

    # NFC mode overrides the main emoji regardless of current nav state
    if nfc_mode_active:
        if nfc_last_result == "circle":
            return others_circle_matrix
        elif nfc_last_result in ("x", "unknown"):
            return others_x_matrix
        else:
            return question_mark_matrix

    sel_menu, sel_pos, sel_neg = _display_selection()

    if sel_menu == 0:  # Emojis menu
        if sel_pos == 1:
            return regular_matrix
        elif sel_pos == 2:
            return wry_matrix
        elif sel_pos == 3:
            return happy_matrix
        elif sel_pos == 4:
            return heart_eyes_matrix
        elif sel_neg == 1:
            return thick_lips_matrix
        elif sel_neg == 2:
            return sad_wry_matrix
        elif sel_neg == 3:
            return sad_matrix
        elif sel_neg == 4:
            return crossbone_eyes_matrix

    elif sel_menu == 1:  # Animations menu
        if sel_pos == 1:
            return fireworks_animation.preview
        elif sel_pos == 2:
            return circular_rainbow_preview_matrix
        elif sel_pos == 3:
            return chakana_matrix
        elif sel_pos == 4:
            return heart_matrix
        elif sel_neg == 1:
            return rain_animation.preview

    elif sel_menu == 2:  # Characters menu
        if sel_pos == 1:
            return finn_matrix
        elif sel_pos == 2:
            return pikachu_matrix
        elif sel_pos == 3:
            return crab_matrix
        elif sel_pos == 4:
            return frog_matrix
        elif sel_neg == 1:
            return bald_matrix
        elif sel_neg == 2:
            return surprise_matrix
        elif sel_neg == 3:
            return green_monster_matrix
        elif sel_neg == 4:
            return angry_matrix

    elif sel_menu == 3:  # Others menu
        if sel_pos == 1:
            return others_circle_matrix
        elif sel_pos == 2:
            return others_yes_matrix
        elif sel_pos == 3:
            return others_somi_matrix
        elif sel_pos == 4:
            return game_mode_matrix   # game mode slot
        elif sel_neg == 1:
            return others_x_matrix
        elif sel_neg == 2:
            return others_no_matrix
        elif sel_neg == 4:
            return question_mark_matrix

    # Default to regular smiley for other menus
    return smiley_matrix

def get_main_emoji_animation():
    """Get the animation state of the main emoji"""
    # Game mode — no wink animation; keep the Platform icon glyph steady.
    if game_mode_active:
        return _game_mode_display_matrix()

    sel_menu, sel_pos, sel_neg = _display_selection()

    if sel_menu == 0:  # Emojis menu
        if sel_pos == 1:
            return regular_wink_matrix
        elif sel_pos == 2:
            return wry_wink_matrix
        elif sel_pos == 3:
            return happy_wink_matrix
        elif sel_pos == 4:
            return heart_eyes_wink_matrix
        elif sel_neg == 1:
            return thick_lips_wink_matrix
        elif sel_neg == 2:
            return sad_wry_wink_matrix
        elif sel_neg == 3:
            return sad_wink_matrix
        elif sel_neg == 4:
            return crossbone_eyes_wink_matrix

    elif sel_menu == 1:  # Animations menu - circular rainbow, chakana, heart bounce previews
        if sel_pos == 2:
            return circular_rainbow_wink_matrix
        elif sel_pos == 3:
            return chakana_matrix
        elif sel_pos == 4:
            return heart_bounce_matrix

    elif sel_menu == 2:  # Characters menu animations (use character-specific matrices)
        if sel_pos == 1:
            return finn_wink_matrix
        elif sel_pos == 2:
            return pikachu_wink_matrix
        elif sel_pos == 3:
            return crab_wink_matrix
        elif sel_pos == 4:
            return frog_wink_matrix
        elif sel_neg == 1:
            return bald_wink_matrix
        elif sel_neg == 2:
            return surprise_wink_matrix
        elif sel_neg == 3:
            return green_monster_wink_matrix
        elif sel_neg == 4:
            return angry_wink_matrix

    elif sel_menu == 3:  # Others menu previews in animation phase
        if sel_pos == 1:
            return others_circle_matrix
        elif sel_pos == 2:
            return others_yes_matrix
        elif sel_pos == 3:
            return others_somi_matrix
        elif sel_pos == 4:
            return game_mode_matrix       # game mode slot — no animation
        elif sel_neg == 1:
            return others_x_matrix
        elif sel_neg == 2:
            return others_no_matrix
        elif sel_neg == 4:
            return question_mark_matrix

    # Default to wink smiley for other menus
    return smiley_wink_matrix

def get_left_side_emojis():
    """Get the left side emoji matrices for menu 0 (Emojis) and menu 1 (Animations)"""
    if menu == 0:
        return [regular_matrix, wry_matrix, happy_matrix, heart_eyes_matrix]
    elif menu == 1:
        return [
            fireworks_animation.preview,
            circular_rainbow_preview_matrix,
            chakana_matrix,
            heart_matrix,
        ]
    elif menu == 2:
        # Finn, Pikachu, Crab, and Frog in the four character slots.
        return [finn_matrix, pikachu_matrix, crab_matrix, frog_matrix]
    elif menu == 3:
        # pos 4 (index 3) is now the game mode entry — show 'G' glyph.
        return [others_circle_matrix, others_yes_matrix, others_somi_matrix, game_mode_matrix]
    else:
        return [smiley_matrix, smiley_matrix, smiley_matrix, smiley_matrix]

def get_right_side_emojis():
    """Get the right side emoji matrices for menu 0 (Emojis), menu 1 (Animations), and menu 2 (Characters)"""
    if menu == 0:
        return [
            thick_lips_matrix,
            sad_wry_matrix,
            sad_matrix,
            crossbone_eyes_matrix,
        ]
    elif menu == 1:
        return [rain_animation.preview, smiley_matrix, smiley_matrix, smiley_matrix]
    elif menu == 2:
        # Bald, Surprise, Green Monster, Angry — matches Pico menu 2 negatives.
        return [
            bald_matrix,
            surprise_matrix,
            green_monster_matrix,
            angry_matrix,
        ]
    elif menu == 3:
        return [others_x_matrix, others_no_matrix, smiley_matrix, question_mark_matrix]
    else:
        return [smiley_matrix, smiley_matrix, smiley_matrix, smiley_matrix]

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
    if pos < 1:
        pos = 4

def check_neg():
    global neg
    if neg > 4:
        neg = 1
    if neg < 1:
        neg = 4

def reset_state():
    """Save current state as previous and reset to initial state"""
    global state, menu, pos, neg, prev_state, prev_menu, prev_pos, prev_neg
    prev_state = "done"
    prev_menu = menu
    prev_pos = pos
    prev_neg = neg
    state = "none"
    menu = 0
    pos = 0
    neg = 0

def reset_prev():
    """Clear previous state tracking"""
    global prev_state, prev_menu, prev_pos, prev_neg
    global nfc_mode_active, nfc_last_result, nfc_last_card_name
    global game_mode_active, fullscreen_mode
    prev_state = "none"
    prev_menu = 0
    prev_pos = 0
    prev_neg = 0
    nfc_mode_active = False
    nfc_last_result = None
    nfc_last_card_name = ""
    game_mode_active = False
    fullscreen_mode = False

def check_animation_interruption():
    """Check if user wants to interrupt the current animation"""
    global stop_animation
    try:
        key1_pressed = disp.digital_read(disp.GPIO_KEY1_PIN) == 0
        key3_pressed = disp.digital_read(disp.GPIO_KEY3_PIN) == 0
        
        # If opposite button is pressed, signal interruption
        if (menu == 1 and pos > 0 and key3_pressed) or (menu == 1 and neg > 0 and key1_pressed):
            stop_animation = True
            return True
        return False
    except:
        # If GPIO read fails, don't interrupt
        return False

def send_emoji_to_pico(menu_val, pos_val, neg_val):
    """Send emoji selection to Pico via BLE"""
    global ble_event_loop
    
    if not ble_event_loop:
        print("BLE not initialized yet — cannot send to Pico or /api/emoji", flush=True)
        return
    
    def send_command():
        try:
            # Use the existing event loop
            future = asyncio.run_coroutine_threadsafe(
                ble_controller.send_emoji_command(menu_val, pos_val, neg_val),
                ble_event_loop
            )
            ok = future.result(timeout=5)
            print(f"[BLE] send_emoji_command finished ok={ok} (False means no BLE write / no API)", flush=True)
        except Exception as e:
            print(f"Error sending to Pico: {e}", flush=True)
    
    # Send in a separate thread to avoid blocking the main loop
    send_thread = threading.Thread(target=send_command)
    send_thread.daemon = True
    send_thread.start()

def start_procedural_animation():
    """Start a procedural animation (fireworks or rain) with interruption support"""
    global animation_running, stop_animation, prev_menu, prev_pos, prev_neg, prev_state
    global state, menu, pos, neg, fullscreen_mode
    
    if animation_running:
        return
    
    animation_running = True
    stop_animation = False
    fullscreen_mode = True
    
    # Save current selection
    prev_state = "done"
    prev_menu = menu
    prev_pos = pos
    prev_neg = neg
    
    # Send emoji command to Pico
    send_emoji_to_pico(menu, pos, neg)
    
    # Clear the display for animation
    draw.rectangle((0, 0, disp.width, disp.height), outline=0, fill=0)
    
    # Full-screen selected mode: 8×8 matrix at scale 16 fills the 128×128 LCD.
    scale = 16
    start_x = 0
    start_y = 0
    
    interrupted = False
    
    # Run the appropriate animation
    if menu == 1 and pos == 1:
        # Fireworks animation
        interrupted = fw_anim_func(draw, image, disp, scale, start_x, start_y, 
                                   iters=10, interruption_check=check_animation_interruption)
    elif menu == 1 and neg == 1:
        # Rain animation
        interrupted = rain_anim_func(draw, image, disp, scale, start_x, start_y, 
                                    iters=200, density=1, interruption_check=check_animation_interruption)
    
    # Handle interruption - toggle to opposite animation
    if interrupted and stop_animation:
        # User pressed opposite button - toggle pos/neg
        if prev_pos > 0:
            neg = prev_pos
            pos = 0
            menu = prev_menu
        elif prev_neg > 0:
            pos = prev_neg
            neg = 0
            menu = prev_menu
        
        # Reset flags
        animation_running = False
        stop_animation = False
        
        # Start the opposite animation in a new thread to avoid recursion
        animation_thread = threading.Thread(target=start_procedural_animation)
        animation_thread.daemon = True
        animation_thread.start()
        return
    
    # Animation completed normally - keep confirmed selection via prev_*; clear
    # live pos/neg so menu highlights are off while fullscreen_mode stays on.
    state = "none"
    pos = 0
    neg = 0
    animation_running = False
    stop_animation = False
    draw_display()

def emoji_two_part_animation():
    """Function to handle two-part emoji animation: normal state then animation state"""
    global is_winking, is_animating, animation_running
    if animation_running:
        return
    animation_running = True
    
    # Send emoji command to Pico
    send_emoji_to_pico(menu, pos, neg)
    
    # First show the normal emoji state
    is_winking = False
    is_animating = False
    draw_display()
    time.sleep(0.5)  # Show normal state for 0.5 seconds
    
    # Then show the animation state
    if menu == 1 and pos == 4:  # Heart bounce (menu 1, pos 4)
        is_animating = True
        is_winking = False
    else:  # Wink animation for other emojis
        is_winking = True
        is_animating = False
    
    draw_display()
    time.sleep(1.0)  # Show animation for 1 second
    
    # Return to normal state
    is_winking = False
    is_animating = False
    draw_display()
    animation_running = False

def start_emoji_animation():
    """Start the appropriate animation based on menu selection"""
    global prev_menu, prev_pos, prev_neg, prev_state, menu, pos, neg, state
    global nfc_mode_active, nfc_last_result, nfc_last_card_name
    global game_mode_active, fullscreen_mode

    # Game mode: menu 3, pos 4, neg 0 — full-screen live game status display.
    # KEY2 joins when a lobby is waiting; joystick navigation exits game mode.
    if menu == 3 and pos == 4 and neg == 0:
        prev_state = "done"
        prev_menu  = menu
        prev_pos   = pos
        prev_neg   = neg
        game_mode_active = True
        fullscreen_mode = True
        print("[GAME] entering game mode (fullscreen)", flush=True)
        state = "none"
        pos   = 0
        neg   = 0
        draw_display()
        # Sync Pico with the current server-known game state now that game mode
        # is active (e.g. game was already active when the user selected this slot).
        if ble_event_loop and ble_event_loop.is_running():
            asyncio.run_coroutine_threadsafe(
                _apply_game_state_to_display(), ble_event_loop
            )
        return

    # NFC mode: menu 3, neg 4 only (pos 4 is now game mode above).
    # Status layout keeps card-name labels visible when a tag is scanned.
    if menu == 3 and neg == 4:
        prev_state = "done"
        prev_menu = menu
        prev_pos = pos
        prev_neg = neg
        nfc_mode_active = True
        nfc_last_result = None
        nfc_last_card_name = ""
        fullscreen_mode = False
        print(f"[NFC] entering NFC mode (menu={menu} pos={pos} neg={neg})", flush=True)
        send_emoji_to_pico(menu, pos, neg)
        state = "none"
        pos = 0
        neg = 0
        draw_display()
        return

    # Check if this is a procedural animation (menu 1)
    if menu == 1 and (pos == 1 or neg == 1):
        start_procedural_animation()
    else:
        # Regular two-part emoji animation — enter full-screen selected mode
        prev_state = "done"
        prev_menu = menu
        prev_pos = pos
        prev_neg = neg
        fullscreen_mode = True
        
        # Run the animation
        emoji_two_part_animation()
        
        # Reset to none state after animation completes (no menu selection).
        # Keep fullscreen_mode; prev_* drives the main emoji via _display_selection().
        state = "none"
        pos = 0
        neg = 0
        draw_display()

def draw_connection_indicator(clear_area=True):
    """Draw the BLE connection status indicator in the lower left corner
    
    Args:
        clear_area: If True, clear the indicator area before drawing (for standalone updates)
    """
    global ble_connection_status
    
    # Position in lower left corner (small scale for compact indicator)
    indicator_scale = 2
    indicator_size = indicator_scale * 8
    indicator_x = 2
    indicator_y = disp.height - indicator_size - 2  # 2 pixels from bottom
    
    # Clear the indicator area if requested (for standalone updates)
    if clear_area:
        draw.rectangle((indicator_x, indicator_y, indicator_x + indicator_size, indicator_y + indicator_size), 
                      outline=0, fill=0)
    
    # Select the appropriate matrix based on connection status
    if ble_connection_status in ("scanning", "connecting"):
        indicator_matrix = connecting_matrix
    elif ble_connection_status == "connected":
        indicator_matrix = connected_matrix
    else:  # "idle" or "disconnected"
        indicator_matrix = not_connected_matrix
    
    # Draw the indicator
    draw_emoji(draw, indicator_matrix, color_map, indicator_scale, indicator_x, indicator_y)


def draw_battery_indicator():
    """Draw a mobile-style battery indicator in two rows at the bottom-right.

    Row 1 (upper): percentage text, right-aligned.
    Row 2 (lower): battery body + nub, right-aligned.

    No-op when INA219 data is not yet available or the HAT is absent.

    Layout (display is 128×128, main emoji occupies x=36..92, y=72..128):
      Pct text  [right-aligned, y≈108..116]  — clear of emoji
      Batt icon [x=104..128,   y=118..126]  — clear of emoji
    """
    pct = _battery_percent
    if pct is None:
        return

    margin  = 2    # pixels from right/bottom edges
    body_w  = 20
    body_h  = 8
    nub_w   = 2
    nub_h   = 4
    row_gap = 2    # vertical gap between text row and icon row

    # --- Battery icon row (bottom) ---
    # Body left edge so that body + nub end at (disp.width - margin).
    batt_x = disp.width - margin - nub_w - body_w   # = 104
    batt_y = disp.height - margin - body_h           # = 118

    # --- Percentage text row (above icon) ---
    pct_text = f"{pct}%"
    try:
        bbox   = draw.textbbox((0, 0), pct_text, font=font)
        text_w = bbox[2] - bbox[0]
        text_h = bbox[3] - bbox[1]
    except AttributeError:
        text_w, text_h = draw.textsize(pct_text, font=font)
    text_x = disp.width - margin - text_w            # right-aligned
    text_y = batt_y - row_gap - text_h               # row above battery icon

    # Colour: green > 50 %, amber 20–50 %, red < 20 %
    if pct > 50:
        fill_color = (0, 180, 0)
    elif pct > 20:
        fill_color = (220, 160, 0)
    else:
        fill_color = (200, 0, 0)

    # Percentage label
    draw.text((text_x, text_y), pct_text, font=font, fill="white")

    # Battery body outline
    draw.rectangle(
        [batt_x, batt_y, batt_x + body_w, batt_y + body_h],
        outline="white", fill=0,
    )
    # Terminal nub on the right
    nub_y = batt_y + (body_h - nub_h) // 2
    draw.rectangle(
        [batt_x + body_w, nub_y, batt_x + body_w + nub_w, nub_y + nub_h],
        fill="white",
    )
    # Charge-level fill bar (inside the outline, coloured by level)
    fill_w = max(0, int((body_w - 2) * pct / 100))
    if fill_w > 0:
        draw.rectangle(
            [batt_x + 1, batt_y + 1, batt_x + 1 + fill_w, batt_y + body_h - 1],
            fill=fill_color,
        )


def _game_status_label():
    """Optional secondary text over the Platform icon glyph.

    Most states are glyph-only (matching Pico). Keep an action hint for lobby
    join, and GAME OVER when the game ends without a winner/loser enrichment.
    """
    if not game_mode_active:
        return None, None
    if _ws_game_state == "lobby" and not _ws_joined:
        return "JOIN? KEY2", "yellow"
    if _game_end_outcome == "ended" or (
        _ws_game_state == "completed" and _game_end_outcome is None
    ):
        return "GAME OVER", (200, 0, 0)
    return None, None


def draw_display():
    """Draw the complete display"""
    # Clear screen
    draw.rectangle((0,0,disp.width,disp.height), outline=0, fill=0)

    # Get the appropriate main emoji
    if is_winking or is_animating:
        current_emoji = get_main_emoji_animation()
    else:
        current_emoji = get_main_emoji()

    # === Full-screen selected mode ===
    # NFC keeps the status layout so card-name labels stay visible.
    if fullscreen_mode and not nfc_mode_active:
        if game_mode_active:
            # Platform icon glyph fills most of the LCD; optional status strip
            # (e.g. JOIN? KEY2) overlays the top when an action is required.
            scale = 14
            emoji_width = scale * 8
            emoji_height = scale * 8
            start_x = (disp.width - emoji_width) // 2
            start_y = (disp.height - emoji_height) // 2
            draw_emoji(draw, current_emoji, color_map, scale, start_x, start_y)

            status_text, status_color = _game_status_label()
            if status_text:
                draw.rectangle((0, 0, disp.width, 16), outline=0, fill=0)
                draw_centered_text(draw, status_text, 3, font, disp.width, status_color)

            draw_connection_indicator(clear_area=False)
            draw_battery_indicator()
        else:
            scale = 16  # 8×16 = 128 — fills the LCD
            draw_emoji(draw, current_emoji, color_map, scale, 0, 0)

        disp.LCD_ShowImage(image, 0, 0)
        return

    # === Main Emoji (bottom half) ===
    scale = 7
    emoji_width = scale * 8
    emoji_height = scale * 8
    start_x = (disp.width - emoji_width) // 2
    start_y = 64 + (64 - emoji_height)

    draw_emoji(draw, current_emoji, color_map, scale, start_x, start_y)
    
    # === Left Side Emojis (with selection) ===
    left_emoji_y = [1, 16, 31, 46]
    left_emojis = get_left_side_emojis()
    for i, y_pos in enumerate(left_emoji_y):
        show_selection = (state == "choosing" and pos == i + 1)
        draw_emoji(draw, left_emojis[i], color_map, 1.5, 5, y_pos, show_selection)
    
    # === Right Side Emojis (with selection) ===
    right_emoji_y = [1, 16, 31, 46]
    right_emojis = get_right_side_emojis()
    for i, y_pos in enumerate(right_emoji_y):
        show_selection = (state == "choosing" and neg == i + 1)
        draw_emoji(draw, right_emojis[i], color_map, 1.5, 110, y_pos, show_selection)
    
    # === Menu Text ===
    text_y_positions = [1, 16, 31, 46]
    for i, item in enumerate(menu_items):
        # Show main menu selection in both "start" and "choosing" states
        is_selected = (i == menu and (state == "start" or state == "choosing"))
        draw_menu_row(draw, item, text_y_positions[i], font, is_selected)
    
    # === NFC Card Name (shown between menu area and main emoji when a card is scanned) ===
    if nfc_mode_active and nfc_last_card_name:
        name_color = (0, 160, 255) if nfc_last_result == "circle" else (220, 60, 60)
        draw_centered_text(draw, nfc_last_card_name, 57, font, disp.width, name_color)

    # === Game mode status text (menu + status layout) ===
    status_text, status_color = _game_status_label()
    if status_text:
        draw_centered_text(draw, status_text, 57, font, disp.width, status_color)

    # === BLE Connection Status Indicator (lower left) ===
    draw_connection_indicator(clear_area=False)  # Don't clear since we already cleared the whole screen

    # === Battery Indicator (lower left, to the right of BLE icon) ===
    draw_battery_indicator()

    # Update display
    disp.LCD_ShowImage(image,0,0)

# === Load font ===
try:
    font = ImageFont.load_default()
except:
    font = ImageFont.load_default()

# === Initial display ===
draw_display()

print("Emoji OS Zero " + VERSION + " started with BLE Controller functionality")
print(f"[PAIR] strict pairing enabled — PAIR_NAME='{PAIR_NAME}', target='{TARGET_DEVICE_NAME}'")
print("Joystick: Navigate menus")
print("KEY1: Select positive")
print("KEY2: Navigate/confirm; exit full-screen selected mode")
print("KEY3: Select negative")
print("=" * 50)

# === Initialize BLE Connection ===
def init_ble_connection():
    """Initialize BLE connection in a separate thread"""
    global ble_event_loop, ble_connection_thread
    
    def connect():
        global ble_event_loop
        try:
            # Log BT adapter state before touching Bleak so any hardware/driver
            # problem shows up clearly in the log.
            _log_bt_adapter_info()

            # Create a new event loop for this thread
            ble_event_loop = asyncio.new_event_loop()
            asyncio.set_event_loop(ble_event_loop)

            # Start WebSocket client alongside BLE — both share this event loop.
            ble_event_loop.create_task(_ws_connect_loop())

            print("[BLE] startup — queueing POST /api/status", flush=True)
            post_to_server("/api/status", _status_payload("startup"))

            # Load the NFC card mapping from the server (falls back to the
            # built-in map if unreachable). Done here on the BLE thread so the
            # blocking GET never stalls the UI loop.
            load_nfc_card_map()

            async def _initial_connect():
                if await ble_controller.scan_for_device(timeout=5):
                    await ble_controller.connect_to_device()
                else:
                    # No matching badge yet; keep trying so a late-booting Pico
                    # is still picked up automatically.
                    asyncio.create_task(_reconnect())

            ble_event_loop.run_until_complete(_initial_connect())

            # Keep the event loop running
            ble_event_loop.run_forever()
            
        except Exception as e:
            print(f"BLE initialization error: {e}")
    
    # Start BLE connection in background
    ble_connection_thread = threading.Thread(target=connect)
    ble_connection_thread.daemon = True
    ble_connection_thread.start()

# Start BLE connection
init_ble_connection()

try:
    while True:
        # === Read button states ===
        up_pressed = disp.digital_read(disp.GPIO_KEY_UP_PIN) == 0
        down_pressed = disp.digital_read(disp.GPIO_KEY_DOWN_PIN) == 0
        left_pressed = disp.digital_read(disp.GPIO_KEY_LEFT_PIN) == 0
        right_pressed = disp.digital_read(disp.GPIO_KEY_RIGHT_PIN) == 0
        center_pressed = disp.digital_read(disp.GPIO_KEY_PRESS_PIN) == 0
        key1_pressed = disp.digital_read(disp.GPIO_KEY1_PIN) == 0
        key2_pressed = disp.digital_read(disp.GPIO_KEY2_PIN) == 0
        key3_pressed = disp.digital_read(disp.GPIO_KEY3_PIN) == 0
        
        # === Handle UP button ===
        if up_pressed and not button_states['up']:
            reset_prev()  # Clear previous state when navigating
            if state == "none":
                state = "start"
            elif state == "start":
                menu = (menu - 1) % 4
                check_menu()
            elif state == "choosing":
                # In choosing mode, UP/DOWN should cycle through left side emojis (positive)
                pos = (pos - 1) % 5
                if pos == 0:
                    pos = 4
                neg = 0
                check_pos()
            draw_display()
            print('Up - Menu:', menu, 'Pos:', pos, 'Neg:', neg, 'State:', state)
            time.sleep(0.2)
        button_states['up'] = up_pressed
        
        # === Handle DOWN button ===
        if down_pressed and not button_states['down']:
            reset_prev()  # Clear previous state when navigating
            if state == "none":
                state = "start"
            elif state == "start":
                menu = (menu + 1) % 4
                check_menu()
            elif state == "choosing":
                # In choosing mode, UP/DOWN should cycle through left side emojis (positive)
                pos = (pos + 1) % 5
                if pos == 0:
                    pos = 1
                neg = 0
                check_pos()
            draw_display()
            print('Down - Menu:', menu, 'Pos:', pos, 'Neg:', neg, 'State:', state)
            time.sleep(0.2)
        button_states['down'] = down_pressed
        
        # === Handle LEFT button ===
        if left_pressed and not button_states['left']:
            reset_prev()  # Clear previous state when navigating
            if state == "choosing":
                neg = (neg + 1) % 5
                if neg == 0:
                    neg = 1
                pos = 0
                check_neg()
            draw_display()
            print('Left - Negative:', neg, 'State:', state)
            time.sleep(0.2)
        button_states['left'] = left_pressed
        
        # === Handle RIGHT button ===
        if right_pressed and not button_states['right']:
            reset_prev()  # Clear previous state when navigating
            if state == "choosing":
                pos = (pos + 1) % 5
                if pos == 0:
                    pos = 1
                neg = 0
                check_pos()
            draw_display()
            print('Right - Positive:', pos, 'State:', state)
            time.sleep(0.2)
        button_states['right'] = right_pressed
        
        # === Handle CENTER button ===
        if center_pressed and not button_states['center']:
            if state == "start":
                state = "choosing"
                pos = 1
                neg = 0
                draw_display()
            elif state == "choosing":
                # Show selected emoji and trigger appropriate animation
                print(f"Selected: Menu {menu}, Pos {pos}, Neg {neg}")
                # Start animation in a separate thread (owns the next redraw /
                # full-screen transition — avoid flashing the menu layout here)
                animation_thread = threading.Thread(target=start_emoji_animation)
                animation_thread.daemon = True
                animation_thread.start()
            print('Center - State:', state)
            time.sleep(0.2)
        button_states['center'] = center_pressed
        
        # === Handle KEY1 button (Positive) ===
        if key1_pressed and not button_states['key1']:
            print('debug KEY1 - menu:', menu, "pos", pos, "neg", neg, 
                "state", state, "prev_pos", prev_pos, "prev_neg", prev_neg, "prev_state", prev_state)

            # Try toggle or replay previous if available
            if prev_state == "done":
                if prev_neg > 0:
                    # Toggle from previous negative to positive
                    pos = prev_neg
                    neg = 0
                    menu = prev_menu
                    print('KEY1 - Toggle from neg to pos, menu:', menu, "pos", pos, "neg", neg)
                    animation_thread = threading.Thread(target=start_emoji_animation)
                    animation_thread.daemon = True
                    animation_thread.start()
                    time.sleep(0.2)
                    button_states['key1'] = key1_pressed
                    continue
                elif prev_pos > 0:
                    # Replay previous positive
                    pos = prev_pos
                    neg = 0
                    menu = prev_menu
                    print('KEY1 - Replay prev pos, menu:', menu, "pos", pos, "neg", neg)
                    animation_thread = threading.Thread(target=start_emoji_animation)
                    animation_thread.daemon = True
                    animation_thread.start()
                    time.sleep(0.2)
                    button_states['key1'] = key1_pressed
                    continue

            # Fallback to regular logic
            if state == "choosing":
                pos = (pos + 1) % 5
                if pos == 0:
                    pos = 1
                neg = 0
                check_pos()

            elif state == "start":
                state = "choosing"
                pos = 1
                neg = 0

            elif state == "none":
                state = "choosing"
                pos = 1
                neg = 0

            draw_display()
            print('KEY1 - Positive:', pos, 'State:', state)
            time.sleep(0.2)
        button_states['key1'] = key1_pressed
        
        # === Handle KEY2 button (Menu/Confirm) ===
        if key2_pressed and not button_states['key2']:
            # Game mode owns KEY2: join when a lobby is waiting; otherwise stay
            # on the full-screen status view (joystick navigation exits).
            if game_mode_active:
                if _join_pending and _ws_game_id:
                    _join_pending = False
                    _ws_joined    = True
                    post_to_server(
                        f"/api/games/{_ws_game_id}/join",
                        {"pairName": PAIR_NAME, "controllerId": CONTROLLER_ID},
                    )
                    draw_display()   # redraws with "WAITING..." status
                    _log_game_state(
                        "lobby_joined",
                        f"KEY2 join POST gameId={_ws_game_id} pair={PAIR_NAME}",
                    )
                    if ble_event_loop is not None:
                        asyncio.run_coroutine_threadsafe(
                            _ble_write_game_cmd("GAME:lobby_joined"),
                            ble_event_loop,
                        )
                time.sleep(0.2)
                button_states['key2'] = key2_pressed
                continue

            # Full-screen selected mode: KEY2 exits to menu + status layout.
            if fullscreen_mode and not nfc_mode_active:
                fullscreen_mode = False
                draw_display()
                print('KEY2 - Exit fullscreen to status view')
                time.sleep(0.2)
                button_states['key2'] = key2_pressed
                continue

            # Only clear prev when *not* confirming the current choosing
            if state != "choosing":
                reset_prev()

            if state == "start":
                menu = (menu + 1) % 4
                check_menu()
                draw_display()
            elif state == "none":
                state = "start"
                draw_display()
            elif state == "choosing":
                # Don't reset prev here! First record prev, then animate.
                # Animation thread owns the next redraw / full-screen transition.
                print(f"Selected: Menu {menu}, Pos {pos}, Neg {neg}")
                animation_thread = threading.Thread(target=start_emoji_animation)
                animation_thread.daemon = True
                animation_thread.start()
            print('KEY2 - Menu:', menu, 'State:', state)
            time.sleep(0.2)
        button_states['key2'] = key2_pressed
        
        # === Handle KEY3 button (Negative) ===
        if key3_pressed and not button_states['key3']:
            print('debug KEY3 - menu:', menu, "pos", pos, "neg", neg, 
                  "state", state, "prev_pos", prev_pos, "prev_neg", prev_neg, "prev_state", prev_state)

            # First, attempt the "toggle / replay previous" case if just after an animation
            if prev_state == "done":
                if prev_pos > 0:
                    # Toggle from previous positive to negative
                    neg = prev_pos
                    pos = 0
                    menu = prev_menu
                    print('KEY3 - Toggle from pos to neg, menu:', menu, "pos", pos, "neg", neg)
                    animation_thread = threading.Thread(target=start_emoji_animation)
                    animation_thread.daemon = True
                    animation_thread.start()
                    # We do NOT reset prev_state here, so it doesn't fall through to other branches
                    time.sleep(0.2)
                    button_states['key3'] = key3_pressed
                    continue
                elif prev_neg > 0:
                    # Replay previous negative
                    neg = prev_neg
                    pos = 0
                    menu = prev_menu
                    print('KEY3 - Replay prev neg, menu:', menu, "pos", pos, "neg", neg)
                    animation_thread = threading.Thread(target=start_emoji_animation)
                    animation_thread.daemon = True
                    animation_thread.start()
                    time.sleep(0.2)
                    button_states['key3'] = key3_pressed
                    continue

            # If we didn't take the toggle/replay branch, do the normal logic
            if state == "choosing":
                neg = (neg + 1) % 5
                if neg == 0:
                    neg = 1
                pos = 0
                check_neg()

            elif state == "start":
                state = "choosing"
                neg = 1
                pos = 0

            elif state == "none":
                state = "choosing"
                neg = 1
                pos = 0

            draw_display()
            print('KEY3 - Negative:', neg, 'State:', state)
            time.sleep(0.2)
        button_states['key3'] = key3_pressed
        time.sleep(0.1)

except KeyboardInterrupt:
    print("Exiting...")
    # Clean up BLE connection
    if ble_event_loop:
        try:
            # Schedule disconnect and stop the loop
            ble_event_loop.call_soon_threadsafe(
                lambda: asyncio.create_task(ble_controller.disconnect())
            )
            # Give it a moment to disconnect
            time.sleep(1)
            ble_event_loop.stop()
        except:
            pass
    # Clean up GPIO pins
    try:
        GPIO.cleanup()
    except:
        pass
    try:
        disp.module_exit()
    except:
        pass
