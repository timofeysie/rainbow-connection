# -*- coding:utf-8 -*-
import LCD_1in44
from PIL import Image, ImageDraw, ImageFont

# === Initialize display ===
disp = LCD_1in44.LCD()
disp.LCD_Init(LCD_1in44.SCAN_DIR_DFT)
disp.LCD_Clear()

# === Create blank canvas ===
image = Image.new('RGB', (disp.width, disp.height), color=(0, 0, 0))
draw = ImageDraw.Draw(image)

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
    ' ': (0, 0, 0),  # background
}

# === Function to draw a single scaled pixel ===
def draw_pixel(draw, x, y, color, scale):
    x0 = x
    y0 = y
    x1 = x + scale
    y1 = y + scale
    draw.rectangle((x0, y0, x1, y1), fill=color)

# === Reusable function to draw emoji ===
def draw_emoji(draw, matrix, color_map, scale, top_left_x, top_left_y):
    for row in range(len(matrix)):
        for col in range(len(matrix[row])):
            symbol = matrix[row][col]
            color = color_map.get(symbol, (0, 0, 0))
            x = top_left_x + col * scale
            y = top_left_y + row * scale
            draw_pixel(draw, x, y, color, scale)

# === Function to draw text centered ===
def draw_centered_text(draw, text, y_position, font, max_width):
    text_width, text_height = draw.textsize(text, font=font)
    x_position = (max_width - text_width) // 2  # center the text
    draw.text((x_position, y_position), text, font=font, fill="white")

# === Load a font (you can adjust the size) ===
font = ImageFont.load_default()

# === main emoji ===
scale = 7
emoji_width = scale * 8
emoji_height = scale * 8
start_x = (disp.width - emoji_width) // 2
start_y = disp.height // 2
draw_emoji(draw, smiley_matrix, color_map, scale, start_x, start_y)

# menu left side emojis
# === emoji 1 ===#
draw_emoji(draw, smiley_matrix, color_map, 1.5, 5, 1)
# === emoji 1 ===#
draw_emoji(draw, smiley_matrix, color_map, 1.5, 5, 16)
# === emoji 2 ===#
draw_emoji(draw, smiley_matrix, color_map, 1.5, 5, 31)
# === emoji 1 ===#
draw_emoji(draw, smiley_matrix, color_map, 1.5, 5, 46)

# menu right side emojis
x_pos = 110
# === emoji 1 ===#
draw_emoji(draw, smiley_matrix, color_map, 1.5, x_pos, 1)
# === emoji 1 ===#
draw_emoji(draw, smiley_matrix, color_map, 1.5, x_pos, 16)
# === emoji 2 ===#
draw_emoji(draw, smiley_matrix, color_map, 1.5, x_pos, 31)
# === emoji 1 ===#
draw_emoji(draw, smiley_matrix, color_map, 1.5, x_pos, 46)

# === Menu Texts ===
menu_items = ["Emojis", "Animations", "Characters", "Other"]

# Draw text for each row of emojis (left side and right side)
text_y_positions = [5, 20, 35, 50]  # Y positions for the text, corresponding to emoji rows

# Draw text for left side menu
for i, item in enumerate(menu_items):
    draw_centered_text(draw, item, text_y_positions[i], font, disp.width)

# Draw text for right side menu
for i, item in enumerate(menu_items):
    draw_centered_text(draw, item, text_y_positions[i], font, disp.width)

# Display on LCD
disp.LCD_ShowImage(image, 0, 0)

# Keep it on screen
input("Smiley drawn using reusable function. Press Enter to exit...")
