# Emoji Badge Controller Setup

(using original notes from docs\emoji-badge-controller-setup.md)

Setting up an emoji badge controller on a Raspberry Pi Zero W with a [Waveshare 1.44inch LCD display HAT](https://www.waveshare.com/wiki/1.44inch_LCD_HAT) involves a number of steps such as ensuring certain libraries are installed, and getting a python script on the device running on startup.

This guide does not cover the basics of setting up and working with a Raspberry Pi.  The below instructions assume a Raspberry Pi Zero W with a Waveshare 1.44inch LCD display HAT installed and are able to access the terminal.  The UPS HAT is also optional for a portable controller.  The 32-bit Raspbian OS should be loaded on an SSD card.

The current repository for the code in this project is: [https://github.com/timofeysie/rainbow-connection](https://github.com/timofeysie/rainbow-connection).

You can setup the UPS HAT first, or the display, it shouldn't matter.  I will cover the UPS HAT first but skip ahead if you want to setup the display and test that first.

## [Waveshare 1.44inch LCD display HAT setup](https://www.waveshare.com/wiki/1.44inch_LCD_HAT)

The are the instructions from the link the last time I did this.

Open terminal, use command to enter the configuration page

sudo raspi-config

Choose Interfacing Options -> SPI -> Yes  to enable SPI interface

Reboot Raspberry Pi：

sudo reboot

Note: *If you use bookworm system, only the lgpio library is available, bcm2835 and wiringPi libarary cannot be installed or used.*

I think I am running the version after bookworm.  This is how to check:

```sh
tim@zero2:~ $ cat /etc/os-release
PRETTY_NAME="Raspbian GNU/Linux 13 (trixie)"
NAME="Raspbian GNU/Linux"
VERSION_ID="13"
VERSION="13 (trixie)"
VERSION_CODENAME=trixie
DEBIAN_VERSION_FULL=13.4
ID=raspbian
ID_LIKE=debian
HOME_URL="http://www.raspbian.org/"
SUPPORT_URL="http://www.raspbian.org/RaspbianForums"
BUG_REPORT_URL="http://www.raspbian.org/RaspbianBugs"
```

So yes, I was wrong.  I am running the latest Trixie.  Today is June 30, 2026.

Bookworm was released 2023-10-10
Trixi was release 2025-10-01.

In that case we skip bcm2835 and wiringPi installation and jump to lgpio.

```sh
sudo su
wget https://github.com/joan2937/lg/archive/master.zip
unzip master.zip
cd lg-master
sudo make install 
# For more information, please refer to the official website: https://github.com/gpiozero/lg
```

Then Python

```sh
sudo apt-get update
sudo apt-get install python3-pip
sudo apt-get install python3-pil
sudo apt-get install python3-numpy
sudo pip3 install spidev
```

The last line fails:

```sh
tim@zero2:~ $ sudo pip install spidev
error: externally-managed-environment

× This environment is externally managed
╰─> To install Python packages system-wide, try apt install
    python3-xyz, where xyz is the package you are trying to
    install.
    
    If you wish to install a non-Debian-packaged Python package,
    create a virtual environment using python3 -m venv path/to/venv.
    Then use path/to/venv/bin/python and path/to/venv/bin/pip. Make
    sure you have python3-full installed.
    
    For more information visit http://rptl.io/venv

note: If you believe this is a mistake, please contact your Python installation or OS distribution provider. You can override this, at the risk of breaking your Python installation or OS, by passing --break-system-packages.
hint: See PEP 668 for the detailed specification.
tim@zero2:~ $ sudo apt-get install spidev
Reading package lists... Done
Building dependency tree... Done
Reading state information... Done
E: Unable to locate package spidev
```

The problem with uses venv (a virtual environment for python) is that is the scripts that depend on it then must also run in the venv.
We want the script to run at startup from rc.local, so for now, it's easier to follow the this:

```sh
tim@zero2:~ $ sudo pip3 install spidev --break-system-packages
Looking in indexes: https://pypi.org/simple, https://www.piwheels.org/simple
Requirement already satisfied: spidev in /usr/lib/python3/dist-packages (3.6)
WARNING: Running pip as the 'root' user can result in broken permissions and conflicting behaviour with the system package manager, possibly rendering your system unusable. It is recommended to use a virtual environment instead: https://pip.pypa.io/warnings/venv. Use the --root-user-action option if you know what you are doing and want to suppress this warning.
```

So not needed anyway.

### Download Examples

This could be an optional step, but good to test the display without our software to make sure the equipmrny works, because it doesn't always.

```sh
sudo apt-get install p7zip-full -y
wget https://files.waveshare.com/upload/f/fa/1.44inch-LCD-HAT-Code.7z
7z x 1.44inch-LCD-HAT-Code.7z
sudo chmod 777 -R 1.44inch-LCD-HAT-Code
cd 1.44inch-LCD-HAT-Code/RaspberryPi/
```

## Clone the emoji-os repo

```sh
mkdir repos
cd repos
git clone https://github.com/timofeysie/rainbow-connection.git
```

## Install Bleak

To run the emoji-os-zero.py, you need to install the bleak library.
Bleak is a library for Bluetooth Low Energy (BLE) communication in Python.

```sh
To run the nfc-zero-with-pairing.py file, you need to install the bleak library. Bleak is a library for Bluetooth Low Energy (BLE) communication in Python.

sudo apt install python3-bleak
```

To try out the pairing and NFC card reading, navigate to the following directory and run the example script:

```sh
cd /home/tim/repos/rainbow-connection/python/tests
python nfc-zero-with-pairing.py
```

## Setup emoji-os-zero to run on startup

Open the rc.local file with the nano editor:

```sh
sudo nano /etc/rc.local
```

Past the following text into the nano editor:

```
#!/bin/sh -e

sleep 10

echo "=== rc.local starting ===" >> /home/tim/rc.local.log
echo "Running emoji_os_zero_1.py..." >> /home/tim/rc.local.log

/usr/bin/python3 /home/tim/repos/rainbow-connection/python/emoji-os/emoji_os_zero.py >> /home/tim/rc.local.log 2>&1

echo "=== rc.local done ===" >> /home/tim/rc.local.log

exit 0
```

You will need to modify the path to this file if you are not Tim.

I check the file is executable again:

```sh
sudo chmod +x /etc/rc.local
sudo chmod +x /home/tim/repos/rainbow-connection/python/emoji-os/emoji-os-zero.py
```

Then reboot.  If you have issues, check the log listed in the rc.local file (home/tim/rc.local.log).

Copty the pair_config.py to the repose directory.
This file can be found in the repos/rainbow-connection/python/emoji-os/pair_config.py file.

Give the controller a name:

```sh
PAIR_NAME = "my-name"
```

This should be the same as a pico badge so that they can pair together.
