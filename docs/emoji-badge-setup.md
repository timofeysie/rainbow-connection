# Emoji Badge setup

These are the steps for setting up an emoji bade.

The current version supports an [8x8 GlowBit display](https://core-electronics.com.au/glowbit-matrix-8x8.html), an NFC reader and optionally "squishy" buttons.

## Required libraries

The Pico will require the following libraries installed:

- glowbit
- piicodev

Use the Thonny IDE to install the libraries.

## Required files

- emoji-os.py (saved as main.py)
- emojis.py
- large_image.py
- ble_advertising.py
- secrets.py

The files here come from the python directory in this repo.

Open the latest emoji-os.py and save that on the Pico as main.py

Open the emojis/emojis.py file and save that as the same name also in the root directory (even though in this project it is a sub-directory).

Currently the app also uses large_image Open the /emojis/large_image.py and save that on the pico.

For the NFC we will need a secrets file from /python/hidden/secrets.py.  This file should also be listed in the .gitignore file so that it is not checked in to the source

```py
ssid = '<wifi-name>'
password = '<wifi-password>'
```

We will also need ble_advertising.py for the Bluetooth code.
