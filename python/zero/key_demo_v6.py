# -*- coding:utf-8 -*-
import LCD_1in44

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

# === Menu state ===
selected_menu = 0  # Start with first item selected

# === Function to draw a single scaled pixel ===
def draw_pixel(draw, x, y, color, scale):
    x0 = x
    y0 = y
    x1 = x + scale
    y1 = y + scale
    draw.rectangle((x0, y0, x1, y1), fill=color)

# === Function to draw emoji ===
def draw_emoji(draw, matrix, color_map, scale, top_left_x, top_left_y):
    for row in range(len(matrix)):
        for col in range(len(matrix[row])):
            symbol = matrix[row][col]
            color = color_map.get(symbol, (0, 0, 0))
            x = top_left_x + col * scale
            y = top_left_y + row * scale
            draw_pixel(draw, x, y, color, scale)

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
    row_height = 15
    row_y = y_position
    
    if is_selected:
        # Draw white background for selected row
        bg_width = 80  # Width of menu text area
        bg_x = (disp.width - bg_width) // 2  # Center the background
        draw.rectangle((bg_x, row_y, bg_x + bg_width, row_y + row_height), fill="white")
        draw_centered_text(draw, text, row_y, font, disp.width, "black")
    else:
        draw_centered_text(draw, text, row_y, font, disp.width, "white")

# === Function to handle menu navigation ===
def handle_menu_navigation():
    global selected_menu
    
    # Check for UP button (move menu up)
    if disp.digital_read(disp.GPIO_KEY_UP_PIN) == 0:
        selected_menu = (selected_menu - 1) % len(menu_items)
        print(f"Menu UP - Selected: {menu_items[selected_menu]}")
        return True
    
    # Check for DOWN button (move menu down)
    if disp.digital_read(disp.GPIO_KEY_DOWN_PIN) == 0:
        selected_menu = (selected_menu + 1) % len(menu_items)
        print(f"Menu DOWN - Selected: {menu_items[selected_menu]}")
        return True
    
    # Check for KEY1 (move menu up)
    if disp.digital_read(disp.GPIO_KEY1_PIN) == 0:
        selected_menu = (selected_menu - 1) % len(menu_items)
        print(f"KEY1 - Menu UP - Selected: {menu_items[selected_menu]}")
        return True
    
    # Check for KEY2 (move menu down)
    if disp.digital_read(disp.GPIO_KEY2_PIN) == 0:
        selected_menu = (selected_menu + 1) % len(menu_items)
        print(f"KEY2 - Menu DOWN - Selected: {menu_items[selected_menu]}")
        return True
    
    # Check for KEY3 (move menu down)
    if disp.digital_read(disp.GPIO_KEY3_PIN) == 0:
        selected_menu = (selected_menu + 1) % len(menu_items)
        print(f"KEY3 - Menu DOWN - Selected: {menu_items[selected_menu]}")
        return True
    
    return False

try:
    while True:
        # === Handle menu navigation ===
        menu_changed = handle_menu_navigation()
        
        # === Draw joystick indicators in top half ===
        if disp.digital_read(disp.GPIO_KEY_UP_PIN ) == 0: # button is released       
            draw.polygon([(20, 20), (30, 2), (40, 20)], outline=255, fill=0xff00)  #Up           
        else: # button is pressed:
            draw.polygon([(20, 20), (30, 2), (40, 20)], outline=255, fill=0)  #Up filled

        if disp.digital_read(disp.GPIO_KEY_LEFT_PIN) == 0: # button is released
            draw.polygon([(0, 30), (18, 21), (18, 41)], outline=255, fill=0xff00)  #left      
        else: # button is pressed:       
            draw.polygon([(0, 30), (18, 21), (18, 41)], outline=255, fill=0)  #left filled

        if disp.digital_read(disp.GPIO_KEY_RIGHT_PIN) == 0: # button is released
            draw.polygon([(60, 30), (42, 21), (42, 41)], outline=255, fill=0xff00) #right
        else: # button is pressed:
            draw.polygon([(60, 30), (42, 21), (42, 41)], outline=255, fill=0) #right filled       

        if disp.digital_read(disp.GPIO_KEY_DOWN_PIN) == 0: # button is released
            draw.polygon([(30, 60), (40, 42), (20, 42)], outline=255, fill=0xff00) #down   
        else: # button is pressed:
            draw.polygon([(30, 60), (40, 42), (20, 42)], outline=255, fill=0) #down filled

        if disp.digital_read(disp.GPIO_KEY_PRESS_PIN) == 0: # button is released
            draw.rectangle((20, 22,40,40), outline=255, fill=0xff00) #center        
        else: # button is pressed:
            draw.rectangle((20, 22,40,40), outline=255, fill=0) #center filled

        if disp.digital_read(disp.GPIO_KEY1_PIN) == 0: # button is released
            draw.ellipse((70,0,90,20), outline=255, fill=0xff00) #A button       
        else: # button is pressed:
            draw.ellipse((70,0,90,20), outline=255, fill=0) #A button filled

        if disp.digital_read(disp.GPIO_KEY2_PIN) == 0: # button is released
            draw.ellipse((100,20,120,40), outline=255, fill=0xff00) #B button] 
        else: # button is pressed:
            draw.ellipse((100,20,120,40), outline=255, fill=0) #B button filled

        if disp.digital_read(disp.GPIO_KEY3_PIN) == 0: # button is released
            draw.ellipse((70,40,90,60), outline=255, fill=0xff00) #A button
        else: # button is pressed:
            draw.ellipse((70,40,90,60), outline=255, fill=0) #A button filled

        # === Draw main menu demo in top half ===
        # Clear top half
        draw.rectangle((0, 0, disp.width, 64), outline=0, fill=0)
        
        # Draw menu items with current selection
        text_y_positions = [5, 20, 35, 50]
        font = ImageFont.load_default()
        
        for i, item in enumerate(menu_items):
            is_selected = (i == selected_menu)  # Use current selection
            draw_menu_row(draw, item, text_y_positions[i], font, is_selected)
        
        # Draw small emojis on left and right sides
        # Left side emojis
        draw_emoji(draw, smiley_matrix, color_map, 1.5, 5, 1)
        draw_emoji(draw, smiley_matrix, color_map, 1.5, 5, 16)
        draw_emoji(draw, smiley_matrix, color_map, 1.5, 5, 31)
        draw_emoji(draw, smiley_matrix, color_map, 1.5, 5, 46)
        
        # Right side emojis
        draw_emoji(draw, smiley_matrix, color_map, 1.5, 110, 1)
        draw_emoji(draw, smiley_matrix, color_map, 1.5, 110, 16)
        draw_emoji(draw, smiley_matrix, color_map, 1.5, 110, 31)
        draw_emoji(draw, smiley_matrix, color_map, 1.5, 110, 46)

        # === Draw main emoji in bottom half ===
        scale = 7
        emoji_width = scale * 8
        emoji_height = scale * 8
        start_x = (disp.width - emoji_width) // 2
        start_y = 55 + (64 - emoji_height) // 2
        draw_emoji(draw, smiley_matrix, color_map, scale, start_x, start_y)

        disp.LCD_ShowImage(image,0,0)
except:
	print("except")
disp.module_exit()
