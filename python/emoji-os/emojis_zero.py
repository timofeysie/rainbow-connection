# -*- coding:utf-8 -*-
# Emoji matrices and helper functions for emoji-os-zero.py
# v0.0.2 for emoji os zero v0.3.8
from animations_zero import fireworks_preview_matrix, rain_preview_matrix, Animation

# === Emoji Matrix Data ===
# Menu 0 emojis Pos
# Regular emoji
regular_matrix = [
    [' ', 'Y', 'Y', 'Y', 'Y', 'Y', 'Y', ' '],
    ['Y', 'Y', 'Y', 'Y', 'Y', 'Y', 'Y', 'Y'],
    ['Y', 'B', 'Y', 'Y', 'Y', 'B', 'Y', 'Y'],
    ['Y', 'B', 'Y', 'Y', 'Y', 'B', 'Y', 'Y'],
    ['Y', 'Y', 'Y', 'Y', 'Y', 'Y', 'Y', 'Y'],
    ['Y', 'Y', 'Y', 'Y', 'Y', 'Y', 'Y', 'Y'],
    ['Y', 'Y', 'B', 'B', 'B', 'Y', 'Y', 'Y'],
    [' ', 'Y', 'Y', 'Y', 'Y', 'Y', 'Y', ' '],
]

# Regular emoji wink state
regular_wink_matrix = [
    [' ', 'Y', 'Y', 'Y', 'Y', 'Y', 'Y', ' '],
    ['Y', 'Y', 'Y', 'Y', 'Y', 'Y', 'Y', 'Y'],
    ['Y', 'B', 'Y', 'Y', 'Y', 'Y', 'Y', 'Y'],
    ['Y', 'B', 'Y', 'Y', 'Y', 'B', 'Y', 'Y'],
    ['Y', 'Y', 'Y', 'Y', 'Y', 'Y', 'Y', 'Y'],
    ['Y', 'Y', 'Y', 'Y', 'Y', 'Y', 'Y', 'Y'],
    ['Y', 'Y', 'B', 'B', 'B', 'Y', 'Y', 'Y'],
    [' ', 'Y', 'Y', 'Y', 'Y', 'Y', 'Y', ' '],
]

# Happy emoji
happy_matrix = [
    [' ', 'Y', 'Y', 'Y', 'Y', 'Y', 'Y', ' '],
    ['Y', 'Y', 'Y', 'Y', 'Y', 'Y', 'Y', 'Y'],
    ['Y', 'B', 'Y', 'Y', 'Y', 'B', 'Y', 'Y'],
    ['Y', 'B', 'Y', 'Y', 'Y', 'B', 'Y', 'Y'],
    ['Y', 'Y', 'Y', 'Y', 'Y', 'Y', 'Y', 'Y'],
    ['Y', 'B', 'Y', 'Y', 'Y', 'B', 'Y', 'Y'],
    ['Y', 'Y', 'B', 'B', 'B', 'Y', 'Y', 'Y'],
    [' ', 'Y', 'Y', 'Y', 'Y', 'Y', 'Y', ' '],
]

# Happy emoji wink state
happy_wink_matrix = [
    [' ', 'Y', 'Y', 'Y', 'Y', 'Y', 'Y', ' '],
    ['Y', 'Y', 'Y', 'Y', 'Y', 'Y', 'Y', 'Y'],
    ['Y', 'B', 'Y', 'Y', 'Y', 'Y', 'Y', 'Y'],
    ['Y', 'B', 'Y', 'Y', 'Y', 'B', 'Y', 'Y'],
    ['Y', 'Y', 'Y', 'Y', 'Y', 'Y', 'Y', 'Y'],
    ['Y', 'B', 'Y', 'Y', 'Y', 'B', 'Y', 'Y'],
    ['Y', 'Y', 'B', 'B', 'B', 'Y', 'Y', 'Y'],
    [' ', 'Y', 'Y', 'Y', 'Y', 'Y', 'Y', ' '],
]

# Wry emoji
wry_matrix = [
    [' ', 'Y', 'Y', 'Y', 'Y', 'Y', 'Y', ' '],
    ['Y', 'Y', 'Y', 'Y', 'Y', 'Y', 'Y', 'Y'],
    ['Y', 'B', 'Y', 'Y', 'Y', 'B', 'Y', 'Y'],
    ['Y', 'B', 'Y', 'Y', 'Y', 'B', 'Y', 'Y'],
    ['Y', 'Y', 'Y', 'Y', 'Y', 'Y', 'Y', 'Y'],
    ['Y', 'Y', 'Y', 'Y', 'Y', 'B', 'Y', 'Y'],
    ['Y', 'Y', 'B', 'B', 'B', 'Y', 'Y', 'Y'],
    [' ', 'Y', 'Y', 'Y', 'Y', 'Y', 'Y', ' '],
]

# Wry emoji wink state
wry_wink_matrix = [
    [' ', 'Y', 'Y', 'Y', 'Y', 'Y', 'Y', ' '],
    ['Y', 'Y', 'Y', 'Y', 'Y', 'Y', 'Y', 'Y'],
    ['Y', 'B', 'Y', 'Y', 'Y', 'Y', 'Y', 'Y'],
    ['Y', 'B', 'Y', 'Y', 'Y', 'B', 'Y', 'Y'],
    ['Y', 'Y', 'Y', 'Y', 'Y', 'Y', 'Y', 'Y'],
    ['Y', 'Y', 'Y', 'Y', 'Y', 'B', 'Y', 'Y'],
    ['Y', 'Y', 'B', 'B', 'B', 'Y', 'Y', 'Y'],
    [' ', 'Y', 'Y', 'Y', 'Y', 'Y', 'Y', ' '],
]

# Heart bounce emoji - state 1
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

# Heart bounce emoji - state 2 (bounced up)
heart_bounce_matrix = [
    [' ', ' ', ' ', ' ', ' ', ' ', ' ', ' '],
    [' ', 'R', 'R', ' ', ' ', 'R', 'R', ' '],
    ['R', 'R', 'R', 'R', 'R', 'R', 'R', 'R'],
    ['R', 'R', 'R', 'R', 'R', 'R', 'R', 'R'],
    ['R', 'R', 'R', 'R', 'R', 'R', 'R', 'R'],
    [' ', 'R', 'R', 'R', 'R', 'R', 'R', ' '],
    [' ', ' ', 'R', 'R', 'R', 'R', ' ', ' '],
    [' ', ' ', ' ', 'R', 'R', ' ', ' ', ' '],
]

# Menu 0 emojis Neg
# Thick lips emoji
thick_lips_matrix = [
    [' ', 'Y', 'Y', 'Y', 'Y', 'Y', 'Y', ' '],
    ['Y', 'Y', 'Y', 'Y', 'Y', 'Y', 'Y', 'Y'],
    ['Y', 'Y', 'B', 'Y', 'Y', 'Y', 'B', 'Y'],
    ['Y', 'Y', 'B', 'Y', 'Y', 'Y', 'B', 'Y'],
    ['Y', 'Y', 'Y', 'Y', 'Y', 'Y', 'Y', 'Y'],
    ['Y', 'Y', 'Y', 'B', 'B', 'B', 'Y', 'Y'],
    ['Y', 'Y', 'Y', 'B', 'B', 'B', 'Y', 'Y'],
    [' ', 'Y', 'Y', 'Y', 'Y', 'Y', 'Y', ' '],
]

# Thick lips emoji wink state
thick_lips_wink_matrix = [
    [' ', 'Y', 'Y', 'Y', 'Y', 'Y', 'Y', ' '],
    ['Y', 'Y', 'Y', 'Y', 'Y', 'Y', 'Y', 'Y'],
    ['Y', 'Y', 'Y', 'Y', 'Y', 'Y', 'B', 'Y'],
    ['Y', 'Y', 'B', 'Y', 'Y', 'Y', 'B', 'Y'],
    ['Y', 'Y', 'Y', 'Y', 'Y', 'Y', 'Y', 'Y'],
    ['Y', 'Y', 'Y', 'B', 'B', 'B', 'Y', 'Y'],
    ['Y', 'Y', 'Y', 'B', 'B', 'B', 'Y', 'Y'],
    [' ', 'Y', 'Y', 'Y', 'Y', 'Y', 'Y', ' '],
]

# Sad emoji
sad_matrix = [
    [' ', 'Y', 'Y', 'Y', 'Y', 'Y', 'Y', ' '],
    ['Y', 'Y', 'Y', 'Y', 'Y', 'Y', 'Y', 'Y'],
    ['Y', 'Y', 'B', 'Y', 'Y', 'Y', 'B', 'Y'],
    ['Y', 'Y', 'B', 'Y', 'Y', 'Y', 'B', 'Y'],
    ['Y', 'Y', 'Y', 'Y', 'Y', 'Y', 'Y', 'Y'],
    ['Y', 'Y', 'Y', 'B', 'B', 'B', 'Y', 'Y'],
    ['Y', 'Y', 'B', 'Y', 'Y', 'Y', 'B', 'Y'],
    [' ', 'Y', 'Y', 'Y', 'Y', 'Y', 'Y', ' '],
]

# Sad emoji wink state
sad_wink_matrix = [
    [' ', 'Y', 'Y', 'Y', 'Y', 'Y', 'Y', ' '],
    ['Y', 'Y', 'Y', 'Y', 'Y', 'Y', 'Y', 'Y'],
    ['Y', 'Y', 'Y', 'Y', 'Y', 'Y', 'Y', 'Y'],
    ['Y', 'Y', 'B', 'Y', 'Y', 'Y', 'B', 'Y'],
    ['Y', 'Y', 'Y', 'Y', 'Y', 'Y', 'Y', 'Y'],
    ['Y', 'Y', 'Y', 'B', 'B', 'B', 'Y', 'Y'],
    ['Y', 'Y', 'B', 'Y', 'Y', 'Y', 'B', 'Y'],
    [' ', 'Y', 'Y', 'Y', 'Y', 'Y', 'Y', ' '],
]

# Angry emoji
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

# Angry emoji wink state
angry_wink_matrix = [
    ['R', ' ', 'R', 'R', 'R', 'R', ' ', 'R'],
    ['R', 'R', ' ', 'R', 'R', ' ', 'R', 'R'],
    ['R', 'Y', 'Y', ' ', ' ', 'Y', 'Y', 'R'],
    ['R', 'R', 'R', 'R', 'R', 'R', 'R', 'R'],
    ['R', 'R', 'R', 'R', 'R', 'R', 'R', 'R'],
    ['R', 'R', ' ', ' ', ' ', ' ', 'R', 'R'],
    ['R', ' ', 'R', 'R', 'R', 'R', ' ', 'R'],
    ['R', 'R', 'R', 'R', 'R', 'R', 'R', 'R'],
]

# Green monster emoji
green_monster_matrix = [
    [' ', 'G', 'G', 'G', 'G', 'G', 'G', ' '],
    ['G', 'G', 'G', 'G', 'G', 'G', 'G', 'G'],
    ['G', 'R', 'G', 'G', 'G', 'G', 'R', 'G'],
    ['G', 'G', 'G', 'G', 'G', 'G', 'G', 'G'],
    ['G', 'G', 'G', 'W', ' ', 'G', 'G', 'G'],
    ['G', ' ', ' ', ' ', ' ', ' ', ' ', 'G'],
    ['G', 'W', ' ', 'W', 'W', ' ', 'W', 'G'],
    ['G', 'G', 'G', 'G', 'G', 'G', 'G', 'G'],
]

# Green monster emoji wink state
green_monster_wink_matrix = [
    [' ', 'G', 'G', 'G', 'G', 'G', 'G', ' '],
    ['G', 'G', 'G', 'G', 'G', 'G', 'G', 'G'],
    ['G', 'Y', 'Y', 'G', 'G', 'Y', 'Y', 'G'],
    ['G', 'G', 'G', 'G', 'G', 'G', 'G', 'G'],
    ['G', 'G', 'G', 'W', ' ', 'G', 'G', 'G'],
    ['G', ' ', ' ', ' ', ' ', ' ', ' ', 'G'],
    ['G', 'W', ' ', 'W', 'W', ' ', 'W', 'G'],
    ['G', 'G', 'G', 'G', 'G', 'G', 'G', 'G'],
]

# Default smiley for menu items
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

# Wink matrix for animation
smiley_wink_matrix = [
    [' ', 'Y', 'Y', 'Y', 'Y', 'Y', 'Y', ' '],
    ['Y', 'Y', 'Y', 'Y', 'Y', 'Y', 'Y', 'Y'],
    ['Y', 'Y', 'Y', 'Y', 'Y', 'Y', 'Y', 'Y'],
    ['Y', 'B', 'Y', 'Y', 'Y', 'Y', 'B', 'Y'],
    ['Y', 'Y', 'Y', 'Y', 'Y', 'Y', 'Y', 'Y'],
    ['Y', 'Y', 'Y', 'Y', 'Y', 'B', 'Y', 'Y'],
    ['Y', 'Y', 'B', 'B', 'B', 'Y', 'Y', 'Y'],
    [' ', 'Y', 'Y', 'Y', 'Y', 'Y', 'Y', ' '],
]

# Chakana (Andean cross) - static 8x8 from glowbit-style layers: W outer, Y, R, P center
# Maps to: drawRectangleFill(0,0,7,7,W); (3,0,4,7),(0,3,7,4),(1,1,6,6)=Y; (3,1,4,6),(1,3,6,4),(2,2,5,5)=R; (3,2,4,5),(2,3,5,4),(3,3,4,4)=P
chakana_matrix = [
    ['W', 'W', 'W', 'Y', 'Y', 'W', 'W', 'W'],
    ['W', 'Y', 'Y', 'Y', 'Y', 'Y', 'Y', 'W'],
    ['W', 'Y', 'Y', 'R', 'R', 'Y', 'Y', 'W'],
    ['Y', 'Y', 'R', 'P', 'P', 'R', 'Y', 'Y'],
    ['Y', 'Y', 'R', 'P', 'P', 'R', 'Y', 'Y'],
    ['W', 'Y', 'Y', 'R', 'R', 'Y', 'Y', 'W'],
    ['W', 'Y', 'Y', 'Y', 'Y', 'Y', 'Y', 'W'],
    ['W', 'W', 'W', 'Y', 'Y', 'W', 'W', 'W'],
]

# Color mapping
color_map = {
    'Y': 'yellow',
    'B': 'black',
    'R': 'red',
    'G': 'green',
    'W': 'white',
    'O': 'orange',
    'P': 'purple',
    'C': 'cyan',
    'M': 'magenta',
    'L': (0, 127, 0),  # Light green
    ' ': (0, 0, 0),
}

# === Helper Functions ===
def draw_pixel(draw, x, y, color, scale):
    x0 = x
    y0 = y
    x1 = x + scale
    y1 = y + scale
    draw.rectangle((x0, y0, x1, y1), fill=color)

def draw_emoji(draw, matrix, color_map, scale, top_left_x, top_left_y, show_selection=False):
    for row in range(len(matrix)):
        for col in range(len(matrix[row])):
            symbol = matrix[row][col]
            color = color_map.get(symbol, (0, 0, 0))
            x = top_left_x + col * scale
            y = top_left_y + row * scale
            draw_pixel(draw, x, y, color, scale)
    
    if show_selection:
        emoji_width = len(matrix[0]) * scale
        emoji_height = len(matrix) * scale
        border_width = 1
        draw.rectangle(
            (top_left_x - border_width, top_left_y - border_width, 
             top_left_x + emoji_width + border_width + 1, top_left_y + emoji_height + border_width + 1),
            outline="white",
            width=border_width
        )

# Animation definitions for menu 1
fireworks_animation = Animation(
    anim_type="procedural",
    data="fireworks",
    duration=10,
    preview=fireworks_preview_matrix
)

rain_animation = Animation(
    anim_type="procedural",
    data="rain",
    duration=200,
    preview=rain_preview_matrix
)

# === Connection Status Indicator Matrices ===
# These are small 8x8 indicators for BLE connection status in lower left corner

# Connecting indicator (loading circle/spinner)
connecting_matrix = [
    [' ', ' ', ' ', 'C', 'C', ' ', ' ', ' '],
    [' ', ' ', 'C', 'C', 'C', 'C', ' ', ' '],
    [' ', 'C', 'C', ' ', ' ', 'C', 'C', ' '],
    ['C', 'C', ' ', ' ', ' ', ' ', 'C', 'C'],
    ['C', 'C', ' ', ' ', ' ', ' ', 'C', 'C'],
    [' ', 'C', 'C', ' ', ' ', 'C', 'C', ' '],
    [' ', ' ', 'C', 'C', 'C', 'C', ' ', ' '],
    [' ', ' ', ' ', 'C', 'C', ' ', ' ', ' '],
]

# Connected indicator (checkmark)
connected_matrix = [
    [' ', ' ', ' ', ' ', ' ', ' ', ' ', ' '],
    [' ', ' ', ' ', ' ', ' ', 'G', 'G', ' '],
    [' ', ' ', ' ', ' ', 'G', 'G', ' ', ' '],
    [' ', ' ', ' ', 'G', 'G', ' ', ' ', ' '],
    [' ', 'G', 'G', 'G', ' ', ' ', ' ', ' '],
    [' ', 'G', 'G', ' ', ' ', ' ', ' ', ' '],
    [' ', ' ', ' ', ' ', ' ', ' ', ' ', ' '],
    [' ', ' ', ' ', ' ', ' ', ' ', ' ', ' '],
]

# Not connected indicator (X)
not_connected_matrix = [
    [' ', ' ', ' ', ' ', ' ', ' ', ' ', ' '],
    [' ', 'R', 'R', ' ', ' ', 'R', 'R', ' '],
    [' ', ' ', 'R', 'R', 'R', 'R', ' ', ' '],
    [' ', ' ', ' ', 'R', 'R', ' ', ' ', ' '],
    [' ', ' ', ' ', 'R', 'R', ' ', ' ', ' '],
    [' ', ' ', 'R', 'R', 'R', 'R', ' ', ' '],
    [' ', 'R', 'R', ' ', ' ', 'R', 'R', ' '],
    [' ', ' ', ' ', ' ', ' ', ' ', ' ', ' '],
]