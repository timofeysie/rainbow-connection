# -*- coding:utf-8 -*-
"""
Test script to verify emoji matrices display correctly
This can be run on a laptop to preview the emojis before testing on the device
"""
from PIL import Image, ImageDraw, ImageFont

# Create a test image
width, height = 240, 240
image = Image.new('RGB', (width, height), (0, 0, 0))
draw = ImageDraw.Draw(image)

# Emoji matrices from emoji_os_zero_1.py
regular_matrix = [
    [' ', 'Y', 'Y', 'Y', 'Y', 'Y', 'Y', ' '],
    ['Y', 'Y', 'Y', 'Y', 'Y', 'Y', 'Y', 'Y'],
    ['Y', 'B', 'Y', 'Y', 'Y', 'Y', 'B', 'Y'],
    ['Y', 'B', 'Y', 'Y', 'Y', 'Y', 'B', 'Y'],
    ['Y', 'Y', 'Y', 'Y', 'Y', 'Y', 'Y', 'Y'],
    ['Y', 'Y', 'Y', 'Y', 'Y', 'B', 'Y', 'Y'],
    ['Y', 'Y', 'B', 'B', 'B', 'Y', 'Y', 'Y'],
    [' ', 'Y', 'Y', 'Y', 'Y', 'Y', 'Y', ' '],
]

happy_matrix = [
    [' ', 'Y', 'Y', 'Y', 'Y', 'Y', 'Y', ' '],
    ['Y', 'Y', 'Y', 'Y', 'Y', 'Y', 'Y', 'Y'],
    ['Y', 'B', 'Y', 'Y', 'Y', 'Y', 'B', 'Y'],
    ['Y', 'B', 'Y', 'Y', 'Y', 'Y', 'B', 'Y'],
    ['Y', 'Y', 'Y', 'Y', 'Y', 'Y', 'Y', 'Y'],
    ['Y', 'Y', 'Y', 'Y', 'Y', 'B', 'Y', 'Y'],
    ['Y', 'Y', 'B', 'B', 'B', 'Y', 'Y', 'Y'],
    [' ', 'Y', 'Y', 'Y', 'Y', 'Y', 'Y', ' '],
]

wry_matrix = [
    [' ', 'Y', 'Y', 'Y', 'Y', 'Y', 'Y', ' '],
    ['Y', 'Y', 'Y', 'Y', 'Y', 'Y', 'Y', 'Y'],
    ['Y', 'B', 'Y', 'Y', 'Y', 'B', 'Y', 'Y'],
    ['Y', 'B', 'Y', 'Y', 'Y', 'B', 'Y', 'Y'],
    ['Y', 'Y', 'Y', 'Y', 'Y', 'B', 'Y', 'Y'],
    ['Y', 'Y', 'B', 'B', 'B', 'Y', 'Y', 'Y'],
    ['Y', 'Y', 'B', 'B', 'B', 'Y', 'Y', 'Y'],
    [' ', 'Y', 'Y', 'Y', 'Y', 'Y', 'Y', ' '],
]

heart_matrix = [
    [' ', 'R', 'R', ' ', ' ', 'R', 'R', ' '],
    ['R', 'R', 'R', 'R', 'R', 'R', 'R', 'R'],
    ['R', 'R', 'R', 'R', 'R', 'R', 'R', 'R'],
    ['R', 'R', 'R', 'R', 'R', 'R', 'R', 'R'],
    [' ', 'R', 'R', 'R', 'R', 'R', 'R', ' '],
    [' ', ' ', 'R', 'R', 'R', 'R', ' ', ' '],
    [' ', ' ', ' ', 'R', 'R', ' ', ' ', ' '],
    [' ', ' ', ' ', ' ', ' ', ' ', ' ', ' '],
]

thick_lips_matrix = [
    [' ', 'Y', 'Y', 'Y', 'Y', 'Y', 'Y', ' '],
    ['Y', 'Y', 'Y', 'Y', 'Y', 'Y', 'Y', 'Y'],
    ['Y', 'B', 'Y', 'Y', 'Y', 'Y', 'B', 'Y'],
    ['Y', 'B', 'Y', 'Y', 'Y', 'Y', 'B', 'Y'],
    ['Y', 'Y', 'Y', 'Y', 'Y', 'Y', 'Y', 'Y'],
    ['Y', 'Y', 'B', 'B', 'B', 'B', 'Y', 'Y'],
    ['Y', 'Y', 'B', 'B', 'B', 'B', 'Y', 'Y'],
    [' ', 'Y', 'Y', 'Y', 'Y', 'Y', 'Y', ' '],
]

sad_matrix = [
    [' ', 'Y', 'Y', 'Y', 'Y', 'Y', 'Y', ' '],
    ['Y', 'Y', 'Y', 'Y', 'Y', 'Y', 'Y', 'Y'],
    ['Y', 'B', 'Y', 'Y', 'Y', 'Y', 'B', 'Y'],
    ['Y', 'B', 'Y', 'Y', 'Y', 'Y', 'B', 'Y'],
    ['Y', 'Y', 'Y', 'Y', 'Y', 'Y', 'Y', 'Y'],
    ['Y', 'Y', 'Y', 'Y', 'Y', 'B', 'Y', 'Y'],
    ['Y', 'Y', 'B', 'B', 'B', 'Y', 'Y', 'Y'],
    [' ', 'Y', 'Y', 'Y', 'Y', 'Y', 'Y', ' '],
]

angry_matrix = [
    ['R', ' ', 'R', 'R', 'R', 'R', ' ', 'R'],
    ['R', 'R', ' ', 'R', 'R', ' ', 'R', 'R'],
    ['R', 'B', 'Y', ' ', ' ', 'Y', 'B', 'R'],
    ['R', 'R', 'R', 'R', 'R', 'R', 'R', 'R'],
    ['R', 'R', 'R', 'R', 'R', 'R', 'R', 'R'],
    ['R', 'R', ' ', ' ', ' ', ' ', 'R', 'R'],
    ['R', ' ', 'R', 'R', 'R', 'R', ' ', 'R'],
    ['R', 'R', 'R', 'R', 'R', 'R', 'R', 'R'],
]

green_monster_matrix = [
    [' ', 'G', 'G', 'G', 'G', 'G', 'G', ' '],
    ['G', 'G', 'G', 'G', 'G', 'G', 'G', 'G'],
    ['G', 'R', 'G', 'G', 'G', 'G', 'R', 'G'],
    ['G', 'G', 'G', 'G', 'G', 'G', 'G', 'G'],
    ['G', 'G', 'G', 'W', 'W', 'G', 'G', 'G'],
    ['G', ' ', ' ', ' ', ' ', ' ', ' ', 'G'],
    ['G', 'W', ' ', 'W', 'W', ' ', 'W', 'G'],
    ['G', 'G', 'G', 'G', 'G', 'G', 'G', 'G'],
]

color_map = {
    'Y': 'yellow',
    'B': 'black',
    'R': 'red',
    'G': 'green',
    'W': 'white',
    ' ': (0, 0, 0),
}

def draw_pixel(draw, x, y, color, scale):
    x0 = x
    y0 = y
    x1 = x + scale
    y1 = y + scale
    draw.rectangle((x0, y0, x1, y1), fill=color)

def draw_emoji(draw, matrix, color_map, scale, top_left_x, top_left_y):
    for row in range(len(matrix)):
        for col in range(len(matrix[row])):
            symbol = matrix[row][col]
            color = color_map.get(symbol, (0, 0, 0))
            x = top_left_x + col * scale
            y = top_left_y + row * scale
            draw_pixel(draw, x, y, color, scale)

# Test all emojis
emojis = [
    ("Regular", regular_matrix),
    ("Happy", happy_matrix),
    ("Wry", wry_matrix),
    ("Heart", heart_matrix),
    ("Thick Lips", thick_lips_matrix),
    ("Sad", sad_matrix),
    ("Angry", angry_matrix),
    ("Green Monster", green_monster_matrix),
]

# Draw emojis in a grid
scale = 15
emoji_size = 8 * scale
spacing = 10

for i, (name, matrix) in enumerate(emojis):
    row = i // 4
    col = i % 4
    
    x = col * (emoji_size + spacing) + spacing
    y = row * (emoji_size + spacing) + spacing
    
    # Draw emoji
    draw_emoji(draw, matrix, color_map, scale, x, y)
    
    # Draw label
    try:
        font = ImageFont.load_default()
    except:
        font = ImageFont.load_default()
    
    draw.text((x, y + emoji_size + 2), name, font=font, fill="white")

# Save the test image
image.save("emoji_test.png")
print("Emoji test image saved as emoji_test.png")
print("Check the image to verify all emojis display correctly")
