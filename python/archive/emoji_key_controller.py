# -*- coding:utf-8 -*-
# emoji_key_controller.py - Emoji OS Zero with LCD Display
# Based on working emoji_key_basic.py with added LCD functionality
# Works on Raspberry Pi Zero with Waveshare LCD HAT

import RPi.GPIO as GPIO
import time
from PIL import Image, ImageDraw, ImageFont

# === GPIO pin definitions for Waveshare LCD HAT ===
KEY_UP_PIN     = 6 
KEY_DOWN_PIN   = 19
KEY_LEFT_PIN   = 5
KEY_RIGHT_PIN  = 26
KEY_PRESS_PIN  = 13
KEY1_PIN       = 21
KEY2_PIN       = 20
KEY3_PIN       = 16

# === Initialize GPIO ===
GPIO.setmode(GPIO.BCM) 
GPIO.setup(KEY_UP_PIN,      GPIO.IN, pull_up_down=GPIO.PUD_UP)
GPIO.setup(KEY_DOWN_PIN,    GPIO.IN, pull_up_down=GPIO.PUD_UP)
GPIO.setup(KEY_LEFT_PIN,    GPIO.IN, pull_up_down=GPIO.PUD_UP)
GPIO.setup(KEY_RIGHT_PIN,   GPIO.IN, pull_up_down=GPIO.PUD_UP)
GPIO.setup(KEY_PRESS_PIN,   GPIO.IN, pull_up_down=GPIO.PUD_UP)
GPIO.setup(KEY1_PIN,        GPIO.IN, pull_up_down=GPIO.PUD_UP)
GPIO.setup(KEY2_PIN,        GPIO.IN, pull_up_down=GPIO.PUD_UP)
GPIO.setup(KEY3_PIN,        GPIO.IN, pull_up_down=GPIO.PUD_UP)

# === Menu state variables ===
menu = 0
pos = 0
neg = 0
state = "none"  # start, end, or none
# preserve the previous state for pos/neg flipping
prev_menu = 0
prev_pos = 0
prev_neg = 0
prev_state = "none"  # or done

# === Display dimensions (same as Waveshare 1.44inch LCD) ===
DISPLAY_WIDTH = 128
DISPLAY_HEIGHT = 128

# === Menu layout margins ===
LEFT_EMOJI_RIGHT_MARGIN = 25    # Right edge of left emoji column
RIGHT_EMOJI_LEFT_MARGIN = 105   # Left edge of right emoji column

# === Smiley matrix (8x8) ===
smiley_matrix = [
    [' ', 'Y', 'Y', 'Y', 'Y', 'Y', 'Y', ' '],
    ['Y', 'Y', 'Y', 'Y', 'Y', 'Y', 'Y', 'Y'],
    ['Y', 'B', 'Y', 'Y', 'Y', 'Y', 'B', 'Y'],
    ['Y', 'B', 'Y', 'Y', 'Y', 'Y', 'B', 'Y'],
    ['Y', 'Y', 'Y', 'Y', 'Y', 'Y', 'Y', 'Y'],
    ['Y', 'Y', 'Y', 'Y', 'Y', 'B', 'Y', 'Y'],
    ['Y', 'Y', 'B', 'B', 'B', 'Y', 'Y', 'Y'],
    [' ', 'Y', 'Y', 'Y', 'Y', 'Y', 'Y', ' '],
]

# === Color mapping ===
color_map = {
    'Y': 'yellow',
    'B': 'black',
    ' ': (0, 0, 0),  # background
}

# === Menu items ===
menu_items = ["Emojis", "Animations", "Characters", "Other"]

# === Initialize LCD display ===
try:
    import LCD_1in44
    disp = LCD_1in44.LCD()
    disp.LCD_Init(LCD_1in44.SCAN_DIR_DFT)
    disp.LCD_Clear()
    lcd_available = True
    print("LCD display initialized successfully")
except ImportError:
    lcd_available = False
    print("LCD driver not available - running in terminal mode only")

# === Function to draw a single scaled pixel ===
def draw_pixel(draw, x, y, color, scale):
    x0 = x
    y0 = y
    x1 = x + scale
    y1 = y + scale
    draw.rectangle((x0, y0, x1, y1), fill=color)

# === Function to draw emoji with optional selection border ===
def draw_emoji(draw, matrix, color_map, scale, top_left_x, top_left_y, show_selection=False):
    for row in range(len(matrix)):
        for col in range(len(matrix[row])):
            symbol = matrix[row][col]
            color = color_map.get(symbol, (0, 0, 0))
            x = top_left_x + col * scale
            y = top_left_y + row * scale
            draw_pixel(draw, x, y, color, scale)
    
    # Draw selection border if requested
    if show_selection:
        # Calculate emoji dimensions
        emoji_width = len(matrix[0]) * scale
        emoji_height = len(matrix) * scale
        
        # Draw white border around the emoji
        border_width = 1
        draw.rectangle(
            (top_left_x - border_width, top_left_y - border_width, 
             top_left_x + emoji_width + border_width + 1, top_left_y + emoji_height + border_width + 1),
            outline="white",
            width=border_width
        )

# === Function to draw text centered ===
def draw_centered_text(draw, text, y_position, font, max_width, text_color="white"):
    # Use textbbox instead of textsize for newer PIL versions
    try:
        bbox = draw.textbbox((0, 0), text, font=font)
        text_width = bbox[2] - bbox[0]
        text_height = bbox[3] - bbox[1]
    except AttributeError:
        # Fallback for older PIL versions
        text_width, text_height = draw.textsize(text, font=font)
    
    x_position = (max_width - text_width) // 2  # center the text
    draw.text((x_position, y_position), text, font=font, fill=text_color)

# === Function to draw menu row with selection styling ===
def draw_menu_row(draw, text, y_position, font, is_selected=False):
    row_height = 15
    row_y = y_position
    
    if is_selected:
        # Calculate the width available for the menu text background
        bg_width = RIGHT_EMOJI_LEFT_MARGIN - LEFT_EMOJI_RIGHT_MARGIN
        
        # Position the background starting from the left margin
        bg_x = LEFT_EMOJI_RIGHT_MARGIN
        
        # Draw white background for selected row (consistent width for all items)
        draw.rectangle((bg_x, row_y, bg_x + bg_width, row_y + row_height), fill="white")
        
        # Draw text in black for selected row
        draw_centered_text(draw, text, row_y, font, DISPLAY_WIDTH, "black")
    else:
        # Draw text in white for unselected row
        draw_centered_text(draw, text, row_y, font, DISPLAY_WIDTH, "white")

# === Function to draw emoji selection indicators ===
def draw_emoji_selection(draw, pos, neg):
    # Clear previous selections
    for y_pos in [1, 16, 31, 46]:
        # Left side emojis
        draw_emoji(draw, smiley_matrix, color_map, 1.5, 5, y_pos, show_selection=False)
        # Right side emojis  
        draw_emoji(draw, smiley_matrix, color_map, 1.5, 110, y_pos, show_selection=False)
    
    # Show current selection
    if pos > 0:
        # Positive selection (left side)
        y_pos = (pos - 1) * 15 + 1
        draw_emoji(draw, smiley_matrix, color_map, 1.5, 5, y_pos, show_selection=True)
    elif neg > 0:
        # Negative selection (right side)
        y_pos = (neg - 1) * 15 + 1
        draw_emoji(draw, smiley_matrix, color_map, 1.5, 110, y_pos, show_selection=True)

# === Function to redraw the entire LCD display ===
def redraw_lcd():
    if not lcd_available:
        return
    
    # Create new blank canvas
    image = Image.new('RGB', (DISPLAY_WIDTH, DISPLAY_HEIGHT), color=(0, 0, 0))
    draw = ImageDraw.Draw(image)
    
    # Load font
    try:
        font = ImageFont.load_default()
    except:
        font = ImageFont.load_default()
    
    # === main emoji ===
    scale = 7
    emoji_width = scale * 8
    emoji_height = scale * 8
    start_x = (DISPLAY_WIDTH - emoji_width) // 2
    start_y = DISPLAY_HEIGHT // 2
    draw_emoji(draw, smiley_matrix, color_map, scale, start_x, start_y)
    
    # === menu left side emojis ===
    draw_emoji(draw, smiley_matrix, color_map, 1.5, 5, 1)
    draw_emoji(draw, smiley_matrix, color_map, 1.5, 5, 16)
    draw_emoji(draw, smiley_matrix, color_map, 1.5, 5, 31)
    draw_emoji(draw, smiley_matrix, color_map, 1.5, 5, 46)
    
    # === menu right side emojis ===
    draw_emoji(draw, smiley_matrix, color_map, 1.5, 110, 1)
    draw_emoji(draw, smiley_matrix, color_map, 1.5, 110, 16)
    draw_emoji(draw, smiley_matrix, color_map, 1.5, 110, 31)
    draw_emoji(draw, smiley_matrix, color_map, 1.5, 110, 46)
    
    # === Menu Texts ===
    text_y_positions = [1, 16, 31, 46]
    
    # Draw text for left side menu with selection styling
    for i, item in enumerate(menu_items):
        is_selected = (i == menu)
        draw_menu_row(draw, item, text_y_positions[i], font, is_selected)
    
    # Draw text for right side menu (same selection state)
    for i, item in enumerate(menu_items):
        is_selected = (i == menu)
        draw_menu_row(draw, item, text_y_positions[i], font, is_selected)
    
    # Draw emoji selection indicators
    draw_emoji_selection(draw, pos, neg)
    
    # Update LCD display
    disp.LCD_ShowImage(image, 0, 0)

# === Menu control functions ===
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
    print("\033[2J\033[H")  # Clear screen and move cursor to top

def draw_menu():
    """Draw the menu indicator on the terminal"""
    global menu
    
    clear_screen()
    print("=" * 50)
    print("           EMOJI OS ZERO")
    print("=" * 50)
    print()
    
    menu_names = ["Emojis", "Animations", "Characters", "Other"]
    
    for i in range(4):
        if i == menu:
            print(f"  > {i}: {menu_names[i]} <")
        else:
            print(f"    {i}: {menu_name[i]}")
    
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
    print("           SELECTED EMOJI")
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
        print("�� Scroll Large Image")
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
        print("��‍🦲 Bald")
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
            time.sleep(0.2)  # Debounce
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
print("Emoji OS Zero with LCD started. Use the joystick and buttons to navigate.")
print("Joystick: Navigate menus")
print("KEY1: Select positive")
print("KEY2: Navigate/confirm")
print("KEY3: Select negative")
print("=" * 50)

# Initial LCD display
if lcd_available:
    redraw_lcd()

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
            draw_menu()
            if lcd_available:
                redraw_lcd()
        draw_selection()
        print('Up - Menu:', menu)
        time.sleep(0.2)  # Debounce
        
    elif GPIO.input(KEY_DOWN_PIN) == 0:  # Down pressed
        if state == "none":
            state = "start"
        elif state == "start":
            menu = (menu + 1) % 4
            check_menu()
            draw_menu()
            if lcd_available:
                redraw_lcd()
        draw_selection()
        print('Down - Menu:', menu)
        time.sleep(0.2)  # Debounce
        
    elif GPIO.input(KEY_LEFT_PIN) == 0:  # Left pressed
        if state == "choosing":
            neg = (neg + 1) % 5
            if neg == 0:
                neg = 1
            pos = 0
            check_neg()
            draw_menu()
            if lcd_available:
                redraw_lcd()
            draw_selection()
        print('Left - Negative:', neg)
        time.sleep(0.2)  # Debounce
        
    elif GPIO.input(KEY_RIGHT_PIN) == 0:  # Right pressed
        if state == "choosing":
            pos = (pos + 1) % 5
            if pos == 0:
                pos = 1
            check_pos()
            draw_menu()
            if lcd_available:
                redraw_lcd()
            draw_selection()
        print('Right - Positive:', pos)
        time.sleep(0.2)  # Debounce
        
    elif GPIO.input(KEY_PRESS_PIN) == 0:  # Center pressed
        if state == "start":
            state = "choosing"
            pos = 1
            neg = 0
            draw_menu()
            if lcd_available:
                redraw_lcd()
            draw_selection()
        elif state == "choosing":
            draw_emoji()
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
            draw_menu()
            if lcd_available:
                redraw_lcd()
            draw_selection()
        elif state == "start":
            state = "choosing"
            pos = 1
            neg = 0
            draw_menu()
            if lcd_available:
                redraw_lcd()
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
        time.sleep(0.2)  # Debounce
        
    elif GPIO.input(KEY2_PIN) == 0:  # KEY2 pressed
        reset_prev()
        if state == "start":
            menu = (menu + 1) % 4
            check_menu()
            draw_menu()
            if lcd_available:
                redraw_lcd()
        elif state == "none":
            state = "start"
            check_menu()
            draw_menu()
        elif state == "choosing":
            draw_emoji()
        print('KEY2 - Menu:', menu)
        time.sleep(0.2)  # Debounce
        
    elif GPIO.input(KEY3_PIN) == 0:  # KEY3 pressed
        if state == "choosing":
            neg = (neg + 1) % 5
            if neg == 0:
                neg = 1
            pos = 0
            check_neg()
            draw_menu()
            if lcd_available:
                redraw_lcd()
            draw_selection()
        elif state == "start":
            state = "choosing"
            neg = 1
            pos = 0
            draw_menu()
            if lcd_available:
                redraw_lcd()
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
        time.sleep(0.2)  # Debounce
    
    time.sleep(0.1)  # Small delay to prevent excessive CPU usage