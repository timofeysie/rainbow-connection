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

## Progressive enhancement approach

We know that python key_demo.py runs.  I draws on the lcd display as well as uses the joystick and buttons without error.  This is our working position.

Then we have the two other aspects of the project that we should implement step by step into this working position.

1. python key_demo.py runs.  I draws on the lcd display as well as uses the joystick and buttons
2. drawing the main emoji and the emoji selecting menu and sub-menus in emoji_key_basic.py.
3. listening to the joystick and buttons and navigating the menu logic in smiley-matrix-4.py.

What we need to do is take main emoji from the smiley-matrix-4b.py file and implement it in the key_demo.py file.

This should take the emoji and draw it at the bottom half of the lcd display and the current joystick and button code draws the shapes in the top half.

Lets call this first step key_demo_with_emoji.py.

Progressive enhancement approach

We know that python key_demo.py runs.  I draws on the lcd display as well as uses the joystick and buttons without error.  This is our working position.

Then we have the two other aspects of the project that we should implement step by step into this working position.

1. python key_demo.py runs.  I draws on the lcd display as well as uses the joystick and buttons
2. drawing the main emoji and the emoji selecting menu and sub-menus in emoji_key_basic.py.
3. listening to the joystick and buttons and navigating the menu logic in smiley-matrix-4.py.

What we need to do is take main emoji from the smiley-matrix-4b.py file and implement it in the key_demo.py file.

This should take the emoji and draw it at the bottom half of the lcd display and the current joystick and button code draws the shapes in the top half.

Lets call this first step key_demo_with_emoji.py.

Commit message: use same GPIO setup as key_demo.py and add main emoji drawing functionality from smiley-matrix-4b.py

When running that code on the device, I see this error:

```sh
tim@raspberrypi:~/emoji-os $ python key_demo_with_emoji.py
/usr/lib/python3/dist-packages/RPi/GPIO/__init__.py:622: Warning: No channels have been set up yet - nothing to clean up!  Try cleaning up at the end of your program instead!
  warnings.warn(Warning(
Traceback (most recent call last):
  File "/usr/lib/python3/dist-packages/RPi/GPIO/__init__.py", line 393, in _gpio_list
    return tuple(_to_gpio(int(channel)) for channel in chanlist)
                ^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^
TypeError: 'int' object is not iterable

During handling of the above exception, another exception occurred:

Traceback (most recent call last):
  File "/home/tim/emoji-os/key_demo_with_emoji.py", line 20, in <module>
    GPIO.setup(KEY_UP_PIN,      GPIO.IN, pull_up_down=GPIO.PUD_UP)    # Input with pull-up
    ^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^
  File "/usr/lib/python3/dist-packages/RPi/GPIO/__init__.py", line 680, in setup
    for gpio in _gpio_list(chanlist):
                ^^^^^^^^^^^^^^^^^^^^
  File "/usr/lib/python3/dist-packages/RPi/GPIO/__init__.py", line 396, in _gpio_list
    return (_to_gpio(int(chanlist)),)
            ^^^^^^^^^^^^^^^^^^^^^^^
  File "/usr/lib/python3/dist-packages/RPi/GPIO/__init__.py", line 356, in _to_gpio
    raise RuntimeError(
RuntimeError: Please set pin numbering mode using GPIO.setmode(GPIO.BOARD) or GPIO.setmode(GPIO.BCM)
```

## Adding all the emojis

Add all the things!

In the python\emoji-os\emoji-os-pico.py script we import ```from emojis import *``` from python\emojis\emojis.py file to get functions like ```def regular():``` which can be used to draw particular emojis.

Currently we are using the same emoji for every menu position.  We want to change this to use specific emojis for each menu position.

When a specific menu is chose from the left or the right sub-menu in python\zero\key_demo_v9.py, we want to also replace the main emoji with the large version of that.  For example, main menu position 0 has pos (positive or left side sub-menu), there are four emojis:

Positive emojis:

- regular()
- happy()
- wry()
- heartBounce()

Negative emojis:

- thickLips()
- sad()
- angry()
- greenMonster()

Here is the code:

```py
    #==========
    #POSITIVE 0
    # regular
    if (menu == 0 and pos == 1):
        print("menu 0 pos 1 normal")
        regular()
    # happy
    if (menu == 0 and pos == 2):
        print("menu 0 pos 2 happy")
        happy()
    # wry
    if (menu == 0 and pos == 3):
        print("menu 0 pos 3 wry")
        wry()
    # heart bounce
    if (menu == 0 and pos == 4):
        print("menu 0 pos 4 heart bounce")
        heartBounce()
    # NEGATIVE 0
    # thick lips
    if (menu == 0 and neg == 1):
        print("menu 0 neg 1 thick lips")
        thickLips()
    # sad
    if (menu == 0 and neg == 2):
        print("menu 0 neg 2 sad")
        sad()
    # angry
    if (menu == 0 and neg == 3):
        print("menu 0 neg 3 angry")
        angry()
    # monster
    if (menu == 0 and neg == 4):
        print("menu 0 neg 4 green monster")
        greenMonster()
    #==========
```

Lets add the functionality to python\zero\key_demo_v9.py to draw the emojis for the main menu first option "Emojis" left side and right side sub-menu and draw the selected emoji as the main emoji.  Please create a emoji_os_zero_1.py file to do this.
