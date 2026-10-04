# Raspberry Pi Pico Emoji Badge Setup

Copy a `pair_config.py` onto the Pico next to `emoji-os-pico.py`. A sample
lives at `rainbow-connection/python/emoji-os/pair_config.py`. The Pico only
reads `PAIR_NAME` — do not copy the controller's `BADGE_NAMES` onto the badge.

Mode 1 — same name as the Zero:

```python
PAIR_NAME = "white"
```

Mode 2 — unique name that appears in the Zero's `BADGE_NAMES` roster:

```python
PAIR_NAME = "white-2"
```

That Pico advertises as `Pico-Client-white-2` and expects `PAIR:white-2`.
The controller `pair_config.py` must include this name:

```python
PAIR_NAME = "white"
BADGE_NAMES = ["white", "white-2"]
```

Name rules:

- Names are case-sensitive and must match the Zero roster exactly.
- Keep names short. Long `Pico-Client-<PAIR_NAME>` advertising names are
  truncated and the Zero will not find the badge.
- A Pico whose name is not in any Zero's `BADGE_NAMES` is never connected.

## Buttonless badges

A Mode 2 badge does not need buttons. The Zero is the only input device:

- The Zero connects to the badge on its own (no badge key press).
- Emoji chosen on the Zero appear on every connected badge.
- The player joins once from the Zero (`KEY1`); every badge shows the lobby,
  question, and result states.
- A badge powered on mid-game is synced to the current state (e.g. `?` while
  a question is open).
- Any connected badge can scan an NFC card. The first scan of a question is
  the station's answer; later scans from sibling badges in the same question
  are rejected and do not change it.

The badge firmware is the same `emoji-os-pico.py` for Mode 1 and Mode 2.

## Check the badge connected

On the Zero log, look for the badge's name:

```text
[BLE] connecting badgeName='white-2' at 28:CD:C1:...
[PAIR] sent 'PAIR:white-2' to 'white-2'
[PAIR] OK — paired badgeName='white-2' picoVersion='0.4.0'
```

In emoji-app **Badges**, the station card shows a `white-2` slot as
`connected` with the Pico version. A roster name with no powered badge reads
**not connected**.

## Required files

rainbow-connection\python\emoji-os\emoji-os-pico.py
rainbow-connection\python\emoji-os\emojis.py
rainbow-connection\python\emoji-os\large_image.py
rainbow-connection\python\emoji-os\ble_advertising.py

These depend on the following libraries installed on the pico:

- piicodev
- glowbit
