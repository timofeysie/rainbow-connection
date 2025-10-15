# -*- coding:utf-8 -*-
# Animation classes and procedural animation functions for emoji-os-zero.py

import random
import time
from PIL import Image, ImageDraw

class Animation:
    """Base animation class to define animation properties"""
    def __init__(self, anim_type, data=None, duration=100, preview=None):
        self.type = anim_type  # "static", "two_frame", or "procedural"
        self.data = data  # Matrix data or animation function
        self.duration = duration  # Iterations for procedural animations
        self.preview = preview  # 8x8 preview matrix for menu display

class Raindrop:
    """Raindrop object for rain animation"""
    def __init__(self, x, speed):
        self.x = x
        self.speed = speed
        self.y = 0  # Internal position * 10 for sub-pixel precision
    
    def update(self):
        """Update raindrop position and return (x, y) coordinates"""
        self.y += self.speed
        return (self.x, self.y // 10)
    
    def get_y(self):
        """Get current y position"""
        return self.y // 10

def draw_circle_on_grid(grid, cx, cy, r, color):
    """
    Draw a circle on an 8x8 grid using Bresenham's circle algorithm
    grid: 8x8 list of lists with RGB tuples
    cx, cy: center coordinates
    r: radius
    color: RGB tuple
    """
    if r < 0:
        return
    
    def set_pixel(x, y):
        if 0 <= x < 8 and 0 <= y < 8:
            grid[y][x] = color
    
    f = 1 - r
    ddf_x = 1
    ddf_y = -2 * r
    x = 0
    y = r
    
    set_pixel(cx, cy + r)
    set_pixel(cx, cy - r)
    set_pixel(cx + r, cy)
    set_pixel(cx - r, cy)
    
    while x < y:
        if f >= 0:
            y -= 1
            ddf_y += 2
            f += ddf_y
        x += 1
        ddf_x += 2
        f += ddf_x
        
        set_pixel(cx + x, cy + y)
        set_pixel(cx - x, cy + y)
        set_pixel(cx + x, cy - y)
        set_pixel(cx - x, cy - y)
        set_pixel(cx + y, cy + x)
        set_pixel(cx - y, cy + x)
        set_pixel(cx + y, cy - x)
        set_pixel(cx - y, cy - x)

def glowbit_color_to_rgb(color):
    """Convert GlowBit 0xRRGGBB format to RGB tuple"""
    r = (color >> 16) & 0xFF
    g = (color >> 8) & 0xFF
    b = color & 0xFF
    return (r, g, b)

def create_blank_grid():
    """Create a blank 8x8 grid with black pixels"""
    return [[(0, 0, 0) for _ in range(8)] for _ in range(8)]

def render_grid_to_image(draw, grid, scale, start_x, start_y):
    """
    Render an 8x8 grid to a PIL Image at the specified location and scale
    draw: PIL ImageDraw object
    grid: 8x8 list of lists with RGB tuples
    scale: scale factor (7 for main display, 1.5 for menu)
    start_x, start_y: top-left corner to start drawing
    """
    for row in range(8):
        for col in range(8):
            color = grid[row][col]
            x = start_x + col * scale
            y = start_y + row * scale
            draw.rectangle((x, y, x + scale, y + scale), fill=color)

def fireworks_animation(draw, image, disp, scale, start_x, start_y, iters=10, interruption_check=None):
    """
    Fireworks animation adapted from GlowBit library (lines 811-825)
    Draws expanding/contracting circles at random positions with random colors
    
    draw: PIL ImageDraw object
    disp: Display object for LCD_ShowImage
    scale: scale factor for rendering
    start_x, start_y: position to draw
    iters: number of fireworks to display
    interruption_check: callable that returns True if animation should stop
    """
    while iters > 0:
        # Check for interruption
        if interruption_check and interruption_check():
            return True  # Animation was interrupted
        
        # Create blank grid
        grid = create_blank_grid()
        
        # Random color and position for this firework
        color_int = random.randint(0, 0xFFFFFF)
        color = glowbit_color_to_rgb(color_int)
        cx = random.randint(0, 7)
        cy = random.randint(0, 7)
        
        # Expanding circles
        for r in range(4):  # 8x8 grid max radius is 4
            if interruption_check and interruption_check():
                return True
            
            grid = create_blank_grid()
            draw_circle_on_grid(grid, cx, cy, r, color)
            
            # Render to display
            draw.rectangle((start_x, start_y, start_x + scale * 8, start_y + scale * 8), fill=(0, 0, 0))
            render_grid_to_image(draw, grid, scale, start_x, start_y)
            disp.LCD_ShowImage(image, 0, 0)
            time.sleep(0.05)
        
        # Contracting circles (fade out)
        for r in range(4):
            if interruption_check and interruption_check():
                return True
            
            grid = create_blank_grid()
            draw_circle_on_grid(grid, cx, cy, r, (0, 0, 0))
            
            # Render to display
            draw.rectangle((start_x, start_y, start_x + scale * 8, start_y + scale * 8), fill=(0, 0, 0))
            render_grid_to_image(draw, grid, scale, start_x, start_y)
            disp.LCD_ShowImage(image, 0, 0)
            time.sleep(0.05)
        
        iters -= 1
    
    return False  # Animation completed normally

def rain_animation(draw, image, disp, scale, start_x, start_y, iters=200, density=1, interruption_check=None):
    """
    Rain animation adapted from GlowBit library (lines 876-913)
    Digital rain effect with falling green droplets
    
    draw: PIL ImageDraw object
    disp: Display object for LCD_ShowImage
    scale: scale factor for rendering
    start_x, start_y: position to draw
    iters: number of frames to animate
    density: raindrop density (drops per 4x4 square)
    interruption_check: callable that returns True if animation should stop
    """
    drops = []
    
    # Color gradient for raindrops (bright to dark green)
    c1 = (200, 255, 200)
    c2 = (0, 127, 0)
    c3 = (0, 64, 0)
    c4 = (0, 32, 0)
    c5 = (0, 16, 0)
    
    # Start with one drop
    p = random.randint(0, 7)
    drops.append(Raindrop(p, random.randint(2, 8)))
    
    while len(drops) > 0 or iters > 0:
        # Check for interruption
        if interruption_check and interruption_check():
            return True  # Animation was interrupted
        
        # Add new drops if needed
        while len(drops) / density < 64 / 16 and iters > 0:
            p = random.randint(0, 7)
            drops.append(Raindrop(p, random.randint(2, 8)))
            iters -= 1
        
        # Create blank grid
        grid = create_blank_grid()
        
        # Update and draw all drops
        for drop in drops:
            (x, y) = drop.update()
            
            # Draw drop with gradient trail
            def set_drop_pixel(x, y, color):
                if 0 <= x < 8 and 0 <= y < 8:
                    grid[y][x] = color
            
            set_drop_pixel(x, y, c1)
            set_drop_pixel(x, y - 1, c2)
            set_drop_pixel(x, y - 2, c3)
            set_drop_pixel(x, y - 3, c4)
            set_drop_pixel(x, y - 4, c5)
            set_drop_pixel(x, y - 5, (0, 0, 0))
            set_drop_pixel(x, y - 6, (0, 0, 0))
            set_drop_pixel(x, y - 7, (0, 0, 0))
        
        # Remove drops that have fallen off screen
        drops = [drop for drop in drops if drop.get_y() <= 8 + 6]
        
        # Render to display
        draw.rectangle((start_x, start_y, start_x + scale * 8, start_y + scale * 8), fill=(0, 0, 0))
        render_grid_to_image(draw, grid, scale, start_x, start_y)
        disp.LCD_ShowImage(draw._image, 0, 0)
        time.sleep(0.05)
    
    return False  # Animation completed normally

# Preview matrices for menu display (8x8 static representations)

# Fireworks preview - starburst pattern with multiple colors
fireworks_preview_matrix = [
    [' ', ' ', ' ', 'Y', 'Y', ' ', ' ', ' '],
    [' ', 'O', ' ', 'Y', 'Y', ' ', 'R', ' '],
    [' ', ' ', 'W', 'W', 'W', 'P', ' ', ' '],
    ['M', 'W', 'W', ' ', ' ', 'W', 'W', 'B'],
    ['M', 'W', 'W', ' ', ' ', 'W', 'W', 'B'],
    [' ', ' ', 'C', 'W', 'W', 'C', ' ', ' '],
    [' ', 'G', ' ', 'W', 'W', ' ', 'O', ' '],
    [' ', ' ', ' ', 'W', 'W', ' ', ' ', ' '],
]

# Rain preview - vertical green streaks
rain_preview_matrix = [
    [' ', 'W', ' ', ' ', ' ', 'W', ' ', ' '],
    [' ', 'L', ' ', 'W', ' ', 'G', ' ', 'W'],
    [' ', 'G', ' ', 'L', ' ', ' ', ' ', 'L'],
    [' ', ' ', ' ', 'G', ' ', 'W', ' ', 'G'],
    ['W', ' ', 'W', ' ', ' ', 'L', ' ', ' '],
    ['L', ' ', 'L', 'W', ' ', 'G', ' ', 'W'],
    ['G', ' ', 'G', 'L', ' ', ' ', ' ', 'L'],
    [' ', ' ', ' ', 'G', ' ', 'W', ' ', 'G'],
]

# Color map for preview matrices (extending existing color_map)
animation_color_map = {
    'Y': 'yellow',
    'B': 'blue',
    'R': 'red',
    'G': 'green',
    'W': 'white',
    'O': 'orange',
    'P': 'purple',
    'C': 'cyan',
    'M': 'magenta',
    'L': (0, 127, 0),  # Light green for rain
    ' ': (0, 0, 0),
}

