# Emoji OS Zero Product Requirements

Emoji OS is a simple menu system that allows you to switch between emojis.

The first version was built for a Raspberry Pi Pico with a GlowBit 8x8 matrix LED and three connected buttons.

The Emoji OS Zero will be designed for a Raspberry Pi Zero 2 W with a Waveshare 1.44inch LCD display HAT.

The demo code from Waveshare demonstrates the joystick, button and display features of the LCD HAT.

This is the [key_demo.py](https://github.com/Kudesnick/1.44inch-LCD-HAT-Code/blob/main/python/key_demo.py) code.

```py
# -*- coding:utf-8 -*-
import LCD_1in44
import LCD_Config

import RPi.GPIO as GPIO

import time
from PIL import Image,ImageDraw,ImageFont,ImageColor

KEY_UP_PIN     = 6 
KEY_DOWN_PIN   = 19
KEY_LEFT_PIN   = 5
KEY_RIGHT_PIN  = 26
KEY_PRESS_PIN  = 13
KEY1_PIN       = 21
KEY2_PIN       = 20
KEY3_PIN       = 16

#init GPIO
GPIO.setmode(GPIO.BCM) 
GPIO.cleanup()
GPIO.setup(KEY_UP_PIN,      GPIO.IN, pull_up_down=GPIO.PUD_UP)    # Input with pull-up
GPIO.setup(KEY_DOWN_PIN,    GPIO.IN, pull_up_down=GPIO.PUD_UP)  # Input with pull-up
GPIO.setup(KEY_LEFT_PIN,    GPIO.IN, pull_up_down=GPIO.PUD_UP)  # Input with pull-up
GPIO.setup(KEY_RIGHT_PIN,   GPIO.IN, pull_up_down=GPIO.PUD_UP) # Input with pull-up
GPIO.setup(KEY_PRESS_PIN,   GPIO.IN, pull_up_down=GPIO.PUD_UP) # Input with pull-up
GPIO.setup(KEY1_PIN,        GPIO.IN, pull_up_down=GPIO.PUD_UP)      # Input with pull-up
GPIO.setup(KEY2_PIN,        GPIO.IN, pull_up_down=GPIO.PUD_UP)      # Input with pull-up
GPIO.setup(KEY3_PIN,        GPIO.IN, pull_up_down=GPIO.PUD_UP)      # Input with pull-up

# 240x240 display with hardware SPI:
disp = LCD_1in44.LCD()
Lcd_ScanDir = LCD_1in44.SCAN_DIR_DFT  #SCAN_DIR_DFT = D2U_L2R
disp.LCD_Init(Lcd_ScanDir)
disp.LCD_Clear()

# Create blank image for drawing.
# Make sure to create image with mode '1' for 1-bit color.
width = 128
height = 128
image = Image.new('RGB', (width, height))

# Get drawing object to draw on image.
draw = ImageDraw.Draw(image)

# Draw a black filled box to clear the image.
draw.rectangle((0,0,width,height), outline=0, fill=0)
disp.LCD_ShowImage(image,0,0)

# try:
while 1:
    # with canvas(device) as draw:
    if GPIO.input(KEY_UP_PIN) == 0: # button is released       
        draw.polygon([(20, 20), (30, 2), (40, 20)], outline=255, fill=0xff00)  #Up        
        print('Up')        
    else: # button is pressed:
        draw.polygon([(20, 20), (30, 2), (40, 20)], outline=255, fill=0)  #Up filled
        
    if GPIO.input(KEY_LEFT_PIN) == 0: # button is released
        draw.polygon([(0, 30), (18, 21), (18, 41)], outline=255, fill=0xff00)  #left
        print('left')        
    else: # button is pressed:       
        draw.polygon([(0, 30), (18, 21), (18, 41)], outline=255, fill=0)  #left filled
        
    if GPIO.input(KEY_RIGHT_PIN) == 0: # button is released
        draw.polygon([(60, 30), (42, 21), (42, 41)], outline=255, fill=0xff00) #right
        print('right')
    else: # button is pressed:
        draw.polygon([(60, 30), (42, 21), (42, 41)], outline=255, fill=0) #right filled       
        
    if GPIO.input(KEY_DOWN_PIN) == 0: # button is released
        draw.polygon([(30, 60), (40, 42), (20, 42)], outline=255, fill=0xff00) #down
        print('down')
    else: # button is pressed:
        draw.polygon([(30, 60), (40, 42), (20, 42)], outline=255, fill=0) #down filled
        
    if GPIO.input(KEY_PRESS_PIN) == 0: # button is released
        draw.rectangle((20, 22,40,40), outline=255, fill=0xff00) #center 
        print('center')
    else: # button is pressed:
        draw.rectangle((20, 22,40,40), outline=255, fill=0) #center filled
        
    if GPIO.input(KEY1_PIN) == 0: # button is released
        draw.ellipse((70,0,90,20), outline=255, fill=0xff00) #A button
        print('KEY1')
    else: # button is pressed:
        draw.ellipse((70,0,90,20), outline=255, fill=0) #A button filled
        
    if GPIO.input(KEY2_PIN) == 0: # button is released
        draw.ellipse((100,20,120,40), outline=255, fill=0xff00) #B button]
        print('KEY2')
    else: # button is pressed:
        draw.ellipse((100,20,120,40), outline=255, fill=0) #B button filled
        
    if GPIO.input(KEY3_PIN) == 0: # button is released
        draw.ellipse((70,40,90,60), outline=255, fill=0xff00) #A button
        print('KEY3')
    else: # button is pressed:
        draw.ellipse((70,40,90,60), outline=255, fill=0) #A button filled
    disp.LCD_ShowImage(image,0,0)
# except:
	# print('except')
    # GPIO.cleanup()
```

I want to create a new version of this file which removes the Bluetooth and nfc features from the emoji-os-pico.py code, and just creates the menu and emoji switching functionality using the above code methods.
We do not want to install any new libraries.

This file also depends on another python\emojis\emojis.py which we will handle next.

Can you please create a new file called emoji-os-zero.py which is a copy of the emoji-os-pico.py file, but with the Bluetooth and nfc features removed.  It must use the same code methods as the key_demo.py file.

## The menu

The emoji-os-pico.py version relies on three buttons to control a menu and select an emoji.

In this version, the middle button 

button1 = pos (positive emojis)
button2 = menu (menu position)
button3 = neg (negative emojis)

The middle menu button2 moves the selected emoji category represented by four positions.  If the user goes past the end of the list it starts from the beginning again.

The categories are

1. Emojis
2. Animations
3. Characters
4. Symbols

Each category has a range of images to draw.  The first category, emojis, has four positive emojis like a smiley face, and the negative emojis has four negative emojis like a frowning face.

The new emoji-os-zero.py file will use a similar setup, but the menu can go up or down with the joystick instead of just one direction.
