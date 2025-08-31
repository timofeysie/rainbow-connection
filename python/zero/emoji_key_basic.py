``
# -*- coding:utf-8 -*-
# emoji_key_basic.py - Emoji OS Zero using terminal output
# Adapted for Raspberry Pi Zero 2 W - avoids all GPIO conflicts
# This version uses terminal output instead of LCD display

import RPi.GPIO as GPIO
import time

# GPIO pin definitions for Waveshare LCD HAT
KEY_UP_PIN     = 6 
KEY_DOWN_PIN   = 19
KEY_LEFT_PIN   = 5
KEY_RIGHT_PIN  = 26
KEY_PRESS_PIN  = 13
KEY1_PIN       = 21
KEY2_PIN       = 20
KEY3_PIN       = 16

# Initialize GPIO
GPIO.setmode(GPIO.BCM) 
GPIO.setup(KEY_UP_PIN,      GPIO.IN, pull_up_down=GPIO.PUD_UP)    # Input with pull-up
GPIO.setup(KEY_DOWN_PIN,    GPIO.IN, pull_up_down=GPIO.PUD_UP)  # Input with pull-up
GPIO.setup(KEY_LEFT_PIN,    GPIO.IN, pull_up_down=GPIO.PUD_UP)  # Input with pull-up
GPIO.setup(KEY_RIGHT_PIN,   GPIO.IN, pull_up_down=GPIO.PUD_UP) # Input with pull-up
GPIO.setup(KEY_PRESS_PIN,   GPIO.IN, pull_up_down=GPIO.PUD_UP) # Input with pull-up
GPIO.setup(KEY1_PIN,        GPIO.IN, pull_up_down=GPIO.PUD_UP)      # Input with pull-up
GPIO.setup(KEY2_PIN,        GPIO.IN, pull_up_down=GPIO.PUD_UP)      # Input with pull-up
GPIO.setup(KEY3_PIN,        GPIO.IN, pull_up_down=GPIO.PUD_UP)      # Input with pull-up

# Menu state variables
menu = 0
pos = 0
neg = 0
state = "none"  # start, end, or none
# preserve the previous state for pos/neg flipping
prev_menu = 0
prev_pos = 0
prev_neg = 0
prev_state = "none"  # or done

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

def clear_screen():
    """Clear the terminal screen"""
    print("\033[2J\033[H")  # Clear screen and move cursor to top

def draw_menu():
    """Draw the menu indicator on the terminal"""
    global menu
    
    clear_screen()
    print("=" * 50)
    print("           EMOJI OS ZERO")
    print("=" * 50)
    print()
    
    menu_names = ["Emojis", "Animations", "Characters", "Symbols"]
    
    for i in range(4):
        if i == menu:
            print(f"  > {i}: {menu_names[i]} <")
        else:
            print(f"    {i}: {menu_names[i]}")
    
    print()
    print("Joystick: Navigate menus")
    print("Center: Select category")
    print("KEY1: Positive, KEY3: Negative")
    print("=" * 50)

def draw_selection():
    """Draw the current selection state"""
    global menu, pos, neg, state
    
    if state == "choosing":
        if pos > 0:
            print(f"\nSELECTING POSITIVE OPTION {pos}")
            print("Use LEFT/RIGHT to change, CENTER to confirm")
        elif neg > 0:
            print(f"\nSELECTING NEGATIVE OPTION {neg}")
            print("Use LEFT/RIGHT to change, CENTER to confirm")
    else:
        print("\nUse UP/DOWN to navigate, CENTER to select category")

def draw_emoji():
    """Display the chosen emoji and reset values"""
    global state, menu, pos, neg
    
    clear_screen()
    print("=" * 50)
    print("           SELECTED EMOJI")
    print("=" * 50)
    print()
    
    #==========
    # POSITIVE 0 - Emojis
    if (menu == 0 and pos == 1):
        print("😊 Regular Smiley Face")
    elif (menu == 0 and pos == 2):
        print("😄 Happy Face")
    elif (menu == 0 and pos == 3):
        print("😏 Wry Face")
    elif (menu == 0 and pos == 4):
        print("💖 Heart Bounce")
        
    # NEGATIVE 0 - Emojis
    elif (menu == 0 and neg == 1):
        print("💋 Thick Lips")
    elif (menu == 0 and neg == 2):
        print("😢 Sad Face")
    elif (menu == 0 and neg == 3):
        print("😠 Angry Face")
    elif (menu == 0 and neg == 4):
        print("👹 Green Monster")
        
    #==========
    # POSITIVE 1 - Animations
    elif (menu == 1 and pos == 1):
        print("🎆 Fireworks")
    elif (menu == 1 and pos == 2):
        print("🌈 Circular Rainbow")
    elif (menu == 1 and pos == 3):
        print("📜 Scroll Large Image")
    elif (menu == 1 and pos == 4):
        print("⚜️ Chakana")
        
    # NEGATIVE 1 - Animations
    elif (menu == 1 and neg == 1):
        print("🌧️ Rain")
        
    #==========
    # POSITIVE 2 - Characters
    elif (menu == 2 and pos == 1):
        print("👦 Finn")
    elif (menu == 2 and pos == 2):
        print("⚡ Pikachu")
    elif (menu == 2 and pos == 3):
        print("🦀 Crab")
    elif (menu == 2 and pos == 4):
        print("🐸 Frog")
        
    # NEGATIVE 2 - Characters
    elif (menu == 2 and neg == 1):
        print("👨‍🦲 Bald")
    elif (menu == 2 and neg == 2):
        print("😲 Surprise")
        
    #==========
    # POSITIVE 3 - Symbols
    elif (menu == 3 and pos == 1):
        print("⭕ Circle")
    elif (menu == 3 and pos == 2):
        print("✅ YES")
    elif (menu == 3 and pos == 3):
        print("🔤 Somi")
        
    # NEGATIVE 3 - Symbols
    elif (menu == 3 and neg == 1):
        print("❌ X")
    elif (menu == 3 and neg == 2):
        print("❌ NO")
        
    else:
        print("No valid selection")
        reset_state()
        return
    
    print()
    print("Press any button to return to menu")
    print("=" * 50)
    
    # Wait for any button press
    while True:
        if (GPIO.input(KEY_UP_PIN) == 0 or 
            GPIO.input(KEY_DOWN_PIN) == 0 or
            GPIO.input(KEY_LEFT_PIN) == 0 or
            GPIO.input(KEY_RIGHT_PIN) == 0 or
            GPIO.input(KEY_PRESS_PIN) == 0 or
            GPIO.input(KEY1_PIN) == 0 or
            GPIO.input(KEY2_PIN) == 0 or
            GPIO.input(KEY3_PIN) == 0):
            time.sleep(0.2)  # Debounce
            break
        time.sleep(0.1)
    
    reset_state()

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

# Initial menu display
draw_menu()

while True:
    # Check joystick inputs for menu navigation
    if GPIO.input(KEY_UP_PIN) == 0:  # Up pressed
        if state == "none":
            state = "start"
        elif state == "start":
            menu = (menu - 1) % 4
            check_menu()
            draw_menu()
        draw_selection()
        print('Up - Menu:', menu)
        time.sleep(0.2)  # Debounce
        
    elif GPIO.input(KEY_DOWN_PIN) == 0:  # Down pressed
        if state == "none":
            state = "start"
        elif state == "start":
            menu = (menu + 1) % 4
            check_menu()
            draw_menu()
        draw_selection()
        print('Down - Menu:', menu)
        time.sleep(0.2)  # Debounce
        
    elif GPIO.input(KEY_LEFT_PIN) == 0:  # Left pressed
        if state == "choosing":
            neg = (neg + 1) % 5
            if neg == 0:
                neg = 1
            pos = 0
            check_neg()
            draw_menu()
            draw_selection()
        print('Left - Negative:', neg)
        time.sleep(0.2)  # Debounce
        
    elif GPIO.input(KEY_RIGHT_PIN) == 0:  # Right pressed
        if state == "choosing":
            pos = (pos + 1) % 5
            if pos == 0:
                pos = 1
            neg = 0
            check_pos()
            draw_menu()
            draw_selection()
        print('Right - Positive:', pos)
        time.sleep(0.2)  # Debounce
        
    elif GPIO.input(KEY_PRESS_PIN) == 0:  # Center pressed
        if state == "start":
            state = "choosing"
            pos = 1
            neg = 0
            draw_menu()
            draw_selection()
        elif state == "choosing":
            draw_emoji()
        print('Center pressed')
        time.sleep(0.2)  # Debounce
        
    # Check button inputs
    elif GPIO.input(KEY1_PIN) == 0:  # KEY1 pressed
        if state == "choosing":
            pos = (pos + 1) % 5
            if pos == 0:
                pos = 1
            neg = 0
            check_pos()
            draw_menu()
            draw_selection()
        elif state == "start":
            state = "choosing"
            pos = 1
            neg = 0
            draw_menu()
            draw_selection()
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
        time.sleep(0.2)  # Debounce
        
    elif GPIO.input(KEY2_PIN) == 0:  # KEY2 pressed
        reset_prev()
        if state == "start":
            menu = (menu + 1) % 4
            check_menu()
            draw_menu()
        elif state == "none":
            state = "start"
            check_menu()
            draw_menu()
        elif state == "choosing":
            draw_emoji()
        print('KEY2 - Menu:', menu)
        time.sleep(0.2)  # Debounce
        
    elif GPIO.input(KEY3_PIN) == 0:  # KEY3 pressed
        if state == "choosing":
            neg = (neg + 1) % 5
            if neg == 0:
                neg = 1
            pos = 0
            check_neg()
            draw_menu()
            draw_selection()
        elif state == "start":
            state = "choosing"
            neg = 1
            pos = 0
            draw_menu()
            draw_selection()
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
        time.sleep(0.2)  # Debounce
    
    time.sleep(0.1)  # Small delay to prevent excessive CPU usage
