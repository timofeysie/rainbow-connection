# Raspberry Pi Pico Emoji Badge Setup

A sample pair_config.py file can be found in the emoji-os directory:

rainbow-connection\python\emoji-os\pair_config.py

```py
PAIR_NAME = "white"
```

This name needs to match a name in the controller pair_config.py file.

## Required files

rainbow-connection\python\emoji-os\emoji-os-pico.py
rainbow-connection\python\emoji-os\emojis.py
rainbow-connection\python\emoji-os\large_image.py
rainbow-connection\python\emoji-os\ble_advertising.py

These depend on the following libraries installed on the pico:

- piicodev
- glowbit
