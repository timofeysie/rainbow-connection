# -*- coding:utf-8 -*-
from PIL import Image, ImageDraw, ImageFont
import tkinter as tk
from tkinter import ttk

# === Display dimensions (same as Waveshare 1.44inch LCD) ===
DISPLAY_WIDTH = 128
DISPLAY_HEIGHT = 128

# === Create blank canvas ===
image = Image.new('RGB', (DISPLAY_WIDTH, DISPLAY_HEIGHT), color=(0, 0, 0))
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
    ' ': (0, 0, 0),  # background
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
    # Use textbbox instead of textsize for newer PIL versions
    try:
        bbox = draw.textbbox((0, 0), text, font=font)
        text_width = bbox[2] - bbox[0]
        text_height = bbox[3] - bbox[1]
    except AttributeError:
        # Fallback for older PIL versions
        text_width, text_height = draw.textsize(text, font=font)
    
    x_position = (max_width - text_width) // 2  # center the text
    draw.text((x_position, y_position), text, font=font, fill="white")

# === Load a font ===
try:
    font = ImageFont.load_default()
except:
    # Fallback if default font fails
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
x_pos = 110
draw_emoji(draw, smiley_matrix, color_map, 1.5, x_pos, 1)
draw_emoji(draw, smiley_matrix, color_map, 1.5, x_pos, 16)
draw_emoji(draw, smiley_matrix, color_map, 1.5, x_pos, 31)
draw_emoji(draw, smiley_matrix, color_map, 1.5, x_pos, 46)

# === Menu Texts ===
menu_items = ["Emojis", "Animations", "Characters", "Other"]

# Draw text for each row of emojis (left side and right side)
text_y_positions = [5, 20, 35, 50]  # Y positions for the text, corresponding to emoji rows

# Draw text for left side menu
for i, item in enumerate(menu_items):
    draw_centered_text(draw, item, text_y_positions[i], font, DISPLAY_WIDTH)

# Draw text for right side menu
for i, item in enumerate(menu_items):
    draw_centered_text(draw, item, text_y_positions[i], font, DISPLAY_WIDTH)

# === Display simulation ===
def show_simulation():
    # Create a scaled version for better visibility on laptop
    scale_factor = 4
    scaled_image = image.resize((DISPLAY_WIDTH * scale_factor, DISPLAY_HEIGHT * scale_factor), Image.NEAREST)
    
    # Create Tkinter window
    root = tk.Tk()
    root.title("Waveshare 1.44inch LCD Simulator")
    
    # Convert PIL image to PhotoImage
    from PIL import ImageTk
    photo = ImageTk.PhotoImage(scaled_image)
    
    # Create label to display image
    label = tk.Label(root, image=photo)
    label.pack()
    
    # Add info text
    info_label = tk.Label(root, text=f"Simulated {DISPLAY_WIDTH}x{DISPLAY_HEIGHT} LCD Display (scaled {scale_factor}x)")
    info_label.pack()
    
    # Add close button
    close_button = tk.Button(root, text="Close", command=root.destroy)
    close_button.pack()
    
    root.mainloop()

if __name__ == "__main__":
    print("Starting LCD Simulator...")
    print(f"Display dimensions: {DISPLAY_WIDTH}x{DISPLAY_HEIGHT}")
    print("Showing simulated LCD output...")
    show_simulation()