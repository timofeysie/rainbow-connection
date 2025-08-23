# -*- coding:utf-8 -*-
# emoji-menu.py - Emoji OS Zero with LCD display
# Combines working key_demo.py LCD structure with working emoji_key_basic.py menu logic

import LCD_1in44
import LCD_Config
import RPi.GPIO as GPIO
import time
from PIL import Image, ImageDraw, ImageFont, ImageColor

# GPIO pin definitions for Waveshare LCD HAT
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

# Get drawing object to draw on image - EXACTLY like key_demo.py
draw = ImageDraw.Draw(image)

# Draw a black filled box to clear the image - EXACTLY like key_demo.py
draw.rectangle((0,0,width,height), outline=0, fill=0)
disp.LCD_ShowImage(image,0,0)

# Menu state variables - FROM emoji_key_basic.py
menu = 0
pos = 0
neg = 0
state = "none"  # start, end, or none
# preserve the previous state for pos/neg flipping
prev_menu = 0
prev_pos = 0
prev_neg = 0
prev_state = "none"  # or done

def check_menu():
    global menu
    if menu > 3:
        menu = 0
    if menu < 0:
        menu = 3

def check_pos():
    global pos
    if pos > 4:
        pos = 1

def check_neg():
    global neg
    if neg > 4:
        neg = 1

def draw_menu_lcd():
    """Draw the menu on the left side of LCD"""
    global menu
    
    # Clear left side (0-63 pixels wide)
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

def draw_emoji_lcd():
    """Draw emoji on the right side of LCD"""
    # Clear right side (64-127 pixels wide)
    draw.rectangle((64, 0, 127, 127), outline=0, fill=0)
    
    if menu == 0 and pos == 1:
        # Simple smiley face
        draw.ellipse((80, 40, 112, 88), outline=255, fill=0)  # Face
        draw.ellipse((88, 50, 96, 58), outline=255, fill=255)  # Left eye
        draw.ellipse((104, 50, 112, 58), outline=255, fill=255)  # Right eye
        draw.arc((88, 60, 104, 76), 0, 180, fill=255, width=2)  # Smile
    elif menu == 0 and pos == 2:
        # Heart
        draw.ellipse((80, 40, 112, 88), outline=255, fill=0xff0000)  # Red heart
    elif menu == 1 and pos == 1:
        # Fireworks
        for i in range(8):
            angle = i * 45
            x = 96 + int(20 * (angle / 90))
            y = 64 + int(20 * (angle / 90))
            draw.line((96, 64, x, y), fill=0xff00ff, width=2)
    elif menu == 2 and pos == 1:
        # Star
        points = [(96, 40), (100, 60), (120, 60), (105, 75), (110, 95), (96, 80), (82, 95), (87, 75), (72, 60), (92, 60)]
        draw.polygon(points, outline=255, fill=0xffff00)
    elif menu == 3 and pos == 1:
        # Circle
        draw.ellipse((80, 40, 112, 88), outline=255, fill=0x0080ff)

def reset_state():
    """Reset the current state and store previous values"""
    global state, menu, pos, neg, prev_state, prev_menu, prev_pos, prev_neg
    prev_state = "done"
    prev_menu = menu
    prev_pos = pos
    prev_neg = neg
    state = "none"
    menu = 0
    pos = 0
    neg = 0

def reset_prev():
    """Reset the previous state values"""
    global prev_state, prev_menu, prev_pos, prev_neg
    prev_state = "none"
    prev_menu = 0
    prev_pos = 0
    prev_neg = 0

# Main loop - EXACTLY like key_demo.py structure
print("Emoji OS Zero started!")
print("Use joystick to navigate, buttons to select")

# Initial display
draw_menu_lcd()
disp.LCD_ShowImage(image,0,0)

while 1:
    # Check joystick inputs - EXACTLY like key_demo.py
    if GPIO.input(KEY_UP_PIN) == 0:  # Up pressed
        if state == "none":
            state = "start"
        elif state == "start":
            menu = (menu - 1) % 4
            check_menu()
        print('Up - Menu:', menu)
        draw_menu_lcd()
        disp.LCD_ShowImage(image,0,0)
        time.sleep(0.2)
        
    elif GPIO.input(KEY_DOWN_PIN) == 0:  # Down pressed
        if state == "none":
            state = "start"
        elif state == "start":
            menu = (menu + 1) % 4
            check_menu()
        print('Down - Menu:', menu)
        draw_menu_lcd()
        disp.LCD_ShowImage(image,0,0)
        time.sleep(0.2)
        
    elif GPIO.input(KEY_LEFT_PIN) == 0:  # Left pressed
        if state == "choosing":
            neg = (neg + 1) % 5
            if neg == 0: neg = 1
            pos = 0
            check_neg()
        print('Left - Negative:', neg)
        draw_menu_lcd()
        disp.LCD_ShowImage(image,0,0)
        time.sleep(0.2)
        
    elif GPIO.input(KEY_RIGHT_PIN) == 0:  # Right pressed
        if state == "choosing":
            pos = (pos + 1) % 5
            if pos == 0: pos = 1
            neg = 0
            check_pos()
        print('Right - Positive:', pos)
        draw_menu_lcd()
        disp.LCD_ShowImage(image,0,0)
        time.sleep(0.2)
        
    elif GPIO.input(KEY_PRESS_PIN) == 0:  # Center pressed
        if state == "start":
            state = "choosing"
            pos = 1
            neg = 0
        elif state == "choosing":
            draw_emoji_lcd()
        print('Center pressed')
        draw_menu_lcd()
        disp.LCD_ShowImage(image,0,0)
        time.sleep(0.2)
        
    # Check button inputs - EXACTLY like key_demo.py
    elif GPIO.input(KEY1_PIN) == 0:  # KEY1 pressed
        if state == "choosing":
            pos = (pos + 1) % 5
            if pos == 0: pos = 1
            neg = 0
            check_pos()
        elif state == "start":
            state = "choosing"
            pos = 1
            neg = 0
        elif prev_state == "done":
            if prev_neg > 0:
                pos = prev_neg
                neg = 0
                menu = prev_menu
                draw_emoji_lcd()
            elif prev_pos > 0:
                pos = prev_pos
                neg = 0
                menu = prev_menu
                draw_emoji_lcd()
        print('KEY1 - Positive:', pos)
        draw_menu_lcd()
        disp.LCD_ShowImage(image,0,0)
        time.sleep(0.2)
        
    elif GPIO.input(KEY2_PIN) == 0:  # KEY2 pressed
        reset_prev()
        if state == "start":
            menu = (menu + 1) % 4
            check_menu()
        elif state == "none":
            state = "start"
            check_menu()
        elif state == "choosing":
            draw_emoji_lcd()
        print('KEY2 - Menu:', menu)
        draw_menu_lcd()
        disp.LCD_ShowImage(image,0,0)
        time.sleep(0.2)
        
    elif GPIO.input(KEY3_PIN) == 0:  # KEY3 pressed
        if state == "choosing":
            neg = (neg + 1) % 5
            if neg == 0: neg = 1
            pos = 0
            check_neg()
        elif state == "start":
            state = "choosing"
            neg = 1
            pos = 0
        elif prev_state == "done":
            if prev_pos > 0:
                neg = prev_pos
                pos = 0
                menu = prev_menu
                draw_emoji_lcd()
            elif prev_neg > 0:
                neg = prev_neg
                pos = 0
                menu = prev_menu
                draw_emoji_lcd()
        print('KEY3 - Negative:', neg)
        draw_menu_lcd()
        disp.LCD_ShowImage(image,0,0)
        time.sleep(0.2)
    
    # Update display - EXACTLY like key_demo.py
    disp.LCD_ShowImage(image,0,0)
    time.sleep(0.1)
