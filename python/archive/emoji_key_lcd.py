# -*- coding:utf-8 -*-
# emoji_key_lcd.py - Emoji OS Zero with LCD display
# Adapted for Raspberry Pi Zero 2 W - uses LCD but avoids GPIO conflicts
# Shows menu on left side, scaled emojis on right side

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

# Initialize GPIO FIRST - before any LCD operations
GPIO.setmode(GPIO.BCM) 
GPIO.setup(KEY_UP_PIN,      GPIO.IN, pull_up_down=GPIO.PUD_UP)    # Input with pull-up
GPIO.setup(KEY_DOWN_PIN,    GPIO.IN, pull_up_down=GPIO.PUD_UP)  # Input with pull-up
GPIO.setup(KEY_LEFT_PIN,    GPIO.IN, pull_up_down=GPIO.PUD_UP)  # Input with pull-up
GPIO.setup(KEY_RIGHT_PIN,   GPIO.IN, pull_up_down=GPIO.PUD_UP) # Input with pull-up
GPIO.setup(KEY_PRESS_PIN,   GPIO.IN, pull_up_down=GPIO.PUD_UP) # Input with pull-up
GPIO.setup(KEY1_PIN,        GPIO.IN, pull_up_down=GPIO.PUD_UP)      # Input with pull-up
GPIO.setup(KEY2_PIN,        GPIO.IN, pull_up_down=GPIO.PUD_UP)      # Input with pull-up
GPIO.setup(KEY3_PIN,        GPIO.IN, pull_up_down=GPIO.PUD_UP)      # Input with pull-up

# Try to import LCD library after GPIO setup
try:
    import LCD_1in44
    import LCD_Config
    
    # Initialize LCD display
    disp = LCD_1in44.LCD()
    Lcd_ScanDir = LCD_1in44.SCAN_DIR_DFT  # SCAN_DIR_DFT = D2U_L2R
    disp.LCD_Init(Lcd_ScanDir)
    disp.LCD_Clear()
    LCD_AVAILABLE = True
    print("LCD display initialized successfully")
except Exception as e:
    print(f"LCD display not available: {e}")
    print("Running in terminal-only mode")
    LCD_AVAILABLE = False

# Create blank image for drawing
width = 128
height = 128
image = Image.new('RGB', (width, height))
draw = ImageDraw.Draw(image)

# Menu state variables
menu = 0
pos = 0
neg = 0
state = "none"  # start, end, or none
# preserve the previous state for pos/neg flipping
prev_menu = 0
prev_pos = 0
prev_neg = 0
prev_state = "none"  # or done
pause = 0.2

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

def clear_display():
    """Clear the display and draw a black background"""
    draw.rectangle((0, 0, width, height), outline=0, fill=0)

def draw_8x8_scaled(pattern, x_offset=64, y_offset=32, scale=4):
    """Draw an 8x8 pattern scaled up to fill half the display"""
    # Each 8x8 pixel becomes scale x scale pixels
    for y in range(8):
        for x in range(8):
            if pattern[y][x]:  # If pixel is set
                # Calculate scaled coordinates
                start_x = x_offset + (x * scale)
                start_y = y_offset + (y * scale)
                end_x = start_x + scale
                end_y = start_y + scale
                # Draw the scaled pixel
                draw.rectangle((start_x, start_y, end_x, end_y), outline=255, fill=255)

def draw_menu_lcd():
    """Draw the menu indicator on the left side of LCD"""
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
    
    if LCD_AVAILABLE:
        disp.LCD_ShowImage(image, 0, 0)

def draw_emoji_lcd():
    """Draw the chosen emoji on the right side of LCD"""
    global state, menu, pos, neg
    
    # Clear right side (64-127 pixels wide)
    draw.rectangle((64, 0, 127, 127), outline=0, fill=0)
    
    #==========
    # POSITIVE 0 - Emojis
    if (menu == 0 and pos == 1):
        # Regular smiley face (8x8 pattern)
        pattern = [
            [0,0,1,1,1,1,0,0],
            [0,1,0,0,0,0,1,0],
            [1,0,1,0,0,1,0,1],
            [1,0,0,0,0,0,0,1],
            [1,0,1,0,0,1,0,1],
            [1,0,0,1,1,0,0,1],
            [0,1,0,0,0,0,1,0],
            [0,0,1,1,1,1,0,0]
        ]
        draw_8x8_scaled(pattern, 64, 32, 6)
        
    elif (menu == 0 and pos == 2):
        # Happy face
        pattern = [
            [0,0,1,1,1,1,0,0],
            [0,1,0,0,0,0,1,0],
            [1,0,1,0,0,1,0,1],
            [1,0,0,0,0,0,0,1],
            [1,0,0,1,1,0,0,1],
            [1,0,1,0,0,1,0,1],
            [0,1,0,0,0,0,1,0],
            [0,0,1,1,1,1,0,0]
        ]
        draw_8x8_scaled(pattern, 64, 32, 6)
        
    elif (menu == 0 and pos == 3):
        # Wry face
        pattern = [
            [0,0,1,1,1,1,0,0],
            [0,1,0,0,0,0,1,0],
            [1,0,1,0,0,1,0,1],
            [1,0,0,0,0,0,0,1],
            [1,0,1,0,0,1,0,1],
            [1,0,0,1,1,0,0,1],
            [0,1,0,0,0,0,1,0],
            [0,0,1,1,1,1,0,0]
        ]
        draw_8x8_scaled(pattern, 64, 32, 6)
        
    elif (menu == 0 and pos == 4):
        # Heart
        pattern = [
            [0,1,1,0,0,1,1,0],
            [1,1,1,1,1,1,1,1],
            [1,1,1,1,1,1,1,1],
            [1,1,1,1,1,1,1,1],
            [0,1,1,1,1,1,1,0],
            [0,0,1,1,1,1,0,0],
            [0,0,0,1,1,0,0,0],
            [0,0,0,0,0,0,0,0]
        ]
        draw_8x8_scaled(pattern, 64, 32, 6)
        
    # NEGATIVE 0 - Emojis
    elif (menu == 0 and neg == 1):
        # Thick lips
        pattern = [
            [0,0,1,1,1,1,0,0],
            [0,1,0,0,0,0,1,0],
            [1,0,1,0,0,1,0,1],
            [1,0,0,0,0,0,0,1],
            [1,0,1,1,1,1,0,1],
            [1,0,1,1,1,1,0,1],
            [0,1,0,0,0,0,1,0],
            [0,0,1,1,1,1,0,0]
        ]
        draw_8x8_scaled(pattern, 64, 32, 6)
        
    elif (menu == 0 and neg == 2):
        # Sad face
        pattern = [
            [0,0,1,1,1,1,0,0],
            [0,1,0,0,0,0,1,0],
            [1,0,1,0,0,1,0,1],
            [1,0,0,0,0,0,0,1],
            [1,0,0,1,1,0,0,1],
            [1,0,1,0,0,1,0,1],
            [0,1,0,0,0,0,1,0],
            [0,0,1,1,1,1,0,0]
        ]
        draw_8x8_scaled(pattern, 64, 32, 6)
        
    elif (menu == 0 and neg == 3):
        # Angry face
        pattern = [
            [0,0,1,1,1,1,0,0],
            [0,1,0,0,0,0,1,0],
            [1,0,1,0,0,1,0,1],
            [1,0,0,0,0,0,0,1],
            [1,0,1,0,0,1,0,1],
            [1,0,0,1,1,0,0,1],
            [0,1,0,0,0,0,1,0],
            [0,0,1,1,1,1,0,0]
        ]
        draw_8x8_scaled(pattern, 64, 32, 6)
        
    elif (menu == 0 and neg == 4):
        # Monster
        pattern = [
            [0,0,1,1,1,1,0,0],
            [0,1,1,1,1,1,1,0],
            [1,1,0,1,1,0,1,1],
            [1,1,1,1,1,1,1,1],
            [1,1,0,1,1,0,1,1],
            [1,1,1,1,1,1,1,1],
            [0,1,1,1,1,1,1,0],
            [0,0,1,1,1,1,0,0]
        ]
        draw_8x8_scaled(pattern, 64, 32, 6)
        
    #==========
    # POSITIVE 1 - Animations
    elif (menu == 1 and pos == 1):
        # Fireworks
        for i in range(8):
            angle = i * 45
            x = 96 + int(20 * (angle / 90))
            y = 64 + int(20 * (angle / 90))
            draw.line((96, 64, x, y), fill=0xff00ff, width=2)
        
    elif (menu == 1 and pos == 2):
        # Rainbow circles
        colors = [0xff0000, 0xff8000, 0xffff00, 0x00ff00, 0x0080ff, 0x8000ff]
        for i, color in enumerate(colors):
            radius = 15 + i * 6
            draw.ellipse((96-radius, 64-radius, 96+radius, 64+radius), outline=color, fill=0)
        
    elif (menu == 1 and pos == 3):
        # Scroll
        draw.text((70, 50), "Scroll", fill=255)
        
    elif (menu == 1 and pos == 4):
        # Chakana
        draw.rectangle((80, 40, 112, 88), outline=255, fill=0)
        draw.line((80, 64), (112, 64), fill=255, width=2)
        draw.line((96, 40), (96, 88), fill=255, width=2)
        
    # NEGATIVE 1 - Animations
    elif (menu == 1 and neg == 1):
        # Rain
        for i in range(8):
            x = 70 + i * 7
            y = 30 + (i % 3) * 15
            draw.line((x, y, x+2, y+6), fill=0x0080ff, width=2)
        
    #==========
    # POSITIVE 2 - Characters
    elif (menu == 2 and pos == 1):
        # Finn
        pattern = [
            [0,0,1,1,1,1,0,0],
            [0,1,1,1,1,1,1,0],
            [1,1,0,1,1,0,1,1],
            [1,1,1,1,1,1,1,1],
            [1,1,0,1,1,0,1,1],
            [1,1,1,1,1,1,1,1],
            [0,1,1,1,1,1,1,0],
            [0,0,1,1,1,1,0,0]
        ]
        draw_8x8_scaled(pattern, 64, 32, 6)
        
    elif (menu == 2 and pos == 2):
        # Pikachu
        pattern = [
            [0,0,1,1,1,1,0,0],
            [0,1,1,1,1,1,1,0],
            [1,1,0,1,1,0,1,1],
            [1,1,1,1,1,1,1,1],
            [1,1,0,1,1,0,1,1],
            [1,1,1,1,1,1,1,1],
            [0,1,1,1,1,1,1,0],
            [0,0,1,1,1,1,0,0]
        ]
        draw_8x8_scaled(pattern, 64, 32, 6)
        
    elif (menu == 2 and pos == 3):
        # Crab
        pattern = [
            [0,0,0,1,1,0,0,0],
            [0,0,1,1,1,1,0,0],
            [0,1,1,1,1,1,1,0],
            [1,1,1,1,1,1,1,1],
            [1,1,1,1,1,1,1,1],
            [0,1,1,1,1,1,1,0],
            [0,0,1,1,1,1,0,0],
            [0,0,0,1,1,0,0,0]
        ]
        draw_8x8_scaled(pattern, 64, 32, 6)
        
    elif (menu == 2 and pos == 4):
        # Frog
        pattern = [
            [0,0,1,1,1,1,0,0],
            [0,1,1,1,1,1,1,0],
            [1,1,0,1,1,0,1,1],
            [1,1,1,1,1,1,1,1],
            [1,1,0,1,1,0,1,1],
            [1,1,1,1,1,1,1,1],
            [0,1,1,1,1,1,1,0],
            [0,0,1,1,1,1,0,0]
        ]
        draw_8x8_scaled(pattern, 64, 32, 6)
        
    # NEGATIVE 2 - Characters
    elif (menu == 2 and neg == 1):
        # Bald
        pattern = [
            [0,0,1,1,1,1,0,0],
            [0,1,0,0,0,0,1,0],
            [1,0,1,0,0,1,0,1],
            [1,0,0,0,0,0,0,1],
            [1,0,1,0,0,1,0,1],
            [1,0,0,1,1,0,0,1],
            [0,1,0,0,0,0,1,0],
            [0,0,1,1,1,1,0,0]
        ]
        draw_8x8_scaled(pattern, 64, 32, 6)
        
    elif (menu == 2 and neg == 2):
        # Surprise
        pattern = [
            [0,0,1,1,1,1,0,0],
            [0,1,0,0,0,0,1,0],
            [1,0,1,0,0,1,0,1],
            [1,0,0,0,0,0,0,1],
            [1,0,0,1,1,0,0,1],
            [1,0,1,0,0,1,0,1],
            [0,1,0,0,0,0,1,0],
            [0,0,1,1,1,1,0,0]
        ]
        draw_8x8_scaled(pattern, 64, 32, 6)
        
    #==========
    # POSITIVE 3 - Symbols
    elif (menu == 3 and pos == 1):
        # Circle
        draw.ellipse((80, 40, 112, 88), outline=255, fill=0x0080ff)
        
    elif (menu == 3 and pos == 2):
        # YES
        draw.text((80, 50), "YES", fill=255)
        
    elif (menu == 3 and pos == 3):
        # Somi
        draw.text((80, 50), "Somi", fill=255)
        
    # NEGATIVE 3 - Symbols
    elif (menu == 3 and neg == 1):
        # X
        draw.line((80, 40, 112, 88), fill=255, width=3)
        draw.line((112, 40, 80, 88), fill=255, width=3)
        
    elif (menu == 3 and neg == 2):
        # NO
        draw.text((80, 50), "NO", fill=255)
        
    else:
        # Reset state if no valid combination
        reset_state()
        return
    
    if LCD_AVAILABLE:
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

# Main loop
print("Emoji OS Zero started. Use the joystick and buttons to navigate.")
print("Joystick: Navigate menus")
print("KEY1: Select positive")
print("KEY2: Navigate/confirm")
print("KEY3: Select negative")
print("=" * 50)

# Initial display
clear_display()
draw_menu_lcd()

while True:
    # Check joystick inputs for menu navigation
    if GPIO.input(KEY_UP_PIN) == 0:  # Up pressed
        if state == "none":
            state = "start"
        elif state == "start":
            menu = (menu - 1) % 4
            check_menu()
            draw_menu_lcd()
        print('Up - Menu:', menu)
        time.sleep(0.2)  # Debounce
        
    elif GPIO.input(KEY_DOWN_PIN) == 0:  # Down pressed
        if state == "none":
            state = "start"
        elif state == "start":
            menu = (menu + 1) % 4
            check_menu()
            draw_menu_lcd()
        print('Down - Menu:', menu)
        time.sleep(0.2)  # Debounce
        
    elif GPIO.input(KEY_LEFT_PIN) == 0:  # Left pressed
        if state == "choosing":
            neg = (neg + 1) % 5
            if neg == 0:
                neg = 1
            pos = 0
            check_neg()
            draw_menu_lcd()
        print('Left - Negative:', neg)
        time.sleep(0.2)  # Debounce
        
    elif GPIO.input(KEY_RIGHT_PIN) == 0:  # Right pressed
        if state == "choosing":
            pos = (pos + 1) % 5
            if pos == 0:
                pos = 1
            neg = 0
            check_pos()
            draw_menu_lcd()
        print('Right - Positive:', pos)
        time.sleep(0.2)  # Debounce
        
    elif GPIO.input(KEY_PRESS_PIN) == 0:  # Center pressed
        if state == "start":
            state = "choosing"
            pos = 1
            neg = 0
            draw_menu_lcd()
        elif state == "choosing":
            draw_emoji_lcd()
        print('Center pressed')
        time.sleep(0.2)  # Debounce
        
    # Check button inputs
    elif GPIO.input(KEY1_PIN) == 0:  # KEY1 pressed
        if state == "choosing":
            pos = (pos + 1) % 5
            if pos == 0:
                pos = 1
            neg = 0
            check_pos()
            draw_menu_lcd()
        elif state == "start":
            state = "choosing"
            pos = 1
            neg = 0
            draw_menu_lcd()
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
        time.sleep(0.2)  # Debounce
        
    elif GPIO.input(KEY2_PIN) == 0:  # KEY2 pressed
        reset_prev()
        if state == "start":
            menu = (menu + 1) % 4
            check_menu()
            draw_menu_lcd()
        elif state == "none":
            state = "start"
            check_menu()
            draw_menu_lcd()
        elif state == "choosing":
            draw_emoji_lcd()
        print('KEY2 - Menu:', menu)
        time.sleep(0.2)  # Debounce
        
    elif GPIO.input(KEY3_PIN) == 0:  # KEY3 pressed
        if state == "choosing":
            neg = (neg + 1) % 5
            if neg == 0:
                neg = 1
            pos = 0
            check_neg()
            draw_menu_lcd()
        elif state == "start":
            state = "choosing"
            neg = 1
            pos = 0
            draw_menu_lcd()
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
        time.sleep(0.2)  # Debounce
    
    time.sleep(0.1)  # Small delay to prevent excessive CPU usage
