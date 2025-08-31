# -*- coding:utf-8 -*-
from PIL import Image, ImageDraw, ImageFont
import tkinter as tk
from tkinter import ttk

# === Display dimensions (same as Waveshare 1.44inch LCD) ===
DISPLAY_WIDTH = 128
DISPLAY_HEIGHT = 128

# === Menu layout margins ===
LEFT_EMOJI_RIGHT_MARGIN = 25    # Right edge of left emoji column
RIGHT_EMOJI_LEFT_MARGIN = 105   # Left edge of right emoji column

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
        # It's the space between the left emoji column and right emoji column
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
# Top-left emoji with selection border (demo purposes)
draw_emoji(draw, smiley_matrix, color_map, 1.5, 5, 1, show_selection=True)
# Other left side emojis without selection
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
text_y_positions = [1, 16, 31, 46]  # Y positions for the text, at the top of each row

# Draw text for left side menu with selection styling
for i, item in enumerate(menu_items):
    # First item ("Emojis") is selected by default
    is_selected = (i == 0)
    draw_menu_row(draw, item, text_y_positions[i], font, is_selected)

# Draw text for right side menu (same selection state)
for i, item in enumerate(menu_items):
    is_selected = (i == 0)
    draw_menu_row(draw, item, text_y_positions[i], font, is_selected)

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
    
    # Add selection info
    selection_label = tk.Label(root, text="First menu item 'Emojis' is selected (white background, black text)")
    selection_label.pack()
    
    # Add close button
    close_button = tk.Button(root, text="Close", command=root.destroy)
    close_button.pack()
    
    root.mainloop()

if __name__ == "__main__":
    print("Starting LCD Simulator...")
    print(f"Display dimensions: {DISPLAY_WIDTH}x{DISPLAY_HEIGHT}")
    print("Showing simulated LCD output with menu selection...")
    show_simulation()