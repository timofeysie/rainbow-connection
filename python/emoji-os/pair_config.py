PAIR_NAME = "white"

# Maps card UID → { name, display, slotLabel }
# slotLabel matches the AnswerOption slot labels in the game (A, B, C, D, E).
# This local map is used as the offline fallback when the server is unreachable.
# The server-fetched map (GET /api/nfc-cards) takes precedence when available.
NFC_CARD_MAP_LOCAL = {
    "5B:6F:B8:08": {"name": "R12 - Monkey", "display": "circle", "slotLabel": "A"},
    "DB:93:B7:08": {"name": "W3 - Clown",   "display": "x",      "slotLabel": "B"},
}