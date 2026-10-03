# Station identity sent to emoji-app (bind, join, guesses, scores).
PAIR_NAME = "power-cable"

# Pico PAIR_NAME values this Zero may connect to.
# Order is the dashboard slot order. Duplicate names are ignored.
# Omit or leave empty to keep Mode 1: roster = [PAIR_NAME].
#
# Mode 1 (one controller, one badge) — omit BADGE_NAMES, or list only the
# controller name:
#   BADGE_NAMES = ["white"]
#
# Mode 2 (one controller, many badges) — each Pico has its own pair_config.py
# whose PAIR_NAME appears in this list:
#   BADGE_NAMES = ["white", "white-2", "white-3"]
BADGE_NAMES = ["power-cable", "black"]

# Maps card UID → { name, display, slotLabel }
# slotLabel matches the AnswerOption slot labels in the game (A, B, C, D, E).
# This local map is used as the offline fallback when the server is unreachable.
# The server-fetched map (GET /api/nfc-cards) takes precedence when available.
NFC_CARD_MAP_LOCAL = {
    "5B:6F:B8:08": {"name": "R12 - Monkey", "display": "circle", "slotLabel": "A"},
    "DB:93:B7:08": {"name": "W3 - Clown",   "display": "x",      "slotLabel": "B"},
    "2B:73:B8:08": {"name": "12",    "display": "A", "slotLabel": "1"},
    "4B:71:B8:08": {"name": "11",   "display": "B",   "slotLabel": "2"},
    "DB:69:B8:08": {"name": "10",    "display": "C",  "slotLabel": "3"},
    "1B:5D:B8:08": {"name": "D", "display": "D",     "slotLabel": "4"},
    "CB:61:B8:08": {"name": "9",     "display": "E",     "slotLabel": "5"},
}