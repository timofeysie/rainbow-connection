# Emoji OS Zero Notes

Just in case something happens, here are some notes from the zero to help with the 'challenging' dev environment.

## Work so far

The python\emoji-os\emoji_key_basic.py file had the menu behavior working to listen to events and choose an emoji, but it only shows on the terminal, not on the lcd display.

The smiley-matrix-4.py file has the working emoji with hardwired menu and small version where the options will go.

Next, we want to listen to joystick/button events and move a selected

## Zero Controller Project

https://www.waveshare.com/wiki/1.44inch_LCD_HAT

python emoji-os-zero.py

python emoji_key.py

python emoji_key_basic.py <- this menu works but no lcd display

python smiley-matrix-4.py <- emoji, menu emojis and menu text
needs menu navigation and emoji select  and update options

https://stackblitz.com/github/timofeysie/rainbow-connection/blob/master/python/emoji-os/emoji-os-zero.py

## Initial prompt

I have a Waveshare 1.44inch LCD display HAT for Raspberry Pi.
It is connected to my Raspberry pi 5 B.

I have followed the instruction in this wiki to set it up:
https://www.waveshare.com/wiki/1.44inch_LCD_HAT which include doing this:

```sh
sudo apt-get install python3-pip
sudo apt-get install python3-pil
sudo apt-get install python3-numpy
sudo pip3 install spidev
```

In this wiki it says:
'If you use bookworm system, only the lgpio library is available,
bcm2835 and wiringPi libarary cannot be installed or used.
Please note that the python library does not need to be installed,
you can directly run the demo'

$ cat /etc/os-release
PRETTY_NAME="Debian GNU/Linux 12 (bookworm)"
NAME="Debian GNU/Linux"
VERSION_ID="12"
VERSION="12 (bookworm)"
VERSION_CODENAME=bookworm
ID=debian
HOME_URL="https://www.debian.org/"
SUPPORT_URL="https://www.debian.org/support"
BUG_REPORT_URL="https://bugs.debian.org/"

I run these instructions from the wiki:
sudo apt-get update
sudo apt-get install python3-pip
sudo apt-get install python3-pil
sudo apt-get install python3-numpy
sudo pip3 install spidev

sudo apt-get install p7zip-full -y
wget https://files.waveshare.com/upload/f/fa/1.44inch-LCD-HAT-Code.7z
7z x 1.44inch-LCD-HAT-Code.7z
sudo chmod 777 -R 1.44inch-LCD-HAT-Code
cd 1.44inch-LCD-HAT-Code/RaspberryPi/

cd python
sudo python main.py
sudo python key_demo.py

I want this script to run on Raspberry pi startup so that I can test that it will run on a Raspberry pi Zero W also with a Waveshare 1.44inch LCD display HAT.

In this way, I want to take the SSD card out of the Raspberry Pi 5 B and put it in the Zero and test that it will also work there.

/home/tim/1.44inch-LCD-HAT-Code/RaspberryPi/python/key_demo.py

Method 1: Using rc.local
/usr/bin/python /home/tim/1.44inch-LCD-HAT-Code/RaspberryPi/python/key_demo.py &

Save and exit by pressing Ctrl + X, then Y and Enter.

ps aux | grep key_demo.py

python smiley-matrix-4.py <- emoji, menu emojis and menu text

## Implementing the main menu

### Prompt start

I have a Waveshare 1.44inch LCD display HAT for Raspberry Pi.
It is connected to my Raspberry pi 5 B.

I have followed the instruction in this wiki to set it up:
https://www.waveshare.com/wiki/1.44inch_LCD_HAT which include doing this:

```sh
sudo apt-get install python3-pip
sudo apt-get install python3-pil
sudo apt-get install python3-numpy
sudo pip3 install spidev
```

The code we are working on shows a main emoji on the bottom of the screen, and a menu at the top with 4 options on the left and 4 options on the right.

## The laptop simulation

First I had to install Pillow.

```sh
pip install Pillow
```

I created a new version with a show_simulation function to show the lcd display on the laptop.

New script: python\zero\smiley-matrix-4b.py
