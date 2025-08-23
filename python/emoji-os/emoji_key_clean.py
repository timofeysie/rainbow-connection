# -*- coding:utf-8 -*-
# emoji_key_clean.py - Clean version that exactly matches key_demo.py structure

import LCD_1in44
import LCD_Config
import RPi.GPIO as GPIO
import time
from PIL import Image, ImageDraw, ImageFont, ImageColor

KEY_UP_PIN     = 6 
KEY_DOWN_PIN   = 19
KEY_LEFT_PIN   = 5
KEY_RIGHT_PIN  = 26
KEY_PRESS_PIN  = 13
KEY1_PIN       = 21
KEY2_PIN       = 20
KEY3_PIN       = 16

#init GPIO - EXACTLY like key_demo.py
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

# 128x128 display with hardware SPI - EXACTLY like key_demo.py
disp = LCD_1in44.LCD()
Lcd_ScanDir = LCD_1in44.SCAN_DIR_DFT  #SCAN_DIR_DFT = D2U_L2R
disp.LCD_Init(Lcd_ScanDir)
disp.LCD_Clear()

# Create blank image for drawing - EXACTLY like key_demo.py
width = 128
height = 128
image = Image.new('RGB', (width, height))
draw = ImageDraw.Draw(image)

# Draw a black filled box to clear the image - EXACTLY like key_demo.py
draw.rectangle((0,0,width,height), outline=0, fill=0)
disp.LCD_ShowImage(image,0,0)

# Menu state variables
menu = 0
pos = 0
neg = 0
state = "none"

def draw_menu():
    """Draw the menu on the left side"""
    # Clear left side
    draw.rectangle((0, 0, 63, 127), outline=0, fill=0)
    
    # Draw menu title
    draw.text((5, 5), "MENU", fill=255)
    
    menu_names = ["Emojis", "Animations", "Characters", "Symbols"]
    
    for i in range(4):
        y_pos = 25 + (i * 20)
        if i == menu:
            # Highlight selected menu
            draw.rectangle((2, y_pos-2, 60, y_pos+15), outline=255, fill=0)
            draw.text((5, y_pos), f"{i}: {menu_names[i]}", fill=255)
        else:
            draw.text((5, y_pos), f"{i}: {menu_names[i]}", fill=128)
    
    # Draw selection info
    if state == "choosing":
        if pos > 0:
            draw.text((5, 110), f"POS: {pos}", fill=0x00ff00)
        elif neg > 0:
            draw.text((5, 110), f"NEG: {neg}", fill=0xff0000)

def draw_emoji():
    """Draw emoji on the right side"""
    # Clear right side
    draw.rectangle((64, 0, 127, 127), outline=0, fill=0)
    
    if menu == 0 and pos == 1:
        # Simple smiley face
        draw.ellipse((80, 40, 112, 88), outline=255, fill=0)  # Face
        draw.ellipse((88, 50, 96, 58), outline=255, fill=255)  # Left eye
        draw.ellipse((104, 50, 112, 58), outline=255, fill=255)  # Right eye
        draw.arc((88, 60, 104, 76), 0, 180, fill=255, width=2)  # Smile

# Main loop - EXACTLY like key_demo.py structure
print("Emoji OS Zero started!")
print("Use joystick to navigate, buttons to select")

while True:
    # Check joystick inputs - EXACTLY like key_demo.py
    if GPIO.input(KEY_UP_PIN) == 0:  # Up pressed
        if state == "none":
            state = "start"
        elif state == "start":
            menu = (menu - 1) % 4
        print('Up - Menu:', menu)
        draw_menu()
        disp.LCD_ShowImage(image,0,0)
        time.sleep(0.2)
        
    elif GPIO.input(KEY_DOWN_PIN) == 0:  # Down pressed
        if state == "none":
            state = "start"
        elif state == "start":
            menu = (menu + 1) % 4
        print('Down - Menu:', menu)
        draw_menu()
        disp.LCD_ShowImage(image,0,0)
        time.sleep(0.2)
        
    elif GPIO.input(KEY_LEFT_PIN) == 0:  # Left pressed
        if state == "choosing":
            neg = (neg + 1) % 5
            if neg == 0: neg = 1
            pos = 0
        print('Left - Negative:', neg)
        draw_menu()
        disp.LCD_ShowImage(image,0,0)
        time.sleep(0.2)
        
    elif GPIO.input(KEY_RIGHT_PIN) == 0:  # Right pressed
        if state == "choosing":
            pos = (pos + 1) % 5
            if pos == 0: pos = 1
            neg = 0
        print('Right - Positive:', pos)
        draw_menu()
        disp.LCD_ShowImage(image,0,0)
        time.sleep(0.2)
        
    elif GPIO.input(KEY_PRESS_PIN) == 0:  # Center pressed
        if state == "start":
            state = "choosing"
            pos = 1
            neg = 0
        elif state == "choosing":
            draw_emoji()
        print('Center pressed')
        draw_menu()
        disp.LCD_ShowImage(image,0,0)
        time.sleep(0.2)
        
    # Check button inputs - EXACTLY like key_demo.py
    elif GPIO.input(KEY1_PIN) == 0:  # KEY1 pressed
        if state == "choosing":
            pos = (pos + 1) % 5
            if pos == 0: pos = 1
            neg = 0
        elif state == "start":
            state = "choosing"
            pos = 1
            neg = 0
        print('KEY1 - Positive:', pos)
        draw_menu()
        disp.LCD_ShowImage(image,0,0)
        time.sleep(0.2)
        
    elif GPIO.input(KEY2_PIN) == 0:  # KEY2 pressed
        if state == "start":
            menu = (menu + 1) % 4
        elif state == "none":
            state = "start"
        elif state == "choosing":
            draw_emoji()
        print('KEY2 - Menu:', menu)
        draw_menu()
        disp.LCD_ShowImage(image,0,0)
        time.sleep(0.2)
        
    elif GPIO.input(KEY3_PIN) == 0:  # KEY3 pressed
        if state == "choosing":
            neg = (neg + 1) % 5
            if neg == 0: neg = 1
            pos = 0
        elif state == "start":
            state = "choosing"
            neg = 1
            pos = 0
        print('KEY3 - Negative:', neg)
        draw_menu()
        disp.LCD_ShowImage(image,0,0)
        time.sleep(0.2)
    
    # Update display - EXACTLY like key_demo.py
    disp.LCD_ShowImage(image,0,0)
    time.sleep(0.1)
