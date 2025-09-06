# -*- coding:utf-8 -*-
# smiley-matrix-controller.py - LCD Menu Controller with Joystick Input
# Combines LCD display with menu navigation system
# Works on both Raspberry Pi (with hardware) and laptop (simulation)

import sys
import os
import time

# === Auto-detect environment ===
def is_raspberry_pi():
    """Detect if running on Raspberry Pi with LCD hardware"""
    try:
        # Check if we can import the LCD driver (only available on Pi with hardware)
        import LCD_1in44
        import LCD_Config
        import RPi.GPIO as GPIO
        import spidev
        return True
    except ImportError:
        return False

# === Import appropriate modules based on environment ===
if is_raspberry_pi():
    # Running on Raspberry Pi with actual LCD hardware
    from PIL import Image, ImageDraw, ImageFont
    import LCD_1in44
    import RPi.GPIO as GPIO
    print("Running on Raspberry Pi with LCD hardware")
else:
    # Running on laptop - use simulation
    from PIL import Image, ImageDraw, ImageFont
    import tkinter as tk
    from tkinter import ttk
    print("Running on laptop - using LCD simulation")

# === Display dimensions (same as Waveshare 1.44inch LCD) ===
DISPLAY_WIDTH = 128
DISPLAY_HEIGHT = 128

# === Menu layout margins ===
LEFT_EMOJI_RIGHT_MARGIN = 25    # Right edge of left emoji column
RIGHT_EMOJI_LEFT_MARGIN = 105   # Left edge of right emoji column

# === GPIO pin definitions for Waveshare LCD HAT (Raspberry Pi only) ===
if is_raspberry_pi():
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
    GPIO.setup(KEY_UP_PIN,      GPIO.IN, pull_up_down=GPIO.PUD_UP)
    GPIO.setup(KEY_DOWN_PIN,    GPIO.IN, pull_up_down=GPIO.PUD_UP)
    GPIO.setup(KEY_LEFT_PIN,    GPIO.IN, pull_up_down=GPIO.PUD_UP)
    GPIO.setup(KEY_RIGHT_PIN,   GPIO.IN, pull_up_down=GPIO.PUD_UP)
    GPIO.setup(KEY_PRESS_PIN,   GPIO.IN, pull_up_down=GPIO.PUD_UP)
    GPIO.setup(KEY1_PIN,        GPIO.IN, pull_up_down=GPIO.PUD_UP)
    GPIO.setup(KEY2_PIN,        GPIO.IN, pull_up_down=GPIO.PUD_UP)
    GPIO.setup(KEY3_PIN,        GPIO.IN, pull_up_down=GPIO.PUD_UP)

# === Initialize display (only on Raspberry Pi) ===
if is_raspberry_pi():
    GPIO.cleanup()
    GPIO.setmode(GPIO.BCM)
    disp = LCD_1in44.LCD()
    disp.LCD_Init(LCD_1in44.SCAN_DIR_DFT)
    disp.LCD_Clear()

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

# === Function to redraw the entire display ===
def redraw_display():
    global image, draw
    
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
    
    # Update display
    if is_raspberry_pi():
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

# === Display simulation (laptop only) ===
def show_simulation():
    if not is_raspberry_pi():
        # Create a scaled version for better visibility on laptop
        scale_factor = 4
        scaled_image = image.resize((DISPLAY_WIDTH * scale_factor, DISPLAY_HEIGHT * scale_factor), Image.NEAREST)
        
        # Create Tkinter window
        root = tk.Tk()
        root.title("Waveshare 1.44inch LCD Controller Simulator")
        
        # Convert PIL image to PhotoImage
        from PIL import ImageTk
        photo = ImageTk.PhotoImage(scaled_image)
        
        # Create label to display image
        label = tk.Label(root, image=photo)
        label.pack()
        
        # Add info text
        info_label = tk.Label(root, text=f"Simulated {DISPLAY_WIDTH}x{DISPLAY_HEIGHT} LCD Display (scaled {scale_factor}x)")
        info_label.pack()
        
        # Add control info
        control_label = tk.Label(root, text="Use arrow keys to navigate, Enter to select, 1/3 for positive/negative")
        control_label.pack()
        
        # Add status info
        status_label = tk.Label(root, text="Menu: 0, State: none, Pos: 0, Neg: 0")
        status_label.pack()
        
        # Add close button
        close_button = tk.Button(root, text="Close", command=root.destroy)
        close_button.pack()
        
        # Keyboard event handling for laptop simulation
        def on_key(event):
            global menu, pos, neg, state
            
            if event.keysym == 'Up':
                if state == "none":
                    state = "start"
                elif state == "start":
                    menu = (menu - 1) % 4
                    check_menu()
                    redraw_display()
            elif event.keysym == 'Down':
                if state == "none":
                    state = "start"
                elif state == "start":
                    menu = (menu + 1) % 4
                    check_menu()
                    redraw_display()
            elif event.keysym == 'Left':
                if state == "choosing":
                    neg = (neg + 1) % 5
                    if neg == 0:
                        neg = 1
                    pos = 0
                    check_neg()
                    redraw_display()
            elif event.keysym == 'Right':
                if state == "choosing":
                    pos = (pos + 1) % 5
                    if pos == 0:
                        pos = 1
                    neg = 0
                    check_pos()
                    redraw_display()
            elif event.keysym == 'Return':  # Enter key
                if state == "start":
                    state = "choosing"
                    pos = 1
                    neg = 0
                    redraw_display()
                elif state == "choosing":
                    print(f"Selected: Menu {menu}, {'Positive' if pos > 0 else 'Negative'} {pos if pos > 0 else neg}")
                    reset_state()
                    redraw_display()
            
            # Update status label
            status_label.config(text=f"Menu: {menu}, State: {state}, Pos: {pos}, Neg: {neg}")
        
        root.bind('<Key>', on_key)
        root.focus_set()
        
        root.mainloop()

# === Main control loop (Raspberry Pi only) ===
def main_control_loop():
    if not is_raspberry_pi():
        return
    
    print("Emoji OS Zero started. Use the joystick and buttons to navigate.")
    print("Joystick: Navigate menus")
    print("KEY1: Select positive")
    print("KEY2: Navigate/confirm")
    print("KEY3: Select negative")
    print("=" * 50)
    
    # Initial display
    redraw_display()
    
    while True:
        # Check joystick inputs for menu navigation
        if GPIO.input(KEY_UP_PIN) == 0:  # Up pressed
            if state == "none":
                state = "start"
            elif state == "start":
                menu = (menu - 1) % 4
                check_menu()
                redraw_display()
            print('Up - Menu:', menu)
            time.sleep(0.2)  # Debounce
            
        elif GPIO.input(KEY_DOWN_PIN) == 0:  # Down pressed
            if state == "none":
                state = "start"
            elif state == "start":
                menu = (menu + 1) % 4
                check_menu()
                redraw_display()
            print('Down - Menu:', menu)
            time.sleep(0.2)  # Debounce
            
        elif GPIO.input(KEY_LEFT_PIN) == 0:  # Left pressed
            if state == "choosing":
                neg = (neg + 1) % 5
                if neg == 0:
                    neg = 1
                pos = 0
                check_neg()
                redraw_display()
            print('Left - Negative:', neg)
            time.sleep(0.2)  # Debounce
            
        elif GPIO.input(KEY_RIGHT_PIN) == 0:  # Right pressed
            if state == "choosing":
                pos = (pos + 1) % 5
                if pos == 0:
                    pos = 1
                check_pos()
                redraw_display()
            print('Right - Positive:', pos)
            time.sleep(0.2)  # Debounce
            
        elif GPIO.input(KEY_PRESS_PIN) == 0:  # Center pressed
            if state == "start":
                state = "choosing"
                pos = 1
                neg = 0
                redraw_display()
            elif state == "choosing":
                print(f"Selected: Menu {menu}, {'Positive' if pos > 0 else 'Negative'} {pos if pos > 0 else neg}")
                reset_state()
                redraw_display()
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
                redraw_display()
            elif state == "start":
                state = "choosing"
                pos = 1
                neg = 0
                redraw_display()
            elif prev_state == "done":
                if prev_neg > 0:
                    pos = prev_neg
                    neg = 0
                    menu = prev_menu
                    redraw_display()
                elif prev_pos > 0:
                    pos = prev_pos
                    neg = 0
                    menu = prev_menu
                    redraw_display()
            print('KEY1 - Positive:', pos)
            time.sleep(0.2)  # Debounce
            
        elif GPIO.input(KEY2_PIN) == 0:  # KEY2 pressed
            reset_prev()
            if state == "start":
                menu = (menu + 1) % 4
                check_menu()
                redraw_display()
            elif state == "none":
                state = "start"
                check_menu()
                redraw_display()
            elif state == "choosing":
                print(f"Selected: Menu {menu}, {'Positive' if pos > 0 else 'Negative'} {pos if pos > 0 else neg}")
                reset_state()
                redraw_display()
            print('KEY2 - Menu:', menu)
            time.sleep(0.2)  # Debounce
            
        elif GPIO.input(KEY3_PIN) == 0:  # KEY3 pressed
            if state == "choosing":
                neg = (neg + 1) % 5
                if neg == 0:
                    neg = 1
                pos = 0
                check_neg()
                redraw_display()
            elif state == "start":
                state = "choosing"
                neg = 1
                pos = 0
                redraw_display()
            elif prev_state == "done":
                if prev_pos > 0:
                    neg = prev_pos
                    pos = 0
                    menu = prev_menu
                    redraw_display()
                elif prev_neg > 0:
                    neg = prev_neg
                    pos = 0
                    menu = prev_menu
                    redraw_display()
            print('KEY3 - Negative:', neg)
            time.sleep(0.2)  # Debounce
        
        time.sleep(0.1)  # Small delay to prevent excessive CPU usage

# === Main execution ===
if __name__ == "__main__":
    print("Starting LCD Menu Controller...")
    print(f"Display dimensions: {DISPLAY_WIDTH}x{DISPLAY_HEIGHT}")
    
    if is_raspberry_pi():
        print("Running on Raspberry Pi with LCD hardware")
        try:
            main_control_loop()
        except KeyboardInterrupt:
            print("\nExiting...")
            GPIO.cleanup()
    else:
        print("Running on laptop - showing LCD simulation with keyboard controls")
        redraw_display()  # Draw initial display
        show_simulation()