# -*- coding:utf-8 -*-
import LCD_1in44
import time

from PIL import Image,ImageDraw,ImageFont,ImageColor

# 240x240 display with hardware SPI:
disp = LCD_1in44.LCD()
Lcd_ScanDir = LCD_1in44.SCAN_DIR_DFT  #SCAN_DIR_DFT = D2U_L2R
disp.LCD_Init(Lcd_ScanDir)
disp.LCD_Clear()

# Create blank image for drawing.
# Make sure to create image with mode '1' for 1-bit color.
image = Image.new('RGB', (disp.width, disp.height))

# Get drawing object to draw on image.
draw = ImageDraw.Draw(image)

# Draw a black filled box to clear the image.
draw.rectangle((0,0,disp.width,disp.height), outline=0, fill=0)
disp.LCD_ShowImage(image,0,0)

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

# === Menu state variables (matching emoji_key_basic.py) ===
menu = 0
pos = 0
neg = 0
state = "none"  # start, end, or none
# preserve the previous state for pos/neg flipping
prev_menu = 0
prev_pos = 0
prev_neg = 0
prev_state = "none"  # or done

# === Button state tracking for debouncing ===
button_states = {
    'up': None,
    'down': None,
    'left': None,
    'right': None,
    'center': None,
    'key1': None,
    'key2': None,
    'key3': None
}

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
        emoji_width = len(matrix[0]) * scale
        emoji_height = len(matrix) * scale
        border_width = 1
        draw.rectangle(
            (top_left_x - border_width, top_left_y - border_width, 
             top_left_x + emoji_width + border_width, top_left_y + emoji_height + border_width),
            outline="white",
            width=border_width
        )

# === Function to draw text centered ===
def draw_centered_text(draw, text, y_position, font, max_width, text_color="white"):
    try:
        bbox = draw.textbbox((0, 0), text, font=font)
        text_width = bbox[2] - bbox[0]
        text_height = bbox[3] - bbox[1]
    except AttributeError:
        text_width, text_height = draw.textsize(text, font=font)
    
    x_position = (max_width - text_width) // 2
    draw.text((x_position, y_position), text, font=font, fill=text_color)

# === Function to draw menu row with selection styling ===
def draw_menu_row(draw, text, y_position, font, is_selected=False):
    row_height = 14
    row_y = y_position
    
    if is_selected:
        bg_width = 80
        bg_x = (disp.width - bg_width) // 2
        draw.rectangle((bg_x, row_y, bg_x + bg_width, row_y + row_height), fill="white")
        
        try:
            bbox = draw.textbbox((0, 0), text, font=font)
            text_height = bbox[3] - bbox[1]
        except AttributeError:
            _, text_height = draw.textsize(text, font=font)
        
        text_y_centered = row_y + (row_height - text_height) // 2
        draw_centered_text(draw, text, text_y_centered, font, disp.width, "black")
    else:
        draw_centered_text(draw, text, row_y, font, disp.width, "white")

# === Function to check for button press (with debouncing) ===
def check_button_press(button_name, pin):
    current_state = disp.digital_read(pin) == 0
    previous_state = button_states[button_name]
    
    if previous_state is None:
        button_states[button_name] = current_state
        return False
    
    if current_state and not previous_state:
        button_states[button_name] = current_state
        return True
    
    button_states[button_name] = current_state
    return False

# === Menu control functions (matching emoji_key_basic.py) ===
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

# === Function to handle menu navigation (matching emoji_key_basic.py logic) ===
def handle_menu_navigation():
    global menu, pos, neg, state, prev_menu, prev_pos, prev_neg, prev_state
    
    # Check joystick inputs for menu navigation
    if check_button_press('up', disp.GPIO_KEY_UP_PIN):  # Up pressed
        if state == "none":
            state = "start"
        elif state == "start":
            menu = (menu - 1) % 4
            check_menu()
        print('Up - Menu:', menu)
        time.sleep(0.2)  # Debounce
        return True
        
    elif check_button_press('down', disp.GPIO_KEY_DOWN_PIN):  # Down pressed
        if state == "none":
            state = "start"
        elif state == "start":
            menu = (menu + 1) % 4
            check_menu()
        print('Down - Menu:', menu)
        time.sleep(0.2)  # Debounce
        return True
        
    elif check_button_press('left', disp.GPIO_KEY_LEFT_PIN):  # Left pressed
        if state == "choosing":
            neg = (neg + 1) % 5
            if neg == 0:
                neg = 1
            pos = 0
            check_neg()
        print('Left - Negative:', neg)
        time.sleep(0.2)  # Debounce
        return True
        
    elif check_button_press('right', disp.GPIO_KEY_RIGHT_PIN):  # Right pressed
        if state == "choosing":
            pos = (pos + 1) % 5
            if pos == 0:
                pos = 1
            neg = 0
            check_pos()
        print('Right - Positive:', pos)
        time.sleep(0.2)  # Debounce
        return True
        
    elif check_button_press('center', disp.GPIO_KEY_PRESS_PIN):  # Center pressed
        if state == "start":
            state = "choosing"
            pos = 1
            neg = 0
        elif state == "choosing":
            print(f"Selected: Menu {menu}, {'Positive' if pos > 0 else 'Negative'} {pos if pos > 0 else neg}")
            reset_state()
        print('Center pressed')
        time.sleep(0.2)  # Debounce
        return True
        
    # Check button inputs
    elif check_button_press('key1', disp.GPIO_KEY1_PIN):  # KEY1 pressed
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
            elif prev_pos > 0:
                pos = prev_pos
                neg = 0
                menu = prev_menu
        print('KEY1 - Positive:', pos)
        time.sleep(0.2)  # Debounce
        return True
        
    elif check_button_press('key2', disp.GPIO_KEY2_PIN):  # KEY2 pressed
        reset_prev()
        if state == "start":
            menu = (menu + 1) % 4
            check_menu()
        elif state == "none":
            state = "start"
            check_menu()
        elif state == "choosing":
            print(f"Selected: Menu {menu}, {'Positive' if pos > 0 else 'Negative'} {pos if pos > 0 else neg}")
            reset_state()
        print('KEY2 - Menu:', menu)
        time.sleep(0.2)  # Debounce
        return True
        
    elif check_button_press('key3', disp.GPIO_KEY3_PIN):  # KEY3 pressed
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
            elif prev_neg > 0:
                neg = prev_neg
                pos = 0
                menu = prev_menu
        print('KEY3 - Negative:', neg)
        time.sleep(0.2)  # Debounce
        return True
    
    return False

try:
    while True:
        # === Handle menu navigation ===
        handle_menu_navigation()
        
        # === Draw joystick indicators in top half ===
        if disp.digital_read(disp.GPIO_KEY_UP_PIN ) == 0:
            draw.polygon([(20, 20), (30, 2), (40, 20)], outline=255, fill=0xff00)
        else:
            draw.polygon([(20, 20), (30, 2), (40, 20)], outline=255, fill=0)

        if disp.digital_read(disp.GPIO_KEY_LEFT_PIN) == 0:
            draw.polygon([(0, 30), (18, 21), (18, 41)], outline=255, fill=0xff00)
        else:
            draw.polygon([(0, 30), (18, 21), (18, 41)], outline=255, fill=0)

        if disp.digital_read(disp.GPIO_KEY_RIGHT_PIN) == 0:
            draw.polygon([(60, 30), (42, 21), (42, 41)], outline=255, fill=0xff00)
        else:
            draw.polygon([(60, 30), (42, 21), (42, 41)], outline=255, fill=0)

        if disp.digital_read(disp.GPIO_KEY_DOWN_PIN) == 0:
            draw.polygon([(30, 60), (40, 42), (20, 42)], outline=255, fill=0xff00)
        else:
            draw.polygon([(30, 60), (40, 42), (20, 42)], outline=255, fill=0)

        if disp.digital_read(disp.GPIO_KEY_PRESS_PIN) == 0:
            draw.rectangle((20, 22,40,40), outline=255, fill=0xff00)
        else:
            draw.rectangle((20, 22,40,40), outline=255, fill=0)

        if disp.digital_read(disp.GPIO_KEY1_PIN) == 0:
            draw.ellipse((70,0,90,20), outline=255, fill=0xff00)
        else:
            draw.ellipse((70,0,90,20), outline=255, fill=0)

        if disp.digital_read(disp.GPIO_KEY2_PIN) == 0:
            draw.ellipse((100,20,120,40), outline=255, fill=0xff00)
        else:
            draw.ellipse((100,20,120,40), outline=255, fill=0)

        if disp.digital_read(disp.GPIO_KEY3_PIN) == 0:
            draw.ellipse((70,40,90,60), outline=255, fill=0xff00)
        else:
            draw.ellipse((70,40,90,60), outline=255, fill=0)

        # === Draw main menu demo in top half ===
        draw.rectangle((0, 0, disp.width, 64), outline=0, fill=0)
        
        # Draw menu items with current selection
        text_y_positions = [5, 20, 35, 50]
        font = ImageFont.load_default()
        
        for i, item in enumerate(menu_items):
            is_selected = (i == menu)
            draw_menu_row(draw, item, text_y_positions[i], font, is_selected)
        
        # Draw small emojis on left and right sides with selection
        emoji_y_positions = [1, 16, 31, 46]
        
        # Left side emojis (negative/left side)
        for i in range(4):
            show_selection = (state == "choosing" and neg > 0 and neg == i + 1)
            draw_emoji(draw, smiley_matrix, color_map, 1.5, 5, emoji_y_positions[i], show_selection)
        
        # Right side emojis (positive/right side)
        for i in range(4):
            show_selection = (state == "choosing" and pos > 0 and pos == i + 1)
            draw_emoji(draw, smiley_matrix, color_map, 1.5, 110, emoji_y_positions[i], show_selection)

        # === Draw main emoji in bottom half ===
        scale = 7
        emoji_width = scale * 8
        emoji_height = scale * 8
        start_x = (disp.width - emoji_width) // 2
        start_y = 64 + (64 - emoji_height) // 2
        draw_emoji(draw, smiley_matrix, color_map, scale, start_x, start_y)

        disp.LCD_ShowImage(image,0,0)
        time.sleep(0.05)
        
except:
	print("except")
disp.module_exit()
