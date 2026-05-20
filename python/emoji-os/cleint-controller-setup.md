# Client Controller Setup

Current working client demo: python controller-1.3.py.

## Controller Setup

On a Raspberry Pi Zero W with a Waveshare 1.44inch LCD display HAT, we will set up a client controller to control the emoji-os-zero.py program.

Requirements:

- git

### Install git

TO install git, run:
```sh
sudo apt-get install git
```

### Setup auto-start

Edit the rc.local:

```sh
sudo nano /etc/rc.local
```

To test Emoji OS on the Raspberry Pi Zero W, run:

cd repos/rainbow-connection/python/emoji-os
python emoji-os-zero-0.3.0.py

The rc.local file should look like this:

```shell
  GNU nano 7.2                      /etc/rc.local                               
#!/bin/sh -e

sleep 10


echo "=== rc.local starting ===" >> /home/tim/rc.local.log

echo "at $(/bin/date) ===" >> /home/tim/rc.local.log;

echo "Running emoji_os_zero v0.3.7" >> /home/tim/rc.local.log

/usr/bin/python /home/tim/repos/rainbow-connection/python/emoji-os/emoji-os-zer>

echo "=== rc.local done ===" >> /home/tim/rc.local.log
```

## Pico Client setup

On a Raspberry Pi Pico 2 W, we will set up a client to connect to the Raspberry Pi Zero W via Bluetooth.

Use Thonny to install the OS for a Raspberry Pi Pico 2 W.

Install the glowbit library and the below required files:

The glowbit 8x8 matrix can be tested with the script python\tests\test-glowbit-circle.py

### Required files

- emoji-os.py (saved as main.py, currently emoji os v0.2.2)
- emojis.py
- large_image.py
- ble_advertising.py

## Multiplayer Pairing (PAIR\_NAME)

Each controller/badge pair uses a shared `PAIR_NAME` so that multiple pairs can
operate in the same room without interfering with each other.  The default value
is `"default"`, which is fine for a single-pair setup.

Both sides read `PAIR_NAME` from an optional `pair_config.py` file placed next
to the main script.  If the file is absent the default is used.

### Pico — set PAIR\_NAME

On the Pico, create `pair_config.py` (place it in the same folder as `main.py`)
with the following content, substituting your chosen name:

```python
PAIR_NAME = "living-room"
```

Upload the file to the Pico via Thonny alongside the other required files.

### Zero controller — set PAIR\_NAME

On the Raspberry Pi Zero W, create `pair_config.py` next to `emoji-os-zero.py`:

```python
PAIR_NAME = "living-room"
```

Both files must use the **same** `PAIR_NAME` value.  The Zero advertises a BLE
device named `Pico-Client-<PAIR_NAME>` and the Pico will only accept a
connection handshake from a controller that sends the matching name.

> **Tip:** use a short, URL-safe string with no spaces, e.g. `"living-room"`,
> `"kitchen"`, or `"badge-1"`.

See `python/emoji-os/project/multiplayer-mode.md` for the full design.
