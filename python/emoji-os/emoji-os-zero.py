# -*- coding:utf-8 -*-
# Emoji OS Zero
VERSION = " v0.8.1"
# Normalized version string sent to the server (strip leading space / 'v').
_CONTROLLER_VERSION = VERSION.strip().lstrip("v")
# Pico badge version from the primary roster link's PAIR_OK:<version> reply.
# Per-badge versions live on BadgeLink.pico_version. "unknown" when the Pico
# replies a bare PAIR_OK (pre-v0.3.2) or when no pairing has happened yet.
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
import socket
import requests
from datetime import datetime, timezone
from urllib.parse import urlparse
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
SERVER_URL = "http://192.168.68.52:3000"
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

# === Network Monitoring ===
# This checks whether Linux has a usable route to the configured emoji server.
# It does not send any data; connecting a UDP socket only asks the kernel which
# local interface/address it would use.
_network_connected = False
_network_indicator_dirty = True
_NETWORK_CHECK_INTERVAL_S = 5.0


def _has_network_route():
    """Return True when a non-loopback route to SERVER_URL is available."""
    target_host = "1.1.1.1"
    target_port = 53
    if SERVER_URL:
        try:
            parsed = urlparse(SERVER_URL)
            if parsed.hostname:
                target_host = parsed.hostname
            if parsed.port:
                target_port = parsed.port
            elif parsed.scheme == "https":
                target_port = 443
            else:
                target_port = 80
        except Exception:
            pass

    probe = None
    try:
        probe = socket.socket(socket.AF_INET, socket.SOCK_DGRAM)
        probe.settimeout(1.0)
        probe.connect((target_host, target_port))
        local_ip = probe.getsockname()[0]
        return local_ip not in ("0.0.0.0", "127.0.0.1")
    except Exception:
        return False
    finally:
        if probe is not None:
            try:
                probe.close()
            except Exception:
                pass


def _network_monitor():
    """Poll network routing and flag the display when its state changes."""
    global _network_connected, _network_indicator_dirty
    previous = None
    while True:
        connected = _has_network_route()
        if connected != previous:
            _network_connected = connected
            _network_indicator_dirty = True
            label = "connected" if connected else "not connected"
            print(f"[NET] network {label}", flush=True)
            previous = connected
        time.sleep(_NETWORK_CHECK_INTERVAL_S)


threading.Thread(target=_network_monitor, daemon=True).start()

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
_ws_game_state    = None   # "ready"|"lobby"|"active"|"completed"|None
_ws_question_id   = None   # str | None — currently open question
_ws_joined        = False  # True once the station has joined (KEY1 or snapshot)
# Each roster badge is its own player. Badges the server has marked joined
# (KEY1 joins every connected badge; later badges auto-join on connect).
_joined_badges    = set()
_join_pending     = False  # True after game.opened arrives; cleared by KEY1 join
_ws_connected     = False  # True while the WS socket is open
# Question phase within an active game (drives Platform icon glyphs).
# None = game active before round 1; "open" / "closed" between rounds;
# "complete" after the final round closes but before the referee ends the game.
_ws_question_phase = None  # None | "open" | "closed" | "complete"
# Per-badge answer shown until question_closed (immediate guess feedback).
_badge_results = {}        # badgeName -> "correct" | "wrong"
# Badges that have shown correct/wrong for the open question (scan or
# question.result). Survives question.closed so a late question.result does not
# re-animate over the white 2×2 "Question closed" glyph.
_badges_answered = set()
# Station response while between questions (only the Zero has buttons; the
# readiness POST applies it to every joined badge): None = prompt, True =
# ready, False = needs more time.
_next_question_ready = None
# End-of-game outcome per badge (Pico glyph) and for the station LCD: winner
# when any badge won, loser otherwise, ended without enrichment.
_badge_end_outcomes = {}   # badgeName -> "winner" | "loser"
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
    "rounds_complete": "All rounds complete",
    "ready_prompt": "Ready for next question?",
    "ready": "Ready for next question",
    "wait": "Needs more time",
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
    "GAME:rounds_complete": "rounds_complete",
    "GAME:ready_prompt": "ready_prompt",
    "GAME:ready": "ready",
    "GAME:wait": "wait",
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
# PAIR_NAME is this controller's station id (bind / join / score).
# BADGE_NAMES is the roster of Pico PAIR_NAME values this Zero may connect to.
# Each Pico keeps its own pair_config.py; that name must appear in BADGE_NAMES.
# If BADGE_NAMES is omitted or empty, the roster is [PAIR_NAME] (Mode 1).
#
# pair_config.py must live in the directory ABOVE the repo root, e.g.
#   /home/<user>/repos/pair_config.py
# given this script lives at
#   /home/<user>/repos/rainbow-connection/python/emoji-os/emoji-os-zero.py
# The path is resolved relative to this file so it is not tied to any
# specific username. If the file is absent or unreadable, PAIR_NAME
# falls back to "default". See python/emoji-os/project/multiplayer-mode.md
# and emoji-app/docs/real-time-game/multi-badge-plan.md.
import os as _os
import importlib.util as _imp_util

_HERE = _os.path.dirname(_os.path.abspath(__file__))
# python/emoji-os/  ->  python/  ->  <repo>/  ->  <repo_parent>/
_PAIR_CONFIG_DIR = _os.path.normpath(_os.path.join(_HERE, "..", "..", ".."))
_PAIR_CONFIG_PATH = _os.path.join(_PAIR_CONFIG_DIR, "pair_config.py")


def _resolve_badge_names(raw, pair_name):
    """Return an ordered, de-duplicated Pico roster from pair_config.BADGE_NAMES.

    Missing, empty, or invalid values fall back to ``[pair_name]`` (Mode 1).
    """
    if not isinstance(raw, (list, tuple)):
        return [pair_name]
    names = []
    seen = set()
    for item in raw:
        if not isinstance(item, str):
            continue
        name = item.strip()
        if not name or name in seen:
            continue
        seen.add(name)
        names.append(name)
    return names if names else [pair_name]


try:
    if not _os.path.isfile(_PAIR_CONFIG_PATH):
        raise FileNotFoundError(f"not found: {_PAIR_CONFIG_PATH}")
    _spec = _imp_util.spec_from_file_location("pair_config", _PAIR_CONFIG_PATH)
    _pair_mod = _imp_util.module_from_spec(_spec)
    _spec.loader.exec_module(_pair_mod)
    PAIR_NAME = _pair_mod.PAIR_NAME
    BADGE_NAMES = _resolve_badge_names(getattr(_pair_mod, "BADGE_NAMES", None), PAIR_NAME)
    if hasattr(_pair_mod, "NFC_CARD_MAP_LOCAL") and isinstance(_pair_mod.NFC_CARD_MAP_LOCAL, dict):
        NFC_CARD_MAP_FALLBACK = _pair_mod.NFC_CARD_MAP_LOCAL
        NFC_CARD_MAP = dict(NFC_CARD_MAP_FALLBACK)
        print(f"[NFC] local card map: {len(NFC_CARD_MAP_FALLBACK)} card(s) from pair_config.py", flush=True)
    _PAIR_CONFIG_SOURCE = _PAIR_CONFIG_PATH
except Exception as _pair_exc:
    PAIR_NAME = "default"
    BADGE_NAMES = [PAIR_NAME]
    _PAIR_CONFIG_SOURCE = f"fallback 'default' ({_pair_exc})"

# Target BLE names advertised by roster Picos (see emoji-os-pico.py).
# Mode 1 (BADGE_NAMES omitted) is still a single Pico-Client-<PAIR_NAME>.
_PICO_ADV_PREFIX = "Pico-Client-"
TARGET_DEVICE_NAMES = [f"{_PICO_ADV_PREFIX}{n}" for n in BADGE_NAMES]
TARGET_DEVICE_NAME = f"{_PICO_ADV_PREFIX}{PAIR_NAME}"
PAIR_HANDSHAKE_TIMEOUT_S = 5.0
_ROSTER_RETRY_S = 8.0
_ROSTER_IDLE_S = 20.0

print(f"[PAIR] config file : {_PAIR_CONFIG_SOURCE}", flush=True)
print(f"[PAIR] PAIR_NAME   : '{PAIR_NAME}'", flush=True)
print(f"[PAIR] BADGE_NAMES : {BADGE_NAMES}", flush=True)
print(f"[PAIR] looking for : {TARGET_DEVICE_NAMES}", flush=True)


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

# Lobby prompt: yellow centre, green KEY1 top-right, red KEY3 bottom-right
game_lobby_matrix = [
    [' ', ' ', ' ', ' ', ' ', ' ', 'G', 'G'],
    [' ', ' ', ' ', ' ', ' ', ' ', 'G', 'G'],
    [' ', ' ', 'Y', 'Y', 'Y', 'Y', ' ', ' '],
    [' ', ' ', 'Y', 'Y', 'Y', 'Y', ' ', ' '],
    [' ', ' ', 'Y', 'Y', 'Y', 'Y', ' ', ' '],
    [' ', ' ', 'Y', 'Y', 'Y', 'Y', ' ', ' '],
    [' ', ' ', ' ', ' ', ' ', ' ', 'R', 'R'],
    [' ', ' ', ' ', ' ', ' ', ' ', 'R', 'R'],
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

# All rounds complete: solid yellow 4×4 centre, without lobby choice corners
game_rounds_complete_matrix = [
    [' ', ' ', ' ', ' ', ' ', ' ', ' ', ' '],
    [' ', ' ', ' ', ' ', ' ', ' ', ' ', ' '],
    [' ', ' ', 'Y', 'Y', 'Y', 'Y', ' ', ' '],
    [' ', ' ', 'Y', 'Y', 'Y', 'Y', ' ', ' '],
    [' ', ' ', 'Y', 'Y', 'Y', 'Y', ' ', ' '],
    [' ', ' ', 'Y', 'Y', 'Y', 'Y', ' ', ' '],
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

class BadgeLink:
    """One BLE connection to a roster Pico, keyed by that Pico's PAIR_NAME."""

    def __init__(self, badge_name):
        self.badge_name = badge_name
        self.client = None
        self.address = None
        self.connected = False
        self.pico_version = "unknown"
        self.intentional_disconnect = False
        self._pair_event = None
        self._pair_response = None

    def is_up(self):
        return bool(self.connected and self.client and self.client.is_connected)


# BLE Central: one BleakClient per BADGE_NAMES entry.
class BLEController:
    """Connects to every Pico whose advertised name is in the roster."""

    def __init__(self):
        self.links = {name: BadgeLink(name) for name in BADGE_NAMES}
        self._scan_lock = None

    def _ensure_scan_lock(self):
        if self._scan_lock is None:
            self._scan_lock = asyncio.Lock()
        return self._scan_lock

    def unmatched_names(self):
        return [name for name in BADGE_NAMES if not self.links[name].is_up()]

    def connected_names(self):
        return [name for name in BADGE_NAMES if self.links[name].is_up()]

    def is_any_connected(self):
        return bool(self.connected_names())

    def primary_link(self):
        """Mode 1 compatibility: first connected roster badge, else first slot."""
        for name in BADGE_NAMES:
            link = self.links.get(name)
            if link and link.is_up():
                return link
        return self.links.get(BADGE_NAMES[0]) if BADGE_NAMES else None

    @property
    def client(self):
        link = self.primary_link()
        return link.client if link else None

    @property
    def device_address(self):
        link = self.primary_link()
        return link.address if link else None

    @property
    def connected(self):
        return self.is_any_connected()

    def _log_roster(self):
        up = self.connected_names()
        print(
            f"[BLE] roster {len(up)}/{len(BADGE_NAMES)} connected: "
            f"{', '.join(up) if up else '(none)'}",
            flush=True,
        )

    def _collect_roster_matches(self, devices, unmatched, found):
        wanted = set(unmatched)
        for device in devices:
            name = device.name or ""
            if not name.startswith(_PICO_ADV_PREFIX):
                continue
            badge_name = name[len(_PICO_ADV_PREFIX):]
            if badge_name not in wanted:
                if badge_name and badge_name not in BADGE_NAMES:
                    print(
                        f"[BLE] ignoring '{name}' (not in BADGE_NAMES)",
                        flush=True,
                    )
                continue
            if badge_name in found:
                continue
            found[badge_name] = device
            print(
                f"✓ Selected {name} → badgeName='{badge_name}' at {device.address}",
                flush=True,
            )

    async def _discover_roster(self, unmatched, timeout):
        """One UUID scan plus one general scan. Returns badgeName → device."""
        found = {}
        print(
            f"Scanning for roster badges: {unmatched} "
            f"(advertised as {[ _PICO_ADV_PREFIX + n for n in unmatched ]})",
            flush=True,
        )

        print(
            f"\nAttempting to scan by service UUID (filtered by roster) — "
            f"timeout={timeout}s ...",
            flush=True,
        )
        _t0 = time.monotonic()
        try:
            devices = await BleakScanner.discover(
                timeout=timeout,
                service_uuids=[UART_SERVICE_UUID],
            )
            print(
                f"[BLE] UUID scan returned {len(devices)} device(s) in "
                f"{time.monotonic()-_t0:.1f}s",
                flush=True,
            )
            if devices:
                print("✓ Found device(s) advertising Nordic UART Service:")
                for device in devices:
                    print(f"  - {(device.name or '(No Name)'):<24} | {device.address}")
                self._collect_roster_matches(devices, unmatched, found)
        except Exception as e:
            print(
                f"[BLE] UUID scan failed after {time.monotonic()-_t0:.1f}s: {e}",
                flush=True,
            )

        still_needed = [n for n in unmatched if n not in found]
        if not still_needed:
            return found

        print(f"\nPerforming general scan for {timeout} seconds...", flush=True)
        _t1 = time.monotonic()
        try:
            devices = await BleakScanner.discover(timeout=timeout)
        except Exception as e:
            print(
                f"[BLE] General scan failed after {time.monotonic()-_t1:.1f}s: {e}",
                flush=True,
            )
            devices = []
        print(
            f"[BLE] General scan returned {len(devices)} device(s) in "
            f"{time.monotonic()-_t1:.1f}s",
            flush=True,
        )
        print("Found BLE devices:")
        print("-" * 50)
        for i, device in enumerate(devices, 1):
            print(f"{i:2d}. {(device.name or '(No Name)'):<20} | {device.address}")
        print("-" * 50)
        self._collect_roster_matches(devices, still_needed, found)
        return found

    async def scan_and_connect_roster(self, timeout=10):
        """Scan once, then connect unmatched roster badges one at a time.

        Returns True if at least one roster badge is connected when finished.
        Overlapping callers wait on a single BlueZ scan lock.
        """
        lock = self._ensure_scan_lock()
        async with lock:
            unmatched = self.unmatched_names()
            if not unmatched:
                print("[BLE] roster complete — skip scan", flush=True)
                return True

            print("[BLE] scanning unmatched roster — " + ", ".join(unmatched), flush=True)
            _refresh_ble_status("scanning")

            found = await self._discover_roster(unmatched, timeout)
            if not found:
                print(
                    f"\n✗ No roster Pico found. Looking for: {unmatched}",
                    flush=True,
                )
                print("Troubleshooting tips:", flush=True)
                print(
                    "1. Each badge needs emoji-os-pico.py with PAIR_NAME in BADGE_NAMES",
                    flush=True,
                )
                print("2. Check the Pico console prints 'Starting advertising...'", flush=True)
                print(
                    f"3. Advertised names must be exactly {TARGET_DEVICE_NAMES}",
                    flush=True,
                )
                print("4. Try moving devices closer together", flush=True)
                _refresh_ble_status()
                self._log_roster()
                return False

            for name in unmatched:
                device = found.get(name)
                if device is None:
                    print(f"[BLE] '{name}' not seen this scan — will retry", flush=True)
                    continue
                await self._connect_named(name, device.address)

            self._log_roster()
            _refresh_ble_status()
            return self.is_any_connected()

    async def _connect_named(self, badge_name, address):
        """Connect + PAIR:<badge_name> for one roster slot. Serial callers only."""
        link = self.links[badge_name]
        if link.is_up():
            return True

        print(f"[BLE] connecting badgeName='{badge_name}' at {address}...", flush=True)
        _refresh_ble_status("connecting")
        _post_slot_status(badge_name, "connecting")
        link.address = address
        link.intentional_disconnect = False
        try:
            link.client = BleakClient(
                address,
                disconnected_callback=lambda client, n=badge_name: _on_pico_disconnect(client, n),
            )
            await link.client.connect(timeout=10.0)
            if not link.client.is_connected:
                print(f"✗ '{badge_name}' failed to connect (not connected after connect())", flush=True)
                link.client = None
                _refresh_ble_status()
                _post_slot_status(badge_name, "disconnected")
                return False

            print(f"✓ '{badge_name}' connected at BLE layer — running pair handshake", flush=True)
            try:
                uart_found = False
                for service in link.client.services:
                    if service.uuid.lower() == UART_SERVICE_UUID.lower():
                        uart_found = True
                        print(f"✓ '{badge_name}' Nordic UART Service is available", flush=True)
                        break
                if not uart_found:
                    print(f"⚠ '{badge_name}' connected but Nordic UART Service not found", flush=True)
            except Exception as e:
                print(f"⚠ '{badge_name}' could not verify services: {e}", flush=True)

            if not await self._do_pair_handshake(link):
                print(f"✗ Pair handshake failed for '{badge_name}' — disconnecting", flush=True)
                link.intentional_disconnect = True
                link.connected = False
                try:
                    await link.client.disconnect()
                except Exception:
                    pass
                link.client = None
                _refresh_ble_status()
                _post_slot_status(badge_name, "disconnected")
                return False

            link.connected = True
            _sync_primary_pico_version()
            _refresh_ble_status()
            print(
                f"[BLE] connected badgeName='{badge_name}' picoVersion='{link.pico_version}' "
                f"— queueing POST /api/status",
                flush=True,
            )
            _post_slot_status(badge_name, "connected")
            try:
                await link.client.start_notify(
                    UART_TX_CHAR_UUID,
                    lambda sender, data, n=badge_name: _on_pico_tx_notify(sender, data, n),
                )
                print(f"[BLE] TX notifications enabled for '{badge_name}'", flush=True)
            except Exception as _ne:
                print(
                    f"[BLE] warning: could not enable TX notifications for '{badge_name}': {_ne}",
                    flush=True,
                )
            await _sync_badge_game_state(badge_name)
            return True

        except asyncio.TimeoutError:
            print(f"✗ '{badge_name}' connection timeout — may be out of range", flush=True)
            link.client = None
            _refresh_ble_status()
            _post_slot_status(badge_name, "disconnected")
            return False
        except Exception as e:
            error_msg = str(e)
            print(f"✗ '{badge_name}' connection error: {error_msg}", flush=True)
            if "not found" in error_msg.lower() or "not available" in error_msg.lower():
                print("  → Device may not be advertising or is out of range", flush=True)
            elif "timeout" in error_msg.lower():
                print("  → Connection timed out — device may be busy", flush=True)
            link.client = None
            _refresh_ble_status()
            _post_slot_status(badge_name, "disconnected")
            return False

    async def _do_pair_handshake(self, link):
        """Send PAIR:<badgeName> and wait for PAIR_OK on that link."""
        link._pair_response = None
        link._pair_event = asyncio.Event()

        def _on_notify(_sender: BleakGATTCharacteristic, data: bytearray):
            try:
                text = bytes(data).decode("utf-8", "ignore").strip()
            except Exception:
                text = ""
            print(
                f"[PAIR] notify from '{link.badge_name}': {text!r}",
                flush=True,
            )
            link._pair_response = text
            if link._pair_event:
                link._pair_event.set()

        try:
            await link.client.start_notify(UART_TX_CHAR_UUID, _on_notify)
        except Exception as e:
            print(f"[PAIR] '{link.badge_name}' start_notify failed: {e}", flush=True)
            return False

        pair_msg = f"PAIR:{link.badge_name}".encode("utf-8")
        try:
            await link.client.write_gatt_char(UART_RX_CHAR_UUID, pair_msg)
            print(f"[PAIR] sent {pair_msg!r} to '{link.badge_name}'", flush=True)
        except Exception as e:
            print(f"[PAIR] '{link.badge_name}' write failed: {e}", flush=True)
            try:
                await link.client.stop_notify(UART_TX_CHAR_UUID)
            except Exception:
                pass
            return False

        try:
            await asyncio.wait_for(link._pair_event.wait(), timeout=PAIR_HANDSHAKE_TIMEOUT_S)
        except asyncio.TimeoutError:
            print(
                f"[PAIR] '{link.badge_name}' handshake timed out after "
                f"{PAIR_HANDSHAKE_TIMEOUT_S}s",
                flush=True,
            )
            try:
                await link.client.stop_notify(UART_TX_CHAR_UUID)
            except Exception:
                pass
            return False

        try:
            await link.client.stop_notify(UART_TX_CHAR_UUID)
        except Exception:
            pass

        resp = link._pair_response or ""
        if resp == "PAIR_OK" or resp.startswith("PAIR_OK:"):
            if ":" in resp:
                link.pico_version = resp.split(":", 1)[1].strip() or "unknown"
            else:
                link.pico_version = "unknown"
            print(
                f"[PAIR] OK — paired badgeName='{link.badge_name}' "
                f"picoVersion='{link.pico_version}'",
                flush=True,
            )
            return True
        print(
            f"[PAIR] '{link.badge_name}' handshake rejected: {link._pair_response!r}",
            flush=True,
        )
        return False

    def _mark_link_down(self, link, reason):
        """Mark one roster slot down without touching the others."""
        print(f"✗ '{link.badge_name}' write failed: {reason}", flush=True)
        link.connected = False
        _refresh_ble_status()
        _post_slot_status(link.badge_name, "disconnected")
        if ble_event_loop and ble_event_loop.is_running():
            asyncio.run_coroutine_threadsafe(_reconnect(), ble_event_loop)

    async def write_link(self, link, data, *, label=""):
        """Write to one link. A failure drops only that slot. Returns True on success."""
        if not link or not link.is_up():
            return False
        try:
            await link.client.write_gatt_char(UART_RX_CHAR_UUID, data)
            return True
        except Exception as exc:
            self._mark_link_down(link, f"{label or data!r}: {exc}")
            return False

    async def write_roster(self, data, *, label="", badge_name=None):
        """Write to every connected badge, or only ``badge_name`` if given.

        Returns the number of successful writes. One failed badge does not
        abort the rest of the roster.
        """
        if badge_name:
            targets = []
            link = self.links.get(badge_name)
            if link:
                targets.append(link)
            elif badge_name:
                print(f"[BLE] skip write {label!r} — unknown badgeName='{badge_name}'", flush=True)
        else:
            targets = [self.links[name] for name in BADGE_NAMES]

        ok = 0
        skipped = 0
        for link in targets:
            if not link.is_up():
                skipped += 1
                print(f"[BLE] skip '{link.badge_name}' for {label!r} (not connected)", flush=True)
                continue
            if await self.write_link(link, data, label=label):
                print(f"✓ Wrote {label!r} to '{link.badge_name}'", flush=True)
                ok += 1
        if ok == 0 and skipped == len(targets):
            print(f"Not connected to any device — skipping {label!r}", flush=True)
        return ok

    async def send_emoji_command(self, menu, pos, neg):
        """Fan-out emoji selection to every connected Pico. One station API post."""
        command = f"{menu}:{pos}:{neg}"
        n = await self.write_roster(command.encode("utf-8"), label=command)
        if n:
            print("[BLE] queueing POST /api/emoji", flush=True)
            post_to_server("/api/emoji", _emoji_payload(menu, pos, neg))
            return True
        return False

    async def disconnect(self):
        """Disconnect every roster link (shutdown)."""
        global _heartbeat_task
        if _heartbeat_task and not _heartbeat_task.done():
            _heartbeat_task.cancel()
            _heartbeat_task = None
        for name, link in self.links.items():
            if not link.client:
                continue
            link.intentional_disconnect = True
            link.connected = False
            if link.client.is_connected:
                try:
                    await link.client.disconnect()
                    print(f"Disconnected '{name}'", flush=True)
                except Exception:
                    pass
            link.client = None
        _refresh_ble_status()
        _post_roster_status("disconnected")

# Global BLE controller instance
ble_controller = BLEController()
ble_connection_thread = None
ble_event_loop = None

# Connection status state: "idle", "connecting", "connected", "disconnected"
ble_connection_status = "idle"

# Heartbeat asyncio task — started once on the BLE loop
_heartbeat_task = None


def _sync_primary_pico_version():
    """Keep the station-level _pico_version aligned with the primary badge."""
    global _pico_version
    link = ble_controller.primary_link()
    if link and link.is_up():
        _pico_version = link.pico_version


def _refresh_ble_status(phase=None):
    """Set the LCD BLE indicator from roster state.

    If any badge is connected the indicator stays connected, even while a
    background scan fills empty slots. ``phase`` is used only when nothing
    is connected yet (scanning / connecting). Per-slot HTTP status is
    posted separately via ``_post_slot_status`` / ``_post_roster_status``.
    """
    global ble_connection_status
    if ble_controller.is_any_connected():
        new_status = "connected"
    elif phase in ("scanning", "connecting"):
        new_status = phase
    else:
        new_status = "disconnected"
    if ble_connection_status == new_status:
        return
    ble_connection_status = new_status
    draw_connection_indicator()
    disp.LCD_ShowImage(image, 0, 0)


def _utc_iso_timestamp():
    # Hint for APIs only — Pi RTC/NTP may be wrong; emoji-app should use server time.
    return datetime.now(timezone.utc).isoformat()


def _canonical_slot_name(badge_name=None):
    """Return a roster slot name, defaulting to the first BADGE_NAMES entry."""
    if isinstance(badge_name, str) and badge_name in ble_controller.links:
        return badge_name
    return BADGE_NAMES[0] if BADGE_NAMES else PAIR_NAME


def _resolve_badge_id():
    if BADGE_ID and BADGE_ID.strip():
        return BADGE_ID.strip()
    addr = ble_controller.device_address
    if addr:
        slug = addr.lower().replace(":", "-")
        return f"badge-{slug}"
    return "unknown"


def _resolve_slot_badge_id(badge_name):
    """MAC-derived badgeId for a slot; ``unknown`` until that Pico has connected."""
    if BADGE_ID and BADGE_ID.strip() and len(BADGE_NAMES) <= 1:
        return BADGE_ID.strip()
    link = ble_controller.links.get(badge_name)
    addr = link.address if link else None
    if addr:
        slug = addr.lower().replace(":", "-")
        return f"badge-{slug}"
    return "unknown"


def _slot_pico_version(badge_name):
    link = ble_controller.links.get(badge_name)
    if link:
        return link.pico_version
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


def _status_payload(ble_status: str, badge_name=None):
    # API: startup | scanning | connecting | connected | disconnected (see server statusBodySchema).
    # pairName is the station id. badgeName is this roster slot. badgeNames is
    # the full roster on every post so the server can create empty slots.
    name = _canonical_slot_name(badge_name)
    payload: dict = {
        "controllerId": CONTROLLER_ID,
        "badgeId": _resolve_slot_badge_id(name),
        "bleStatus": ble_status,
        "timestamp": _utc_iso_timestamp(),
        "pairName": PAIR_NAME,
        "badgeName": name,
        "badgeNames": list(BADGE_NAMES),
        "controllerVersion": _CONTROLLER_VERSION,
        "picoVersion": _slot_pico_version(name),
    }
    if _battery_percent is not None:
        payload["batteryLevel"] = _battery_percent
    return payload


def _post_slot_status(badge_name, ble_status):
    """POST /api/status for one roster slot (connect / drop / liveness)."""
    name = _canonical_slot_name(badge_name)
    print(
        f"[STATUS] badgeName='{name}' bleStatus={ble_status} "
        f"badgeId={_resolve_slot_badge_id(name)} "
        f"picoVersion={_slot_pico_version(name)}",
        flush=True,
    )
    post_to_server("/api/status", _status_payload(ble_status, badge_name=name))


def _post_roster_status(ble_status):
    """POST one status identity per configured badge name (boot / shutdown)."""
    print(
        f"[STATUS] roster POST bleStatus={ble_status} names={list(BADGE_NAMES)}",
        flush=True,
    )
    for name in BADGE_NAMES:
        _post_slot_status(name, ble_status)


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
        "badgeName": PAIR_NAME,
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
        slot = payload.get("badgeName", "")
        url = f"{SERVER_URL}{path}"
        try:
            kw = {"json": payload, "timeout": 3}
            if API_HEADERS:
                kw["headers"] = API_HEADERS
            slot_bit = f" badgeName={slot}" if slot else ""
            print(
                f"[API] POST {path} controller={cid} badge={bid}{slot_bit}",
                flush=True,
            )
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
    status, data = fetch_with_status(path)
    return data if status == 200 else None


def fetch_with_status(path: str):
    """Blocking HTTP GET; returns (status_code, parsed JSON or None).

    status_code is None when SERVER_URL is empty or the request fails, so a
    caller can tell "server said 404" apart from "server unreachable".
    """
    if not SERVER_URL:
        return None, None
    url = f"{SERVER_URL}{path}"
    try:
        kw = {"timeout": 3}
        if API_HEADERS:
            kw["headers"] = API_HEADERS
        print(f"[API] GET {path}", flush=True)
        r = requests.get(url, **kw)
        print(f"[API] response {path} -> HTTP {r.status_code}", flush=True)
        if r.status_code == 200:
            return 200, r.json()
        return r.status_code, None
    except Exception as e:
        print(f"[API] request failed {path}: {e}", flush=True)
    return None, None


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


def _on_pico_disconnect(client: BleakClient, badge_name=None):
    """Bleak calls this (sync) when one roster BLE link is lost."""
    name = badge_name or "?"
    link = ble_controller.links.get(badge_name) if badge_name else None
    if link and link.intentional_disconnect:
        link.intentional_disconnect = False
        link.connected = False
        print(f"[BLE] '{name}' disconnected (intentional)", flush=True)
        _sync_primary_pico_version()
        _refresh_ble_status()
        return
    print(f"⚠ Pico '{name}' disconnected unexpectedly", flush=True)
    if link:
        link.connected = False
    _sync_primary_pico_version()
    _refresh_ble_status()
    if badge_name:
        _post_slot_status(badge_name, "disconnected")
    ble_controller._log_roster()
    if ble_event_loop and ble_event_loop.is_running():
        asyncio.run_coroutine_threadsafe(_reconnect(), ble_event_loop)


def _schedule_pair_answer(badge_name: str, is_correct: bool, detail: str):
    """Apply correct/wrong for one badge from any thread."""
    if ble_event_loop is None:
        return
    asyncio.run_coroutine_threadsafe(
        _apply_pair_answer(badge_name, is_correct, detail),
        ble_event_loop,
    )


def _relay_nfc_tag(card_uid: str, badge_name=None):
    """Relay a TAG:<cardUid> notification from the Pico as POST /api/guesses.

    Card → slot map (demo):
      R12 Monkey ``5B:6F:B8:08`` → slot **A**
      W3 Clown   ``DB:93:B7:08`` → slot **B**
    Server compares slot to the open question's correct option → blue circle /
    red X. Unknown cards (no slotLabel) are treated as wrong (red X).
    Each badge is its own player: the guess belongs to ``badgeName`` (Mode 1:
    ``PAIR_NAME``) and ``pairName`` is this station. A sibling badge's scan is
    a separate guess; a second scan from the same badge is ignored here.
    """
    player = badge_name or PAIR_NAME
    src = f" badgeName={player}"
    if not _ws_game_id or not _ws_question_id:
        print(
            f"[NFC] TAG {card_uid!r}{src} ignored — no active game/question "
            f"(gameId={_ws_game_id} questionId={_ws_question_id})",
            flush=True,
        )
        return
    if player in _badges_answered:
        print(
            f"[NFC] TAG {card_uid!r}{src} ignored — badge already answered "
            f"questionId={_ws_question_id}",
            flush=True,
        )
        return
    card_info = NFC_CARD_MAP.get(card_uid, {})
    slot_label = card_info.get("slotLabel")
    _log_game_state(
        "card_scanned",
        f"TAG={card_uid!r}{src} slotLabel={slot_label!r} → POST /api/guesses",
    )

    # Unknown / unmapped card → wrong (red X). Do not send invalid badgeId.
    if not slot_label:
        _schedule_pair_answer(
            player,
            False,
            f"unknown TAG={card_uid!r}{src} — no slotLabel; treat as wrong",
        )
        return

    payload = {
        "gameId":     _ws_game_id,
        "questionId": _ws_question_id,
        "pairName":   PAIR_NAME,
        "badgeName":  player,
        "cardUid":    card_uid,
        "slotLabel":  slot_label,
    }
    # Guess API only accepts 24-char hex ObjectIds for badgeId; BLE slug
    # (badge-88-…) must be omitted or the whole guess 400s with no feedback.
    bid = _resolve_slot_badge_id(badge_name) if badge_name else _resolve_badge_id()
    if isinstance(bid, str) and len(bid) == 24 and all(
        c in "0123456789abcdefABCDEF" for c in bid
    ):
        payload["badgeId"] = bid

    def _post_guess_and_apply():
        if not SERVER_URL:
            print(
                "[API] skip guess POST — SERVER_URL empty; "
                "leaving tap acknowledgement pending",
                flush=True,
            )
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
                print(
                    "[GAME] zero | card_scanned | Card scanned | "
                    f"guess HTTP {r.status_code}; outcome unknown — "
                    f"waiting for question.result; {snippet}",
                    flush=True,
                )
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
            _schedule_pair_answer(
                player,
                bool(is_correct),
                f"POST /api/guesses{src} isCorrect={is_correct} "
                f"slotLabel={data.get('slotLabel')!r}",
            )
        except Exception as exc:
            print(f"[API] request failed /api/guesses: {exc}", flush=True)
            print(
                "[GAME] zero | card_scanned | Card scanned | "
                f"guess request failed; outcome unknown — "
                f"waiting for question.result; {exc}",
                flush=True,
            )

    threading.Thread(target=_post_guess_and_apply, daemon=True).start()


def _on_pico_tx_notify(_sender: BleakGATTCharacteristic, data: bytearray, badge_name=None):
    """Persistent TX notification handler — receives async messages from the Pico.

    Handles two prefixes:
    - ``TAG:<cardUid>``  — new game-mode path (Step 4 Pico firmware); relays
      the UID to the server as a guess via POST /api/guesses.
    - ``NFC:<card_id>``  — legacy path; looks up the card in NFC_CARD_MAP and
      updates the Zero/Pico display (unchanged behaviour).
    """
    try:
        text = bytes(data).decode("utf-8", "ignore").strip()
        src = f" badge={badge_name}" if badge_name else ""
        print(f"[PICO→ZERO]{src} {text!r}", flush=True)
        if text.startswith("TAG:"):
            card_uid = text[4:]
            _relay_nfc_tag(card_uid, badge_name)
        elif text.startswith("NFC:"):
            card_id = text[4:]
            _handle_nfc_card(card_id, badge_name)
    except Exception as e:
        print(f"[BLE] error in TX notify handler: {e}", flush=True)


def _handle_nfc_card(card_id: str, badge_name=None):
    """Process an NFC card ID received from the Pico.

    Looks up the card in NFC_CARD_MAP, updates the Zero display, sends
    the result back to every connected Pico so their matrices match,
    and POSTs the result to /api/emoji so the dashboard reflects the scan.
    The result is cleared after NFC_RESULT_DISPLAY_S seconds.
    """
    global nfc_last_result, nfc_last_card_name
    src = f" badgeName={badge_name}" if badge_name else ""

    if not nfc_mode_active:
        print(f"[NFC] card read ignored (not in NFC mode): {card_id}{src}", flush=True)
        return

    card = NFC_CARD_MAP.get(card_id)
    if card:
        nfc_last_card_name = card["name"]
        nfc_last_result = card["display"]
        print(f"[NFC] known card{src}: {card['name']} → {card['display']}", flush=True)
    else:
        nfc_last_card_name = f"Unknown ({card_id})"
        nfc_last_result = "unknown"
        print(f"[NFC] unknown card{src}: {card_id}", flush=True)

    draw_display()

    # Post the NFC scan result to the server so the dashboard updates.
    # "circle" cards → menu 3 pos 4 neg 0 (others_nfc_pos)
    # "x" / unknown  → menu 3 pos 0 neg 4 (others_nfc_neg)
    if nfc_last_result == "circle":
        post_to_server("/api/emoji", _emoji_payload(3, 4, 0))
    else:
        post_to_server("/api/emoji", _emoji_payload(3, 0, 4))

    # Fan-out so every connected badge mirrors the Zero's NFC response
    result_symbol = "circle" if nfc_last_result == "circle" else "x"
    nfc_result_cmd = f"NFC_RESULT:{result_symbol}".encode("utf-8")
    if ble_event_loop:
        async def _send_nfc_result():
            await ble_controller.write_roster(
                nfc_result_cmd,
                label=f"NFC_RESULT:{result_symbol}",
            )
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
    """Fill unmatched roster slots after a drop or a missed first scan."""
    await asyncio.sleep(2)
    await ble_controller.scan_and_connect_roster(timeout=10)


async def _roster_maintain_loop():
    """Periodically rescan empty roster slots without overlapping BlueZ scans."""
    while True:
        unmatched = ble_controller.unmatched_names()
        await asyncio.sleep(_ROSTER_RETRY_S if unmatched else _ROSTER_IDLE_S)
        if ble_controller.unmatched_names():
            print(
                f"[BLE] roster maintain — unmatched={ble_controller.unmatched_names()}",
                flush=True,
            )
            await ble_controller.scan_and_connect_roster(timeout=10)


# === WebSocket client ===

def _player_badges():
    """Joined roster badges in roster order (the players this station answers for)."""
    return [name for name in BADGE_NAMES if name in _joined_badges]


def _station_result():
    """Correct/wrong for the Zero LCD: Mode 1 mirrors its badge; Mode 2 shows none."""
    if len(BADGE_NAMES) == 1:
        return _badge_results.get(BADGE_NAMES[0])
    return None


def _current_game_cmd(badge_name=None):
    """GAME:* command for one badge (or the station when ``badge_name`` is None)."""
    if _ws_game_state == "completed":
        outcome = _badge_end_outcomes.get(badge_name) if badge_name else None
        outcome = outcome or _game_end_outcome
        if outcome == "winner":
            return "GAME:winner"
        if outcome == "loser":
            return "GAME:loser"
        return "GAME:ended"
    result = _badge_results.get(badge_name) if badge_name else _station_result()
    if result == "correct":
        return "GAME:correct"
    if result == "wrong":
        return "GAME:wrong"
    joined = (badge_name in _joined_badges) if badge_name else _ws_joined
    if _ws_game_state == "lobby" and not joined:
        return "GAME:lobby"
    if _ws_game_state == "lobby" and joined:
        return "GAME:lobby_joined"
    if _ws_game_state == "active" and _ws_question_id:
        return "GAME:question_open"
    if _ws_game_state == "active" and _ws_question_phase == "complete":
        return "GAME:rounds_complete"
    if _ws_game_state == "active" and _ws_question_phase == "closed":
        if _next_question_ready is True:
            return "GAME:ready"
        if _next_question_ready is False:
            return "GAME:wait"
        return "GAME:ready_prompt"
    if _ws_game_state == "active":
        return "GAME:active"
    if game_mode_active:
        return "GAME:mode"
    return None


def _post_join(badge_names, reason: str):
    """POST join for these roster badges (each one is a player) and mark them joined."""
    if not _ws_game_id or not badge_names:
        return
    _joined_badges.update(badge_names)
    post_to_server(
        f"/api/games/{_ws_game_id}/join",
        {
            "pairName": PAIR_NAME,
            "controllerId": CONTROLLER_ID,
            "badgeNames": list(badge_names),
        },
    )
    _log_game_state(
        "lobby_joined",
        f"{reason} join POST gameId={_ws_game_id} pair={PAIR_NAME} "
        f"badges={list(badge_names)}",
    )


def _key1_join_badges():
    """Badges joined by KEY1: Mode 1 always its badge; Mode 2 the connected ones."""
    if len(BADGE_NAMES) == 1:
        return list(BADGE_NAMES)
    return ble_controller.connected_names()


async def _sync_badge_game_state(badge_name):
    """Push the current GAME:* command to one newly connected badge.

    Buttonless badges cannot press KEY1. Once the station has joined, a badge
    that connects later while the game is in the lobby or active auto-joins as
    its own player, then gets its own state (GAME:lobby_joined,
    GAME:question_open, …).
    """
    if (
        _ws_joined
        and _ws_game_state in ("lobby", "active")
        and badge_name not in _joined_badges
    ):
        _post_join([badge_name], f"late badge '{badge_name}'")
    cmd = _current_game_cmd(badge_name)
    if not cmd:
        print(f"[BLE] '{badge_name}' late-join: no GAME:* to sync", flush=True)
        return
    print(f"[BLE] '{badge_name}' late-join sync {cmd}", flush=True)
    await _ble_write_game_cmd(cmd, badge_name=badge_name)


async def _ble_write_game_cmd(cmd: str, *, force: bool = False, badge_name=None):
    """Write a GAME:* command to every connected Pico, or one badge.

    Game follow (Milestone 3): ``game.opened`` → GAME:lobby; KEY1 join →
    GAME:lobby_joined; question / result / end events → matching GAME:*.
    A late-connecting badge is synced by ``_sync_badge_game_state``.
    Always forwarded while connected. The badge must receive ``GAME:question_open``
    to arm NFC even if the Zero LCD has left game mode to browse emojis.
    ``force`` is kept for call-site compatibility (ignored).
    """
    del force  # API compat; game BLE is never deferred
    state_id = _GAME_CMD_TO_STATE.get(cmd)
    n = await ble_controller.write_roster(
        cmd.encode("utf-8"),
        label=cmd,
        badge_name=badge_name,
    )
    if n == 0:
        if state_id:
            _log_game_state(state_id, f"BLE not connected — skipping {cmd}")
        else:
            print(f"[WS] BLE not connected — skipping {cmd}", flush=True)
        return
    target = badge_name or f"{n} badge(s)"
    if state_id:
        _log_game_state(state_id, f"BLE→{cmd} ({target})")
    else:
        print(f"[BLE] wrote {cmd!r} to {target}", flush=True)


async def _apply_pair_answer(
    badge_name: str, is_correct: bool, detail: str, *, force: bool = False
):
    """Show correct/wrong on one badge (and the Mode 1 LCD); hold until question_closed.

    Sibling badges keep their own state — they stay on GAME:question_open
    until they scan.
    """
    state_id = "correct" if is_correct else "wrong"
    detail = f"badge={badge_name} {detail}"
    if badge_name in _badges_answered and not force:
        print(
            f"[GAME] zero | {state_id} | {_GAME_STATE_LABELS[state_id]} | "
            f"skip re-animate (already answered); {detail}",
            flush=True,
        )
        return
    # Do not flash correct/wrong after the question has already closed to the
    # white 2×2 glyph — that would fight the Question closed state.
    if _ws_question_phase in ("closed", "complete") and not force:
        print(
            f"[GAME] zero | {state_id} | {_GAME_STATE_LABELS[state_id]} | "
            f"skip — question already closed; {detail}",
            flush=True,
        )
        _badges_answered.add(badge_name)
        return
    _badge_results[badge_name] = state_id
    _badges_answered.add(badge_name)
    _log_game_state(state_id, detail)
    if game_mode_active:
        draw_display()
    await _ble_write_game_cmd(
        "GAME:correct" if is_correct else "GAME:wrong",
        badge_name=badge_name,
    )


def _reset_badge_answers():
    """Clear per-badge correct/wrong and the answered guard (new question / game)."""
    _badge_results.clear()
    _badges_answered.clear()


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
    # Winner/loser glyphs only while the server game is still completed.
    # After Play Again → ready, stale _game_end_outcome must not keep fireworks.
    if _ws_game_state == "completed":
        if _game_end_outcome == "winner":
            return fireworks_animation.preview
        if _game_end_outcome == "loser":
            return rain_animation.preview
        if _game_end_outcome == "ended":
            return game_question_closed_matrix
        return game_question_closed_matrix
    station_result = _station_result()
    if station_result == "correct":
        return game_correct_matrix
    if station_result == "wrong":
        return others_x_matrix
    if _ws_game_state == "lobby" and not _ws_joined:
        return game_lobby_matrix
    if _ws_game_state == "lobby":
        return game_lobby_joined_matrix
    if _ws_game_state == "active":
        if _ws_question_phase == "open":
            return question_mark_matrix
        if _ws_question_phase == "complete":
            return game_rounds_complete_matrix
        if _ws_question_phase == "closed":
            return game_question_closed_matrix
        return game_active_matrix
    # ready / None / unknown — standby 'G'
    return game_mode_matrix


def _clear_game_end_ui():
    """Stop outcome animation and clear winner/loser sticky state."""
    global _game_end_outcome, stop_animation
    _game_end_outcome = None
    _badge_end_outcomes.clear()
    if animation_running:
        stop_animation = True


async def _apply_game_state_to_display():
    """Redraw the Zero LCD (if in game mode) and sync the Pico game state.

    Called after a WS reconnect/welcome snapshot and when the user enters game
    mode locally. Pico is always synced — NFC arming must not depend on the
    Zero LCD being in game mode. Zero LCD redraw is skipped while browsing.
    """
    global _ws_question_phase
    if _ws_game_state == "active" and _ws_question_id:
        _ws_question_phase = "open"
    elif _ws_game_state == "active" and _ws_question_phase is None:
        pass  # keep None → green active until first question
    if game_mode_active:
        draw_display()
    # Sync every connected Pico with its own known game state so a reconnect
    # or late game-mode entry picks up the right display without waiting for
    # the next server event.
    for badge_name in ble_controller.connected_names():
        cmd = _current_game_cmd(badge_name)
        if cmd:
            await _ble_write_game_cmd(cmd, badge_name=badge_name)


def _exit_game_mode_to_menu():
    """Leave full-screen game mode and return to menu-select (state=start).

    Server-side join / game snapshot globals are kept so re-entering game mode
    restores the current status on Zero + Pico.
    """
    global game_mode_active, fullscreen_mode, state, menu, pos, neg
    global prev_state, prev_menu, prev_pos, prev_neg
    global nfc_mode_active, nfc_last_result, nfc_last_card_name
    print("[GAME] exiting game mode → menu select (KEY2)", flush=True)
    game_mode_active = False
    fullscreen_mode = False
    nfc_mode_active = False
    nfc_last_result = None
    nfc_last_card_name = ""
    # Clear prev so KEY1/KEY3 do not immediately replay game-mode slot.
    prev_state = "none"
    prev_menu = 0
    prev_pos = 0
    prev_neg = 0
    state = "start"
    menu = 0
    pos = 0
    neg = 0
    draw_display()


def _respond_to_ready_prompt(ready: bool) -> bool:
    """Record KEY1 ready / KEY3 wait while between questions."""
    global _next_question_ready
    if not (
        game_mode_active
        and _ws_game_state == "active"
        and _ws_question_phase == "closed"
        and _ws_game_id
    ):
        return False

    _next_question_ready = ready
    badge_names = _player_badges() or list(BADGE_NAMES[:1])
    post_to_server(
        f"/api/games/{_ws_game_id}/readiness",
        {
            "pairName": PAIR_NAME,
            "controllerId": CONTROLLER_ID,
            "ready": ready,
            "badgeNames": badge_names,
        },
    )
    draw_display()
    state_id = "ready" if ready else "wait"
    _log_game_state(
        state_id,
        f"{'KEY1 ready' if ready else 'KEY3 wait'} POST "
        f"gameId={_ws_game_id} pair={PAIR_NAME} badges={badge_names}",
    )
    if ble_event_loop is not None:
        asyncio.run_coroutine_threadsafe(
            _ble_write_game_cmd("GAME:ready" if ready else "GAME:wait"),
            ble_event_loop,
        )
    return True


async def _ws_handle_event(event: dict):
    """Dispatch a single WebSocket event from the server."""
    global _ws_game_id, _ws_game_state, _ws_question_id, _ws_joined, _join_pending
    global _ws_question_phase
    global _next_question_ready
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
        # draft (setup) and ready (standby) both show the G glyph on controllers.
        raw_state = event.get("state")
        _ws_game_state = "ready" if raw_state in ("draft", "ready") else raw_state
        _ws_question_id = event.get("openQuestionId")
        _ws_joined      = event.get("joined", False)
        _next_question_ready = event.get("readyForNextQuestion")
        # KEY1 join only works when lobby is open and we have not joined yet.
        _join_pending = bool(
            _ws_game_state == "lobby" and not _ws_joined and _ws_game_id
        )
        _reset_badge_answers()
        # Per-badge join / guess state; older servers send no players[].
        _joined_badges.clear()
        players = event.get("players")
        if isinstance(players, list):
            for player in players:
                name = player.get("badgeName") if isinstance(player, dict) else None
                if name not in BADGE_NAMES:
                    continue
                if player.get("joined"):
                    _joined_badges.add(name)
                if player.get("guessed") and _ws_question_id:
                    _badges_answered.add(name)
                    _badge_results[name] = "correct" if player.get("isCorrect") else "wrong"
        elif _ws_joined:
            _joined_badges.update(BADGE_NAMES)
        # Snapshot welcome has no winner enrichment — clear sticky end UI so a
        # reconnect or re-entry after Play Again does not re-show fireworks.
        _clear_game_end_ui()
        if _ws_game_state == "active" and _ws_question_id:
            _ws_question_phase = "open"
        elif _ws_game_state == "active":
            _ws_question_phase = (
                "complete" if event.get("roundsComplete") else "closed"
            )
        else:
            _ws_question_phase = None
        print(
            f"[WS] welcome: game={_ws_game_id} state={_ws_game_state} "
            f"joined={_ws_joined} badges={_player_badges()} "
            f"join_pending={_join_pending}",
            flush=True,
        )
        await _apply_game_state_to_display()

    elif etype == "game.ready":
        # Play Again / Restart — back to standby 'G' (not winner fireworks).
        _ws_game_state = "ready"
        _ws_question_id = None
        _ws_question_phase = None
        _ws_joined = False
        _joined_badges.clear()
        _join_pending = False
        _reset_badge_answers()
        _next_question_ready = None
        _clear_game_end_ui()
        _log_game_state("mode", "WS game.ready — standby G")
        if game_mode_active:
            draw_display()
        await _ble_write_game_cmd("GAME:mode")

    elif etype == "pair.unbound":
        # Referee removed this station, or Play Again cleared bindings.
        if event.get("pairName") not in (None, PAIR_NAME):
            return
        had_game = _ws_game_id is not None or _ws_game_state is not None
        _ws_game_id = None
        _ws_game_state = None
        _ws_question_id = None
        _ws_question_phase = None
        _ws_joined = False
        _joined_badges.clear()
        _join_pending = False
        _reset_badge_answers()
        _next_question_ready = None
        _clear_game_end_ui()
        if not had_game:
            return
        _log_game_state("mode", "WS pair.unbound — standby G")
        if game_mode_active:
            draw_display()
        await _ble_write_game_cmd("GAME:mode")

    elif etype == "game.opened":
        _ws_game_id    = event.get("gameId")
        _ws_game_state = "lobby"
        _ws_joined     = False
        _joined_badges.clear()
        _join_pending  = True
        _ws_question_phase = None
        _reset_badge_answers()
        _next_question_ready = None
        _clear_game_end_ui()
        _log_game_state("lobby", f"WS game.opened gameId={_ws_game_id}")
        if game_mode_active:
            draw_display()
        await _ble_write_game_cmd("GAME:lobby")

    elif etype == "game.started":
        _ws_game_state = "active"
        _ws_question_phase = None
        _reset_badge_answers()
        _next_question_ready = None
        _clear_game_end_ui()
        _log_game_state("active", "WS game.started")
        if game_mode_active:
            draw_display()
        await _ble_write_game_cmd("GAME:active")

    elif etype == "question.opened":
        _ws_question_id = event.get("questionId")
        _ws_question_phase = "open"
        _reset_badge_answers()
        _next_question_ready = None
        _log_game_state(
            "question_open",
            f"WS question.opened questionId={_ws_question_id}",
        )
        if game_mode_active:
            draw_display()
        await _ble_write_game_cmd("GAME:question_open")

    elif etype == "question.closed":
        _ws_question_id = None
        _ws_question_phase = (
            "complete" if event.get("isFinalRound") else "closed"
        )
        _badge_results.clear()  # LCD / badges → white 2×2; answered set kept for skip
        _next_question_ready = None
        _log_game_state("question_closed", "WS question.closed")
        if game_mode_active:
            draw_display()
        if _ws_question_phase == "complete":
            _log_game_state("rounds_complete", "final question closed")
            await _ble_write_game_cmd("GAME:rounds_complete")
        else:
            await _ble_write_game_cmd("GAME:ready_prompt")

    elif etype == "game.ended":
        # The server sends one enriched game.ended per badge (player). Only the
        # first one of a game resets the round state.
        if _ws_game_state != "completed":
            _reset_badge_answers()
        _ws_game_state  = "completed"
        _ws_question_id = None
        _ws_question_phase = None
        # Prefer winner/loser when enriched fields arrive (Step 8); else generic end.
        if "isWinner" in event:
            badge_name = event.get("badgeName")
            if badge_name and badge_name not in BADGE_NAMES:
                print(f"[WS] game.ended for unknown badge '{badge_name}' — ignored", flush=True)
                return
            outcome = "winner" if event.get("isWinner") else "loser"
            # Older servers send one station-level event without badgeName.
            targets = [badge_name] if badge_name else list(BADGE_NAMES)
            for name in targets:
                _badge_end_outcomes[name] = outcome
            station_outcome = (
                "winner" if "winner" in _badge_end_outcomes.values() else "loser"
            )
            station_changed = station_outcome != _game_end_outcome
            _game_end_outcome = station_outcome
            _log_game_state(
                outcome,
                f"WS game.ended badge={badge_name or 'all'} rank={event.get('rank')} "
                f"score={event.get('score')}",
            )
            if game_mode_active:
                draw_display()
            await _ble_write_game_cmd(
                "GAME:winner" if outcome == "winner" else "GAME:loser",
                badge_name=badge_name,
            )
            if station_changed:
                _start_game_outcome_animation(station_outcome == "winner")
        else:
            _game_end_outcome = "ended"
            _log_game_state("game_ended", "WS game.ended")
            if game_mode_active:
                draw_display()
            await _ble_write_game_cmd("GAME:ended")

    elif etype == "question.result":
        results = event.get("results") or []
        by_badge = {}
        for row in results:
            key = row.get("badgeName") or row.get("pairName")
            if key:
                by_badge[key] = row
        # Mode 1 always answers for its badge; Mode 2 for the joined badges.
        targets = _player_badges() or (list(BADGE_NAMES) if len(BADGE_NAMES) == 1 else [])
        for name in targets:
            row = by_badge.get(name)
            is_correct = bool(row and row.get("isCorrect"))
            slot = row.get("slotLabel") if row else None
            await _apply_pair_answer(
                name,
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
                    "badgeNames":        list(BADGE_NAMES),
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
        status, data = fetch_with_status(f"/api/pairs/{PAIR_NAME}")
        if status == 404:
            # Not bound to any game (removed by the referee, or Play Again).
            if ble_event_loop and ble_event_loop.is_running():
                asyncio.run_coroutine_threadsafe(
                    _ws_handle_event({"type": "pair.unbound", "pairName": PAIR_NAME}),
                    ble_event_loop,
                )
            return
        if not isinstance(data, dict):
            return
        synthetic_event = {
            "type":                 "controller.welcome",
            "gameId":               data.get("gameId"),
            "state":                data.get("state"),
            "joined":               data.get("joined", False),
            "openQuestionId":       data.get("openQuestionId"),
            "readyForNextQuestion": data.get("readyForNextQuestion"),
            "roundsComplete":       data.get("roundsComplete", False),
        }
        if isinstance(data.get("players"), list):
            synthetic_event["players"] = data["players"]
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
        for name, link in ble_controller.links.items():
            if not link.is_up():
                continue
            try:
                await link.client.write_gatt_char(UART_RX_CHAR_UUID, b"STATUS")
            except Exception:
                # The disconnected_callback will handle the clean-up;
                # swallow the exception here to keep the loop alive.
                print(f"[BLE] heartbeat write failed for '{name}'", flush=True)
        connected = ble_controller.connected_names()
        if connected:
            nowm = time.monotonic()
            if nowm - _last_status_liveness_post >= STATUS_LIVENESS_POST_S:
                _last_status_liveness_post = nowm
                print(
                    f"[BLE] liveness — queueing POST /api/status connected "
                    f"for {connected}",
                    flush=True,
                )
                for name in connected:
                    _post_slot_status(name, "connected")
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

    # Keep the badge on ? / NFC-ready while a question is open — do not overwrite
    # with a decorative emoji (Zero LCD can still show the chosen emoji).
    if _ws_question_id and _ws_question_phase == "open":
        print(
            "[GAME] skip emoji BLE — question open; Pico stays on scan state",
            flush=True,
        )
        return

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
    # KEY1 joins when a lobby is waiting; KEY2 exits to menu select.
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


def draw_network_indicator():
    """Draw Wi-Fi route status directly above the BLE indicator.

    Green Wi-Fi arcs mean the Zero has a usable network route. Red crossed
    arcs mean it does not. This reports LAN routing independently of BLE state
    and does not require the emoji server itself to be running.
    """
    color = (0, 200, 0) if _network_connected else (220, 40, 40)
    center_x = 10

    # Three compact Wi-Fi arcs aligned with the lower-left BLE indicator.
    draw.arc(
        [center_x - 10, 84, center_x + 10, 104],
        start=215,
        end=325,
        fill=color,
        width=2,
    )
    draw.arc(
        [center_x - 7, 89, center_x + 7, 103],
        start=215,
        end=325,
        fill=color,
        width=2,
    )
    draw.arc(
        [center_x - 4, 94, center_x + 4, 102],
        start=215,
        end=325,
        fill=color,
        width=2,
    )
    draw.ellipse([center_x - 1, 100, center_x + 1, 102], fill=color)

    if not _network_connected:
        draw.line(
            [center_x - 8, 86, center_x + 8, 102],
            fill=color,
            width=2,
        )


def _game_status_label():
    """Optional secondary text over the Platform icon glyph.

    Most states are glyph-only (matching Pico). Keep an action hint for lobby
    join, and GAME OVER when the game ends without a winner/loser enrichment.
    """
    if not game_mode_active:
        return None, None
    if _ws_game_state == "lobby" and not _ws_joined:
        return "KEY1 JOIN  KEY3 NO", "yellow"
    if _ws_game_state == "active" and _ws_question_phase == "open" and len(BADGE_NAMES) > 1:
        players = _player_badges()
        answered = sum(1 for name in players if name in _badges_answered)
        return f"ANSWERED {answered}/{len(players)}", "yellow"
    if _ws_game_state == "active" and _ws_question_phase == "closed":
        if _next_question_ready is True:
            return "READY", (0, 200, 0)
        if _next_question_ready is False:
            return "WAIT", (220, 40, 40)
        return "KEY1 READY  KEY3 WAIT", "yellow"
    if _ws_game_state == "active" and _ws_question_phase == "complete":
        return "ROUNDS COMPLETE", "yellow"
    if _ws_game_state == "completed" and (
        _game_end_outcome == "ended" or _game_end_outcome is None
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
            # (e.g. JOIN? KEY1) overlays the top when an action is required.
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
            draw_network_indicator()
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

    # === Network indicator (left) and battery indicator (right) ===
    draw_network_indicator()
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
print(
    f"[PAIR] strict pairing enabled — PAIR_NAME='{PAIR_NAME}', "
    f"BADGE_NAMES={BADGE_NAMES}, targets={TARGET_DEVICE_NAMES}"
)
print("Joystick: Navigate menus")
print("KEY1: Select positive; in game lobby press to join")
print("KEY2: Navigate/confirm; exit game/fullscreen to menu select")
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

            print("[BLE] startup — queueing per-slot POST /api/status", flush=True)
            _post_roster_status("scanning")

            # Load the NFC card mapping from the server (falls back to the
            # built-in map if unreachable). Done here on the BLE thread so the
            # blocking GET never stalls the UI loop.
            load_nfc_card_map()

            async def _initial_connect():
                global _heartbeat_task
                await ble_controller.scan_and_connect_roster(timeout=5)
                if _heartbeat_task is None or _heartbeat_task.done():
                    _heartbeat_task = asyncio.create_task(_heartbeat_loop())
                asyncio.create_task(_roster_maintain_loop())

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
        # Redraw when the background network monitor detects a state change.
        # Defer during an animation so the status redraw does not overwrite it.
        if _network_indicator_dirty and not animation_running:
            _network_indicator_dirty = False
            draw_display()

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
            # Game mode: KEY1 joins a lobby or confirms readiness between rounds.
            if game_mode_active:
                if _respond_to_ready_prompt(True):
                    pass
                elif _join_pending and _ws_game_id:
                    _join_pending = False
                    _ws_joined    = True
                    # Each connected badge joins as its own player; badges that
                    # connect later auto-join in _sync_badge_game_state.
                    _post_join(_key1_join_badges(), "KEY1")
                    draw_display()
                    if ble_event_loop is not None:
                        asyncio.run_coroutine_threadsafe(
                            _ble_write_game_cmd("GAME:lobby_joined"),
                            ble_event_loop,
                        )
                time.sleep(0.2)
                button_states['key1'] = key1_pressed
                continue

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
            # Game mode: KEY2 exits to menu select (does not join — that is KEY1).
            if game_mode_active:
                _exit_game_mode_to_menu()
                time.sleep(0.2)
                button_states['key2'] = key2_pressed
                continue

            # Full-screen selected emoji: KEY2 exits to menu + status layout.
            if fullscreen_mode and not nfc_mode_active:
                fullscreen_mode = False
                state = "start"
                draw_display()
                print('KEY2 - Exit fullscreen to menu select')
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
            # Game mode: KEY3 asks the referee to wait between rounds.
            if game_mode_active:
                _respond_to_ready_prompt(False)
                time.sleep(0.2)
                button_states['key3'] = key3_pressed
                continue

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
