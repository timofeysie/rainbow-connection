# -*- coding:utf-8 -*-
# emoji_key_simple.py - Emoji OS Zero using working key_demo.py structure
# Adapted for Raspberry Pi Zero 2 W with Waveshare 1.44inch LCD HAT
# This version avoids GPIO library conflicts by using only RPi.GPIO

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

# Initialize LCD display
disp = LCD_1in44.LCD()
Lcd_ScanDir = LCD_1in44.SCAN_DIR_DFT  # SCAN_DIR_DFT = D2U_L2R
disp.LCD_Init(Lcd_ScanDir)
disp.LCD_Clear()

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

def draw_menu():
    """Draw the menu indicator on the display"""
    global menu
    global pause
    
    clear_display()
    
    if menu == 0:
        # Draw indicator for menu 0 (top)
        draw.rectangle((60, 20, 68, 28), outline=255, fill=255)
        disp.LCD_ShowImage(image, 0, 0)
        time.sleep(pause)
    elif menu == 1:
        # Draw indicator for menu 1 (second from top)
        draw.rectangle((60, 40, 68, 48), outline=255, fill=255)
        disp.LCD_ShowImage(image, 0, 0)
        time.sleep(pause)
    elif menu == 2:
        # Draw indicator for menu 2 (second from bottom)
        draw.rectangle((60, 60, 68, 68), outline=255, fill=255)
        disp.LCD_ShowImage(image, 0, 0)
        time.sleep(pause)
    elif menu == 3:
        # Draw indicator for menu 3 (bottom)
        draw.rectangle((60, 80, 68, 88), outline=255, fill=255)
        disp.LCD_ShowImage(image, 0, 0)
        time.sleep(pause)

def draw_pos():
    """Draw the positive state indicator"""
    global pos
    
    if pos == 1:
        draw.rectangle((20, 20, 28, 28), outline=0, fill=0x00ff00)  # Green
        disp.LCD_ShowImage(image, 0, 0)
        time.sleep(pause)
    elif pos == 2:
        draw.rectangle((20, 40, 28, 48), outline=0, fill=0x00ff00)  # Green
        disp.LCD_ShowImage(image, 0, 0)
        time.sleep(pause)
    elif pos == 3:
        draw.rectangle((20, 60, 28, 68), outline=0, fill=0x00ff00)  # Green
        disp.LCD_ShowImage(image, 0, 0)
        time.sleep(pause)
    elif pos == 4:
        draw.rectangle((20, 80, 28, 88), outline=0, fill=0x00ff00)  # Green
        disp.LCD_ShowImage(image, 0, 0)
        time.sleep(pause)

def draw_neg():
    """Draw the negative state indicator"""
    global neg
    
    if neg == 1:
        draw.rectangle((100, 20, 108, 28), outline=0, fill=0xff0000)  # Red
        disp.LCD_ShowImage(image, 0, 0)
    elif neg == 2:
        draw.rectangle((100, 40, 108, 48), outline=0, fill=0xff0000)  # Red
        disp.LCD_ShowImage(image, 0, 0)
    elif neg == 3:
        draw.rectangle((100, 60, 108, 68), outline=0, fill=0xff0000)  # Red
        disp.LCD_ShowImage(image, 0, 0)
    elif neg == 4:
        draw.rectangle((100, 80, 108, 88), outline=0, fill=0xff0000)  # Red
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

def draw_emoji():
    """Draw the chosen emoji and reset values"""
    global state, menu, pos, neg
    
    print(f"draw emoji menu at {menu}, pos at {pos}, neg at {neg}, state {state}")
    
    clear_display()
    
    #==========
    # POSITIVE 0
    # regular
    if (menu == 0 and pos == 1):
        print("menu 0 pos 1 normal")
        # Draw a simple smiley face
        draw.ellipse((40, 30, 88, 78), outline=255, fill=0)  # Face outline
        draw.ellipse((50, 45, 60, 55), outline=255, fill=255)  # Left eye
        draw.ellipse((68, 45, 78, 55), outline=255, fill=255)  # Right eye
        draw.arc((50, 50, 78, 70), 0, 180, fill=255, width=3)  # Smile
        disp.LCD_ShowImage(image, 0, 0)
        
    # happy
    elif (menu == 0 and pos == 2):
        print("menu 0 pos 2 happy")
        # Draw a happy face
        draw.ellipse((40, 30, 88, 78), outline=255, fill=0)  # Face outline
        draw.ellipse((50, 45, 60, 55), outline=255, fill=255)  # Left eye
        draw.ellipse((68, 45, 78, 55), outline=255, fill=255)  # Right eye
        draw.arc((50, 40, 78, 80), 0, 180, fill=255, width=3)  # Big smile
        disp.LCD_ShowImage(image, 0, 0)
        
    # wry
    elif (menu == 0 and pos == 3):
        print("menu 0 pos 3 wry")
        # Draw a wry face
        draw.ellipse((40, 30, 88, 78), outline=255, fill=0)  # Face outline
        draw.ellipse((50, 45, 60, 55), outline=255, fill=255)  # Left eye
        draw.ellipse((68, 45, 78, 55), outline=255, fill=255)  # Right eye
        draw.arc((50, 50, 78, 70), 0, 180, fill=255, width=3)  # Wry smile
        draw.line((50, 60, 60, 70), fill=255, width=2)  # Wry eyebrow
        disp.LCD_ShowImage(image, 0, 0)
        
    # heart bounce
    elif (menu == 0 and pos == 4):
        print("menu 0 pos 4 heart bounce")
        # Draw a heart
        draw.ellipse((50, 40, 70, 60), outline=255, fill=255)  # Left heart lobe
        draw.ellipse((70, 40, 90, 60), outline=255, fill=255)  # Right heart lobe
        draw.polygon([(50, 50), (90, 50), (70, 80)], outline=255, fill=255)  # Heart point
        disp.LCD_ShowImage(image, 0, 0)
        
    # NEGATIVE 0
    # thick lips
    elif (menu == 0 and neg == 1):
        print("menu 0 neg 1 thick lips")
        # Draw a face with thick lips
        draw.ellipse((40, 30, 88, 78), outline=255, fill=0)  # Face outline
        draw.ellipse((50, 45, 60, 55), outline=255, fill=255)  # Left eye
        draw.ellipse((68, 45, 78, 55), outline=255, fill=255)  # Right eye
        draw.rectangle((50, 60, 78, 70), outline=255, fill=255)  # Thick lips
        disp.LCD_ShowImage(image, 0, 0)
        
    # sad
    elif (menu == 0 and neg == 2):
        print("menu 0 neg 2 sad")
        # Draw a sad face
        draw.ellipse((40, 30, 88, 78), outline=255, fill=0)  # Face outline
        draw.ellipse((50, 45, 60, 55), outline=255, fill=255)  # Left eye
        draw.ellipse((68, 45, 78, 55), outline=255, fill=255)  # Right eye
        draw.arc((50, 60, 78, 80), 180, 360, fill=255, width=3)  # Sad mouth
        disp.LCD_ShowImage(image, 0, 0)
        
    # angry
    elif (menu == 0 and neg == 3):
        print("menu 0 neg 3 angry")
        # Draw an angry face
        draw.ellipse((40, 30, 88, 78), outline=255, fill=0)  # Face outline
        draw.ellipse((50, 45, 60, 55), outline=255, fill=255)  # Left eye
        draw.ellipse((68, 45, 78, 55), outline=255, fill=255)  # Right eye
        draw.line((45, 35, 55, 45), fill=255, width=2)  # Angry eyebrow
        draw.line((73, 35, 83, 45), fill=255, width=2)  # Angry eyebrow
        draw.arc((50, 60, 78, 80), 180, 360, fill=255, width=3)  # Angry mouth
        disp.LCD_ShowImage(image, 0, 0)
        
    # monster
    elif (menu == 0 and neg == 4):
        print("menu 0 neg 4 green monster")
        # Draw a monster face
        draw.ellipse((40, 30, 88, 78), outline=0x00ff00, fill=0x00ff00)  # Green face
        draw.ellipse((50, 45, 60, 55), outline=255, fill=255)  # Left eye
        draw.ellipse((68, 45, 78, 55), outline=255, fill=255)  # Right eye
        draw.rectangle((50, 60, 78, 70), outline=255, fill=255)  # Monster mouth
        disp.LCD_ShowImage(image, 0, 0)
        
    #==========
    # POSITIVE 1
    # fireworks
    elif (menu == 1 and pos == 1):
        print("menu 1 pos 1 fireworks")
        # Draw fireworks pattern
        for i in range(8):
            angle = i * 45
            x = 64 + int(30 * (angle / 90))
            y = 64 + int(30 * (angle / 90))
            draw.line((64, 64, x, y), fill=0xff00ff, width=2)
        disp.LCD_ShowImage(image, 0, 0)
        
    # circularRainbow
    elif (menu == 1 and pos == 2):
        print("menu 1 pos 2 circularRainbow")
        # Draw rainbow circles
        colors = [0xff0000, 0xff8000, 0xffff00, 0x00ff00, 0x0080ff, 0x8000ff]
        for i, color in enumerate(colors):
            radius = 20 + i * 8
            draw.ellipse((64-radius, 64-radius, 64+radius, 64+radius), outline=color, fill=0)
        disp.LCD_ShowImage(image, 0, 0)
        
    # scroll_large_image
    elif (menu == 1 and pos == 3):
        print("menu 1 pos 3 scroll_large_image")
        # Placeholder for scroll_large_image
        draw.text((40, 50), "Scroll", fill=255)
        disp.LCD_ShowImage(image, 0, 0)
        
    # chakana
    elif (menu == 1 and pos == 4):
        print("menu 1 pos 4 chacana")
        # Draw chakana symbol
        draw.rectangle((50, 40, 78, 68), outline=255, fill=0)
        draw.line((50, 54), (78, 54), fill=255, width=2)  # Horizontal line
        draw.line((64, 40), (64, 68), fill=255, width=2)  # Vertical line
        disp.LCD_ShowImage(image, 0, 0)
        
    # NEGATIVE 1
    # rain
    elif (menu == 1 and neg == 1):
        print("menu 1 neg 1 rain")
        # Draw rain drops
        for i in range(10):
            x = 20 + i * 10
            y = 20 + (i % 3) * 20
            draw.line((x, y, x+2, y+8), fill=0x0080ff, width=2)
        disp.LCD_ShowImage(image, 0, 0)
        
    #==========
    # POSITIVE 2
    # finn
    elif (menu == 2 and pos == 1):
        print("menu 2 pos 1 finn")
        # Draw Finn character
        draw.ellipse((40, 30, 88, 78), outline=255, fill=0xffcc99)  # Face
        draw.ellipse((50, 45, 60, 55), outline=255, fill=255)  # Left eye
        draw.ellipse((68, 45, 78, 55), outline=255, fill=255)  # Right eye
        draw.arc((50, 50, 78, 70), 0, 180, fill=255, width=3)  # Smile
        disp.LCD_ShowImage(image, 0, 0)
        
    # pikachu
    elif (menu == 2 and pos == 2):
        print("menu 2 pos 2 pikachu")
        # Draw Pikachu
        draw.ellipse((40, 30, 88, 78), outline=255, fill=0xffff00)  # Yellow face
        draw.ellipse((50, 45, 60, 55), outline=255, fill=0)  # Left eye
        draw.ellipse((68, 45, 78, 55), outline=255, fill=0)  # Right eye
        draw.ellipse((55, 60, 73, 68), outline=255, fill=0xff6600)  # Red cheeks
        disp.LCD_ShowImage(image, 0, 0)
        
    # crab
    elif (menu == 2 and pos == 3):
        print("menu 2 pos 3 crab")
        # Draw crab
        draw.ellipse((40, 50, 88, 70), outline=255, fill=0xff0000)  # Body
        draw.line((30, 60), (40, 60), fill=255, width=3)  # Left claw
        draw.line((88, 60), (98, 60), fill=255, width=3)  # Right claw
        disp.LCD_ShowImage(image, 0, 0)
        
    # frog
    elif (menu == 2 and pos == 4):
        print("menu 2 pos 4 frog")
        # Draw frog
        draw.ellipse((40, 30, 88, 78), outline=255, fill=0x00ff00)  # Green face
        draw.ellipse((50, 45, 60, 55), outline=255, fill=255)  # Left eye
        draw.ellipse((68, 45, 78, 55), outline=255, fill=255)  # Right eye
        draw.ellipse((55, 60, 73, 68), outline=255, fill=0x00ff00)  # Mouth
        disp.LCD_ShowImage(image, 0, 0)
        
    # NEGATIVE 2
    # bald
    elif (menu == 2 and neg == 1):
        print("menu 2 neg 1 bald")
        # Draw bald head
        draw.ellipse((40, 30, 88, 78), outline=255, fill=0xffcc99)  # Head
        draw.ellipse((50, 45, 60, 55), outline=255, fill=255)  # Left eye
        draw.ellipse((68, 45, 78, 55), outline=255, fill=255)  # Right eye
        disp.LCD_ShowImage(image, 0, 0)
        
    # surprise
    elif (menu == 2 and neg == 2):
        print("menu 2 neg 2 surprise")
        # Draw surprised face
        draw.ellipse((40, 30, 88, 78), outline=255, fill=0)  # Face outline
        draw.ellipse((50, 45, 60, 55), outline=255, fill=255)  # Left eye
        draw.ellipse((68, 45, 78, 55), outline=255, fill=255)  # Right eye
        draw.ellipse((55, 60, 73, 68), outline=255, fill=255)  # O mouth
        disp.LCD_ShowImage(image, 0, 0)
        
    #==========
    # POSITIVE 3
    # circle
    elif (menu == 3 and pos == 1):
        print("menu 3 pos 1 circle")
        draw.ellipse((40, 40, 88, 88), outline=255, fill=0x0080ff)
        disp.LCD_ShowImage(image, 0, 0)
        
    # yes
    elif (menu == 3 and pos == 2):
        print("menu 3 pos 2 yes")
        # Draw "YES" text
        draw.text((40, 50), "YES", fill=255)
        disp.LCD_ShowImage(image, 0, 0)
        
    # Somi
    elif (menu == 3 and pos == 3):
        print("menu 3 pos 3 Somi")
        # Draw "Somi" text
        draw.text((40, 50), "Somi", fill=255)
        disp.LCD_ShowImage(image, 0, 0)
        
    # NEGATIVE 3
    # X
    elif (menu == 3 and neg == 1):
        print("menu 3 neg 1 X")
        # Draw an X
        draw.line((40, 40, 88, 88), fill=255, width=3)
        draw.line((88, 40, 40, 88), fill=255, width=3)
        disp.LCD_ShowImage(image, 0, 0)
        
    # no
    elif (menu == 3 and neg == 2):
        print("menu 3 neg 2 no")
        # Draw "NO" text
        draw.text((40, 50), "NO", fill=255)
        disp.LCD_ShowImage(image, 0, 0)
        
    else:
        # Reset state if no valid combination
        reset_state()

# Main loop
print("Emoji OS Zero started. Use the joystick and buttons to navigate.")
print("Joystick: Navigate menus")
print("KEY1: Select positive")
print("KEY2: Navigate/confirm")
print("KEY3: Select negative")

while True:
    # Check joystick inputs for menu navigation
    if GPIO.input(KEY_UP_PIN) == 0:  # Up pressed
        if state == "none":
            state = "start"
        elif state == "start":
            menu = (menu - 1) % 4
            check_menu()
            clear_display()
            draw_menu()
        print('Up - Menu:', menu)
        
    elif GPIO.input(KEY_DOWN_PIN) == 0:  # Down pressed
        if state == "none":
            state = "start"
        elif state == "start":
            menu = (menu + 1) % 4
            check_menu()
            clear_display()
            draw_menu()
        print('Down - Menu:', menu)
        
    elif GPIO.input(KEY_LEFT_PIN) == 0:  # Left pressed
        if state == "choosing":
            neg = (neg + 1) % 5
            if neg == 0:
                neg = 1
            pos = 0
            check_neg()
            clear_display()
            draw_menu()
            draw_neg()
        print('Left - Negative:', neg)
        
    elif GPIO.input(KEY_RIGHT_PIN) == 0:  # Right pressed
        if state == "choosing":
            pos = (pos + 1) % 5
            if pos == 0:
                pos = 1
            neg = 0
            check_pos()
            clear_display()
            draw_menu()
            draw_pos()
        print('Right - Positive:', pos)
        
    elif GPIO.input(KEY_PRESS_PIN) == 0:  # Center pressed
        if state == "start":
            state = "choosing"
            pos = 1
            neg = 0
            clear_display()
            draw_menu()
            draw_pos()
        elif state == "choosing":
            clear_display()
            draw_emoji()
        print('Center pressed')
        
    # Check button inputs
    elif GPIO.input(KEY1_PIN) == 0:  # KEY1 pressed
        if state == "choosing":
            pos = (pos + 1) % 5
            if pos == 0:
                pos = 1
            neg = 0
            check_pos()
            clear_display()
            draw_menu()
            draw_pos()
        elif state == "start":
            state = "choosing"
            pos = 1
            neg = 0
            clear_display()
            draw_menu()
            draw_pos()
        elif prev_state == "done":
            if prev_neg > 0:
                pos = prev_neg
                neg = 0
                menu = prev_menu
                clear_display()
                draw_emoji()
            elif prev_pos > 0:
                pos = prev_pos
                neg = 0
                menu = prev_menu
                clear_display()
                draw_emoji()
        print('KEY1 - Positive:', pos)
        
    elif GPIO.input(KEY2_PIN) == 0:  # KEY2 pressed
        reset_prev()
        if state == "start":
            menu = (menu + 1) % 4
            check_menu()
            clear_display()
            draw_menu()
        elif state == "none":
            state = "start"
            check_menu()
            clear_display()
            draw_menu()
        elif state == "choosing":
            clear_display()
            draw_emoji()
        print('KEY2 - Menu:', menu)
        
    elif GPIO.input(KEY3_PIN) == 0:  # KEY3 pressed
        if state == "choosing":
            neg = (neg + 1) % 5
            if neg == 0:
                neg = 1
            pos = 0
            check_neg()
            clear_display()
            draw_menu()
            draw_neg()
        elif state == "start":
            state = "choosing"
            neg = 1
            pos = 0
            clear_display()
            draw_menu()
            draw_neg()
        elif prev_state == "done":
            if prev_pos > 0:
                neg = prev_pos
                pos = 0
                menu = prev_menu
                clear_display()
                draw_emoji()
            elif prev_neg > 0:
                neg = prev_neg
                pos = 0
                menu = prev_menu
                clear_display()
                draw_emoji()
        print('KEY3 - Negative:', neg)
    
    time.sleep(0.1)  # Small delay to prevent excessive CPU usage
