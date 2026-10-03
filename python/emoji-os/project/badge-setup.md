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

## Required files

rainbow-connection\python\emoji-os\emoji-os-pico.py
rainbow-connection\python\emoji-os\emojis.py
rainbow-connection\python\emoji-os\large_image.py
rainbow-connection\python\emoji-os\ble_advertising.py

These depend on the following libraries installed on the pico:

- piicodev
- glowbit
