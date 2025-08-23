# -*- coding:utf-8 -*-
# emoji-menu.py - Emoji OS Zero with LCD display
# Combines working simple display approach with working emoji_key_basic.py menu logic

import time
from PIL import Image, ImageDraw
import LCD_1in44
import RPi.GPIO as GPIO

# GPIO pin definitions for Waveshare LCD HAT
KEY_UP_PIN     = 6 
KEY_DOWN_PIN   = 19
KEY_LEFT_PIN   = 5
KEY_RIGHT_PIN  = 26
KEY_PRESS_PIN  = 13
KEY1_PIN       = 21
KEY2_PIN       = 20
KEY3_PIN       = 16

# Initialize GPIO
GPIO.setmode(GPIO.BCM) 
GPIO.setup(KEY_UP_PIN,      GPIO.IN, pull_up_down=GPIO.PUD_UP)    # Input with pull-up
GPIO.setup(KEY_DOWN_PIN,    GPIO.IN, pull_up_down=GPIO.PUD_UP)  # Input with pull-up
GPIO.setup(KEY_LEFT_PIN,    GPIO.IN, pull_up_down=GPIO.PUD_UP)  # Input with pull-up
GPIO.setup(KEY_RIGHT_PIN,   GPIO.IN, pull_up_down=GPIO.PUD_UP) # Input with pull-up
GPIO.setup(KEY_PRESS_PIN,   GPIO.IN, pull_up_down=GPIO.PUD_UP) # Input with pull-up
GPIO.setup(KEY1_PIN,        GPIO.IN, pull_up_down=GPIO.PUD_UP)      # Input with pull-up
GPIO.setup(KEY2_PIN,        GPIO.IN, pull_up_down=GPIO.PUD_UP)      # Input with pull-up
GPIO.setup(KEY3_PIN,        GPIO.IN, pull_up_down=GPIO.PUD_UP)      # Input with pull-up

# Initialize display - using the working simple approach
disp = LCD_1in44.LCD()
disp.LCD_Init(LCD_1in44.SCAN_DIR_DFT)
disp.LCD_Clear()

image = Image.new('RGB', (disp.width, disp.height))
draw = ImageDraw.Draw(image)

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

def draw_menu():
    """Draw the menu on the LCD display"""
    # Clear the entire display
    draw.rectangle((0, 0, disp.width, disp.height), fill=(0, 0, 0))
    
    # Draw menu title
    draw.text((10, 10), "EMOJI OS ZERO", fill=(255, 255, 255))
    
    # Draw menu items
    menu_names = ["Emojis", "Animations", "Characters", "Symbols"]
    for i in range(4):
        y = 40 + i * 30
        if i == menu:
            # Highlight selected menu
            color = (0, 255, 0)  # Green for selected
            draw.rectangle((5, y-5, 120, y+25), outline=color, fill=(0, 0, 0))
        else:
            color = (255, 255, 255)  # White for unselected
        draw.text((10, y), f"{i}: {menu_names[i]}", fill=color)
    
    # Draw selection info
    if state == "choosing":
        if pos > 0:
            draw.text((10, 160), f"POSITIVE: {pos}", fill=(0, 255, 0))
        elif neg > 0:
            draw.text((10, 160), f"NEGATIVE: {neg}", fill=(255, 0, 0))
    else:
        draw.text((10, 160), "Use UP/DOWN to navigate", fill=(128, 128, 128))
    
    # Update display
    disp.LCD_ShowImage(image, 0, 0)

def draw_emoji():
    """Draw emoji on the LCD display"""
    # Clear the entire display
    draw.rectangle((0, 0, disp.width, disp.height), fill=(0, 0, 0))
    
    # Draw emoji based on selection
    if menu == 0 and pos == 1:
        # Simple smiley face
        draw.ellipse((40, 40, 88, 88), outline=(255, 255, 255), fill=(0, 0, 0))  # Face
        draw.ellipse((55, 55, 67, 67), outline=(255, 255, 255), fill=(255, 255, 255))  # Left eye
        draw.ellipse((73, 55, 85, 67), outline=(255, 255, 255), fill=(255, 255, 255))  # Right eye
        draw.arc((55, 65, 73, 83), 0, 180, fill=(255, 255, 255), width=3)  # Smile
        label = "Smiley Face"
    elif menu == 0 and pos == 2:
        # Heart
        draw.ellipse((40, 40, 88, 88), outline=(255, 0, 0), fill=(255, 0, 0))  # Red heart
        label = "Heart"
    elif menu == 1 and pos == 1:
        # Fireworks
        for i in range(8):
            angle = i * 45
            x = 64 + int(25 * (angle / 90))
            y = 64 + int(25 * (angle / 90))
            draw.line((64, 64, x, y), fill=(255, 0, 255), width=3)
        label = "Fireworks"
    elif menu == 2 and pos == 1:
        # Star
        points = [(64, 30), (70, 50), (90, 50), (75, 65), (80, 85), (64, 70), (48, 85), (53, 65), (38, 50), (58, 50)]
        draw.polygon(points, outline=(255, 255, 0), fill=(255, 255, 0))
        label = "Star"
    elif menu == 3 and pos == 1:
        # Circle
        draw.ellipse((40, 40, 88, 88), outline=(0, 128, 255), fill=(0, 128, 255))
        label = "Circle"
    else:
        label = f"Menu {menu}, Option {pos}"
    
    # Draw label
    draw.text((10, 120), label, fill=(255, 255, 255))
    draw.text((10, 160), "Press KEY2 to return", fill=(128, 128, 128))
    
    # Update display
    disp.LCD_ShowImage(image, 0, 0)

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

# Main loop - FROM emoji_key_basic.py
print("Emoji OS Zero started! Use the joystick and buttons to navigate.")
print("Joystick: Navigate menus")
print("KEY1: Select positive")
print("KEY2: Navigate/confirm")
print("KEY3: Select negative")
print("=" * 50)

# Initial menu display
draw_menu()

while True:
    # Check joystick inputs for menu navigation
    if GPIO.input(KEY_UP_PIN) == 0:  # Up pressed
        if state == "none":
            state = "start"
        elif state == "start":
            menu = (menu - 1) % 4
            check_menu()
        print('Up - Menu:', menu)
        draw_menu()
        time.sleep(0.2)  # Debounce
        
    elif GPIO.input(KEY_DOWN_PIN) == 0:  # Down pressed
        if state == "none":
            state = "start"
        elif state == "start":
            menu = (menu + 1) % 4
            check_menu()
        print('Down - Menu:', menu)
        draw_menu()
        time.sleep(0.2)  # Debounce
        
    elif GPIO.input(KEY_LEFT_PIN) == 0:  # Left pressed
        if state == "choosing":
            neg = (neg + 1) % 5
            if neg == 0:
                neg = 1
            pos = 0
            check_neg()
        print('Left - Negative:', neg)
        draw_menu()
        time.sleep(0.2)  # Debounce
        
    elif GPIO.input(KEY_RIGHT_PIN) == 0:  # Right pressed
        if state == "choosing":
            pos = (pos + 1) % 5
            if pos == 0:
                pos = 1
            neg = 0
            check_pos()
        print('Right - Positive:', pos)
        draw_menu()
        time.sleep(0.2)  # Debounce
        
    elif GPIO.input(KEY_PRESS_PIN) == 0:  # Center pressed
        if state == "start":
            state = "choosing"
            pos = 1
            neg = 0
        elif state == "choosing":
            draw_emoji()
        print('Center pressed')
        draw_menu()
        time.sleep(0.2)  # Debounce
        
    # Check button inputs
    elif GPIO.input(KEY1_PIN) == 0:  # KEY1 pressed
        if state == "choosing":
            pos = (pos + 1) % 5
            if pos == 0:
                pos = 1
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
                draw_emoji()
            elif prev_pos > 0:
                pos = prev_pos
                neg = 0
                menu = prev_menu
                draw_emoji()
        print('KEY1 - Positive:', pos)
        draw_menu()
        time.sleep(0.2)  # Debounce
        
    elif GPIO.input(KEY2_PIN) == 0:  # KEY2 pressed
        reset_prev()
        if state == "start":
            menu = (menu + 1) % 4
            check_menu()
        elif state == "none":
            state = "start"
            check_menu()
        elif state == "choosing":
            draw_emoji()
        print('KEY2 - Menu:', menu)
        draw_menu()
        time.sleep(0.2)  # Debounce
        
    elif GPIO.input(KEY3_PIN) == 0:  # KEY3 pressed
        if state == "choosing":
            neg = (neg + 1) % 5
            if neg == 0:
                neg = 1
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
                draw_emoji()
            elif prev_neg > 0:
                neg = prev_neg
                pos = 0
                menu = prev_menu
                draw_emoji()
        print('KEY3 - Negative:', neg)
        draw_menu()
        time.sleep(0.2)  # Debounce
    
    time.sleep(0.1)  # Small delay to prevent excessive CPU usage
