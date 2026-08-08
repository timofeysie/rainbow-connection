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

Both sides read `PAIR_NAME` from an optional `pair_config.py` file.  If no file
is found the default is used.

### Pico — set PAIR\_NAME

On the Pico, create `pair_config.py` (place it in the same folder as `main.py`)
with the following content, substituting your chosen name:

```python
PAIR_NAME = "living-room"
```

Upload the file to the Pico via Thonny alongside the other required files.
Because the Pico is updated by hand, leaving the file in place across firmware
copies is straightforward.

### Zero controller — set PAIR\_NAME

The Zero is updated via `git pull`, so the config lives **outside** the cloned
repo to avoid being overwritten.  The Zero looks one directory above the repo
root first (e.g. `/home/tim/repos/pair_config.py` when the repo is at
`/home/tim/repos/rainbow-connection/`), and falls back to a file co-located
with the script if no external file is found.

Recommended setup on the Zero:

```sh
echo 'PAIR_NAME = "living-room"' > ~/repos/pair_config.py
```

(Adjust the path to match wherever your `rainbow-connection/` clone lives —
`pair_config.py` should sit in that clone's parent directory.)

The file contents are just:

```python
PAIR_NAME = "living-room"
```

After setup, future `git pull` runs will leave `~/repos/pair_config.py`
untouched. If you previously had a `pair_config.py` inside
`python/emoji-os/`, you can revert it with `git checkout
python/emoji-os/pair_config.py` and the external file will take precedence.

The Zero prints the resolved location at startup so you can confirm which file
was loaded:

```text
[PAIR] PAIR_NAME='living-room' (loaded from /home/tim/repos/pair_config.py) — looking for 'Pico-Client-living-room'
```

Both Pico and Zero must use the **same** `PAIR_NAME` value.  The Pico
advertises a BLE device named `Pico-Client-<PAIR_NAME>` and only accepts a
connection handshake from a controller that sends the matching name.

> **Tip:** use a short, URL-safe string with no spaces, e.g. `"living-room"`,
> `"kitchen"`, or `"badge-1"`.

See `python/emoji-os/project/multiplayer-mode.md` for the full design.
