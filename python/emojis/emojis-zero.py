# emojis-zero.py for emoji os zero v0.1.0
# Adapted for Raspberry Pi Zero 2 W with Waveshare 1.44inch LCD HAT
import time
from PIL import Image, ImageDraw

# Global variables for display context
# These will be set by the main emoji-os-zero.py file
disp = None
image = None
draw = None

def set_display_context(display, img, draw_obj):
    """Set the display context for drawing functions"""
    global disp, image, draw
    disp = display
    image = img
    draw = draw_obj

def clear_display():
    """Clear the display and draw a black background"""
    if draw:
        draw.rectangle((0, 0, 128, 128), outline=0, fill=0)

def draw_8x8_pattern(pattern, scale=8, offset_x=32, offset_y=32):
    """Draw an 8x8 pattern scaled up on the 128x128 display"""
    if not draw:
        return
        
    for row in range(8):
        for col in range(8):
            if pattern[row][col] != 0:
                # Scale up the 8x8 pattern to fit nicely on the 128x128 display
                x1 = offset_x + col * scale
                y1 = offset_y + row * scale
                x2 = x1 + scale
                y2 = y1 + scale
                
                if isinstance(pattern[row][col], int):
                    # Simple color value
                    color = pattern[row][col]
                else:
                    # RGB tuple
                    color = pattern[row][col]
                
                draw.rectangle((x1, y1, x2, y2), outline=color, fill=color)

def scroll_large_image():
    """Placeholder for scroll_large_image function - removed as requested"""
    print("scroll_large_image function removed as requested")
    # Draw a simple placeholder pattern
    if draw:
        draw.rectangle((20, 20, 108, 108), outline=255, fill=0)
        draw.ellipse((40, 40, 88, 88), outline=0x00ff00, fill=0)
        draw.ellipse((50, 50, 78, 78), outline=0xff0000, fill=0)
        if disp:
            disp.LCD_ShowImage(image, 0, 0)

def chakana():
    """Draw a chakana (Inca cross) pattern"""
    if not draw:
        return
        
    speed = 0.2
    clear_display()
    
    # Center square
    draw.rectangle((60, 60, 68, 68), outline=255, fill=255)
    if disp:
        disp.LCD_ShowImage(image, 0, 0)
    time.sleep(speed)

    # Vertical and horizontal lines
    draw.rectangle((60, 56, 68, 72), outline=255, fill=255)  # Vertical
    draw.rectangle((56, 60, 72, 68), outline=255, fill=255)  # Horizontal
    draw.rectangle((60, 60, 68, 68), outline=0xffff00, fill=0xffff00)  # Center yellow
    if disp:
        disp.LCD_ShowImage(image, 0, 0)
    time.sleep(speed)

    # Expand pattern
    draw.rectangle((60, 52, 68, 76), outline=255, fill=255)  # Vertical
    draw.rectangle((52, 60, 76, 68), outline=255, fill=255)  # Horizontal
    draw.rectangle((56, 56, 72, 72), outline=255, fill=255)  # Center square
    draw.rectangle((60, 56, 68, 72), outline=0xffff00, fill=0xffff00)  # Vertical yellow
    draw.rectangle((56, 60, 72, 68), outline=0xffff00, fill=0xffff00)  # Horizontal yellow
    draw.rectangle((60, 60, 68, 68), outline=0xff0000, fill=0xff0000)  # Center red
    if disp:
        disp.LCD_ShowImage(image, 0, 0)
    time.sleep(speed)

    # Final pattern
    draw.rectangle((60, 48, 68, 80), outline=255, fill=255)  # Vertical
    draw.rectangle((48, 60, 80, 68), outline=255, fill=255)  # Horizontal
    draw.rectangle((52, 52, 76, 76), outline=255, fill=255)  # Center square
    draw.rectangle((60, 48, 68, 80), outline=0xffff00, fill=0xffff00)  # Vertical yellow
    draw.rectangle((48, 60, 80, 68), outline=0xffff00, fill=0xffff00)  # Horizontal yellow
    draw.rectangle((56, 56, 72, 72), outline=0xffff00, fill=0xffff00)  # Center yellow
    draw.rectangle((60, 56, 68, 72), outline=0xff0000, fill=0xff0000)  # Vertical red
    draw.rectangle((56, 60, 72, 68), outline=0xff0000, fill=0xff0000)  # Horizontal red
    draw.rectangle((60, 60, 68, 68), outline=0x8000ff, fill=0x8000ff)  # Center purple
    if disp:
        disp.LCD_ShowImage(image, 0, 0)
    time.sleep(speed)

    # Full pattern
    draw.rectangle((48, 48, 80, 80), outline=255, fill=255)  # Center square
    draw.rectangle((60, 48, 68, 80), outline=0xffff00, fill=0xffff00)  # Vertical yellow
    draw.rectangle((48, 60, 80, 68), outline=0xffff00, fill=0xffff00)  # Horizontal yellow
    draw.rectangle((52, 52, 76, 76), outline=0xffff00, fill=0xffff00)  # Center yellow
    draw.rectangle((60, 56, 68, 72), outline=0xff0000, fill=0xff0000)  # Vertical red
    draw.rectangle((56, 60, 72, 68), outline=0xff0000, fill=0xff0000)  # Horizontal red
    draw.rectangle((56, 56, 72, 72), outline=0xff0000, fill=0xff0000)  # Center red
    draw.rectangle((60, 56, 68, 72), outline=0x8000ff, fill=0x8000ff)  # Vertical purple
    draw.rectangle((56, 60, 72, 68), outline=0x8000ff, fill=0x8000ff)  # Horizontal purple
    draw.rectangle((60, 60, 68, 68), outline=0x8000ff, fill=0x8000ff)  # Center purple
    if disp:
        disp.LCD_ShowImage(image, 0, 0)

def regular():
    """Draw a regular smiley face"""
    print("regular")
    if not draw:
        return
        
    clear_display()
    T = [[0, 0, 1, 1, 1, 1, 0, 0],
         [0, 1, 0, 0, 0, 0, 1, 0],
         [1, 0, 1, 0, 0, 1, 0, 1],
         [1, 0, 0, 0, 0, 0, 0, 1],
         [1, 0, 1, 1, 1, 1, 0, 1],
         [1, 0, 0, 0, 0, 0, 0, 1],
         [0, 1, 0, 0, 0, 0, 1, 0],
         [0, 0, 1, 1, 1, 1, 0, 0]]
    
    # Convert pattern to use white (255) instead of 1
    pattern = [[255 if cell == 1 else 0 for cell in row] for row in T]
    draw_8x8_pattern(pattern)
    
    if disp:
        disp.LCD_ShowImage(image, 0, 0)

def sad():
    """Draw a sad face"""
    print("sad")
    if not draw:
        return
        
    clear_display()
    T = [[0, 0, 1, 1, 1, 1, 0, 0],
         [0, 1, 0, 0, 0, 0, 1, 0],
         [1, 0, 1, 0, 0, 1, 0, 1],
         [1, 0, 0, 0, 0, 0, 0, 1],
         [1, 0, 0, 1, 1, 0, 0, 1],
         [1, 0, 1, 0, 0, 1, 0, 1],
         [0, 1, 0, 0, 0, 0, 1, 0],
         [0, 0, 1, 1, 1, 1, 0, 0]]
    
    pattern = [[255 if cell == 1 else 0 for cell in row] for row in T]
    draw_8x8_pattern(pattern)
    
    if disp:
        disp.LCD_ShowImage(image, 0, 0)

def happy():
    """Draw a happy face"""
    if not draw:
        return
        
    clear_display()
    T = [[0, 0, 1, 1, 1, 1, 0, 0],
         [0, 1, 0, 0, 0, 0, 1, 0],
         [1, 0, 1, 0, 0, 1, 0, 1],
         [1, 0, 0, 0, 0, 0, 0, 1],
         [1, 0, 1, 0, 0, 1, 0, 1],
         [1, 0, 0, 1, 1, 0, 0, 1],
         [0, 1, 0, 0, 0, 0, 1, 0],
         [0, 0, 1, 1, 1, 1, 0, 0]]
    
    pattern = [[255 if cell == 1 else 0 for cell in row] for row in T]
    draw_8x8_pattern(pattern)
    
    if disp:
        disp.LCD_ShowImage(image, 0, 0)

def thickLips():
    """Draw a face with thick lips"""
    if not draw:
        return
        
    clear_display()
    T = [[0, 0, 1, 1, 1, 1, 0, 0],
         [0, 1, 0, 0, 0, 0, 1, 0],
         [1, 0, 1, 0, 0, 1, 0, 1],
         [1, 0, 0, 0, 0, 0, 0, 1],
         [1, 0, 1, 1, 1, 1, 0, 1],
         [1, 0, 1, 1, 1, 1, 0, 1],
         [0, 1, 0, 0, 0, 0, 1, 0],
         [0, 0, 1, 1, 1, 1, 0, 0]]
    
    pattern = [[255 if cell == 1 else 0 for cell in row] for row in T]
    draw_8x8_pattern(pattern)
    
    if disp:
        disp.LCD_ShowImage(image, 0, 0)

def wry():
    """Draw a wry face"""
    print("wry")
    if not draw:
        return
        
    clear_display()
    T = [[0, 0, 1, 1, 1, 1, 0, 0],
         [0, 1, 0, 0, 0, 0, 1, 0],
         [1, 0, 1, 0, 1, 0, 0, 1],
         [1, 0, 1, 0, 1, 0, 0, 1],
         [1, 0, 0, 0, 0, 1, 0, 1],
         [1, 0, 1, 1, 1, 0, 0, 1],
         [0, 1, 0, 0, 0, 0, 1, 0],
         [0, 0, 1, 1, 1, 1, 0, 0]]
    
    pattern = [[255 if cell == 1 else 0 for cell in row] for row in T]
    draw_8x8_pattern(pattern)
    
    if disp:
        disp.LCD_ShowImage(image, 0, 0)

def heartBounce():
    """Draw a bouncing heart animation"""
    print("heart bounce")
    if not draw:
        return
        
    clear_display()
    T = [[0, 1, 1, 0, 0, 1, 1, 0],
         [1, 1, 1, 1, 1, 1, 1, 1],
         [1, 1, 1, 1, 1, 1, 1, 1],
         [1, 1, 1, 1, 1, 1, 1, 1],
         [0, 1, 1, 1, 1, 1, 1, 0],
         [0, 0, 1, 1, 1, 1, 0, 0],
         [0, 0, 0, 1, 1, 0, 0, 0],
         [0, 0, 0, 0, 0, 0, 0, 0]]
    
    pattern = [[0xff0000 if cell == 1 else 0 for cell in row] for row in T]
    draw_8x8_pattern(pattern)
    
    if disp:
        disp.LCD_ShowImage(image, 0, 0)
    time.sleep(1)
    
    # Second frame
    T2 = [[0, 0, 0, 0, 0, 0, 0, 0],
           [0, 1, 1, 0, 0, 1, 1, 0],
           [1, 1, 1, 1, 1, 1, 1, 1],
           [1, 1, 1, 1, 1, 1, 1, 1],
           [1, 1, 1, 1, 1, 1, 1, 1],
           [0, 1, 1, 1, 1, 1, 1, 0],
           [0, 0, 1, 1, 1, 1, 0, 0],
           [0, 0, 0, 1, 1, 0, 0, 0]]
    
    clear_display()
    pattern2 = [[0xff0000 if cell == 1 else 0 for cell in row] for row in T2]
    draw_8x8_pattern(pattern2)
    
    if disp:
        disp.LCD_ShowImage(image, 0, 0)
    time.sleep(1)
    
    # Third frame (back to first)
    clear_display()
    draw_8x8_pattern(pattern)
    
    if disp:
        disp.LCD_ShowImage(image, 0, 0)

def finn():
    """Draw Finn the Human character"""
    print("finn the human")
    if not draw:
        return
        
    clear_display()
    T = [[0x40c4fe, 0x40c4fe, 0xffffff, 0x40c4fe, 0x40c4fe, 0x40c4fe, 0xffffff, 0x40c4fe],
         [0x40c4fe, 0x40c4fe, 0xffffff, 0xffffff, 0xffffff, 0xffffff, 0xffffff, 0x40c4fe],
         [0x40c4fe, 0x40c4fe, 0xffffff, 0x000000, 0xfadc64, 0xfadc64, 0x000000, 0x40c4fe],
         [0x86bc46, 0x79ad41, 0xffffff, 0xfadc64, 0xfadc64, 0xfadc64, 0xfadc64, 0x40c4fe],
         [0x18581c, 0xa4c77a, 0x79c5e9, 0x1f8ce2, 0x1f8ce2, 0x1f8ce2, 0x1f8ce2, 0x40c4fe],
         [0xfadc64, 0x18581c, 0x1f8ce2, 0x1f8ce2, 0x1f8ce2, 0x1f8ce2, 0x1f8ce2, 0xfadc64],
         [0x64d802, 0x64d802, 0x0b3d8a, 0x0b3d8a, 0x0b3d8a, 0x0b3d8a, 0x0b3d8a, 0x64d802],
         [0x64d802, 0x64d802, 0xfadc64, 0x64d802, 0x64d802, 0x64d802, 0xfadc64, 0x64d802]]
    
    draw_8x8_pattern(T)
    
    if disp:
        disp.LCD_ShowImage(image, 0, 0)
    time.sleep(0.5)

def angry():
    """Draw an angry face"""
    print("angry")
    if not draw:
        return
        
    clear_display()
    T = [[0xff0000, 0x000000, 0xff0000, 0xff0000, 0xff0000, 0xff0000, 0x000000, 0xff0000],
         [0xff0000, 0xff0000, 0x000000, 0xff0000, 0xff0000, 0x000000, 0xff0000, 0xff0000],
         [0xff0000, 0x40c4fe, 0xffffff, 0x000000, 0x000000, 0x40c4fd, 0xffffff, 0xff0000],
         [0xff0000, 0xff0000, 0xff0000, 0xff0000, 0xff0000, 0xff0000, 0xff0000, 0xff0000],
         [0xff0000, 0xff0000, 0xff0000, 0xff0000, 0xff0000, 0xff0000, 0xff0000, 0xff0000],
         [0xff0000, 0xff0000, 0x000000, 0x000000, 0x000000, 0x000000, 0xff0000, 0xff0000],
         [0xff0000, 0x000000, 0xff0000, 0xff0000, 0xff0000, 0xff0000, 0x000000, 0xff0000],
         [0xff0000, 0xff0000, 0xff0000, 0xff0000, 0xff0000, 0xff0000, 0xff0000, 0xff0000]]
    
    draw_8x8_pattern(T)
    
    if disp:
        disp.LCD_ShowImage(image, 0, 0)

def greenMonster():
    """Draw a green monster face"""
    print("green monster")
    if not draw:
        return
        
    clear_display()
    T = [[0x000000, 0x00ff00, 0x00ff00, 0x00ff00, 0x00ff00, 0x00ff00, 0x00ff00, 0x000000],
         [0x00ff00, 0x00ff00, 0x00ff00, 0x00ff00, 0x00ff00, 0x00ff00, 0x00ff00, 0x00ff00],
         [0x00ff00, 0xff0000, 0x00ff00, 0x00ff00, 0xff0000, 0x00ff00, 0x00ff00, 0x00ff00],
         [0x00ff00, 0x00ff00, 0x00ff00, 0x00ff00, 0x00ff00, 0x00ff00, 0x00ff00, 0x00ff00],
         [0x00ff00, 0x00ff00, 0xffffff, 0x000000, 0xffffff, 0x000000, 0xffffff, 0x00ff00],
         [0x00ff00, 0x000000, 0x000000, 0x000000, 0x000000, 0x000000, 0x000000, 0x00ff00],
         [0x00ff00, 0xffffff, 0x000000, 0xffffff, 0x000000, 0xffffff, 0x000000, 0x00ff00],
         [0x00ff00, 0x00ff00, 0x00ff00, 0x00ff00, 0x00ff00, 0x00ff00, 0x00ff00, 0x00ff00]]
    
    draw_8x8_pattern(T)
    
    if disp:
        disp.LCD_ShowImage(image, 0, 0)

def pikachu():
    """Draw Pikachu character"""
    print("pikachu")
    if not draw:
        return
        
    clear_display()
    T = [[0xffffff, 0x424242, 0x424242, 0xffffff, 0xffffff, 0xffffff, 0xffffff, 0x404242],
         [0xffffff, 0xffffff, 0xffec3c, 0xff9800, 0xffffff, 0xffffff, 0xffffff, 0xff9800],
         [0xffffff, 0xffffff, 0xffffff, 0xffec3c, 0xffec3c, 0xfadc64, 0xffec3c, 0xff9800],
         [0xff9800, 0xff9800, 0xffffff, 0xfadc64, 0x000000, 0xfadc64, 0xfadc64, 0x000000],
         [0xff9800, 0xff9800, 0xffffff, 0xea1e04, 0xfef100, 0xfef100, 0xfef100, 0xff9800],
         [0xffffff, 0xa25900, 0xffffff, 0xfef100, 0xe68900, 0xfef100, 0xff9800, 0xffffff],
         [0xffffff, 0xb06100, 0xfaee00, 0xff9800, 0xfbee00, 0xa25900, 0xfbee00, 0xffffff],
         [0xffffff, 0xffffff, 0xfaee00, 0xd27b00, 0xa25900, 0xb16200, 0xb16200, 0xffffff]]
    
    draw_8x8_pattern(T)
    
    if disp:
        disp.LCD_ShowImage(image, 0, 0)

def crab():
    """Draw a crab character"""
    print("crab")
    if not draw:
        return
        
    clear_display()
    T = [[0x000000, 0xffffff, 0xffffff, 0x000000, 0xffffff, 0xffffff, 0x000000, 0x000000],
         [0x000000, 0xffffff, 0x0000ff, 0x000000, 0xffffff, 0x0000ff, 0x000000, 0x000000],
         [0x000000, 0xff0000, 0x000000, 0x000000, 0xff0000, 0x000000, 0x000000, 0x000000],
         [0x000000, 0xff0000, 0x000000, 0x000000, 0xff0000, 0x000000, 0x000000, 0x000000],
         [0xff0000, 0xff0000, 0xff0000, 0xff0000, 0xff0000, 0x000000, 0xff0000, 0xff0000],
         [0xff0000, 0xff0000, 0x000000, 0x000000, 0xff0000, 0xff0000, 0xff0000, 0x000000],
         [0xff0000, 0xff0000, 0xff0000, 0xff0000, 0xff0000, 0x000000, 0x000000, 0xff0000],
         [0xff0000, 0x000000, 0xff0000, 0x000000, 0xff0000, 0x000000, 0x000000, 0x000000]]
    
    draw_8x8_pattern(T)
    
    if disp:
        disp.LCD_ShowImage(image, 0, 0)

def frog():
    """Draw a frog character"""
    print("frog")
    if not draw:
        return
        
    clear_display()
    T = [[0x000000, 0x00ff00, 0x00ff00, 0x00ff00, 0x00ff00, 0x00ff00, 0x00ff00, 0x00ff00],
         [0x000000, 0x00ff00, 0x000000, 0x00ff00, 0x00ff00, 0x00ff00, 0x000000, 0x00ff00],
         [0x00ff00, 0x00ff00, 0x00ff00, 0x00ff00, 0x00ff00, 0x00ff00, 0x00ff00, 0x00ff00],
         [0x00ff00, 0x000000, 0x000000, 0x000000, 0x000000, 0x000000, 0x000000, 0x000000],
         [0x00ff00, 0x00ff00, 0x00ff00, 0x00ff00, 0x00ff00, 0x00ff00, 0x00ff00, 0x00ff00],
         [0x00ff00, 0x00ff00, 0x00ff00, 0x00ff00, 0x00ff00, 0x00ff00, 0x00ff00, 0x00ff00],
         [0x00ff00, 0x00ff00, 0x00ff00, 0x00ff00, 0x00ff00, 0x00ff00, 0x00ff00, 0x00ff00],
         [0x00ff00, 0x00ff00, 0x000000, 0x00ff00, 0x00ff00, 0x00ff00, 0x000000, 0x00ff00]]
    
    draw_8x8_pattern(T)
    
    if disp:
        disp.LCD_ShowImage(image, 0, 0)

def bald():
    """Draw a bald character"""
    print("bald")
    if not draw:
        return
        
    clear_display()
    T = [[0x000000, 0x443b31, 0x443b31, 0x443b31, 0x443b31, 0x443b31, 0x443b31, 0x000000],
         [0x443b31, 0x443b31, 0x443b31, 0x443b31, 0x443b31, 0x443b31, 0x443b31, 0x443b31],
         [0x443b31, 0x443b31, 0x443b31, 0x443b31, 0x443b31, 0x443b31, 0x443b31, 0x443b31],
         [0x443b31, 0x443b31, 0x443b31, 0x443b31, 0x443b31, 0x443b31, 0x443b31, 0x443b31],
         [0x443b31, 0x443b31, 0x443b31, 0x443b31, 0x443b31, 0x443b31, 0x443b31, 0x443b31],
         [0x646464, 0x443b31, 0x443b31, 0x443b31, 0x646464, 0x443b31, 0x443b31, 0x443b31],
         [0x443b31, 0x443b31, 0x443b31, 0x443b31, 0x443b31, 0x443b31, 0x443b31, 0x443b31],
         [0x443b31, 0x000000, 0x000000, 0x000000, 0x443b31, 0x443b31, 0x443b31, 0x000000]]
    
    draw_8x8_pattern(T)
    
    if disp:
        disp.LCD_ShowImage(image, 0, 0)

def surprise():
    """Draw a surprised face"""
    print("surprise")
    if not draw:
        return
        
    clear_display()
    T = [[0x964600, 0x964600, 0x964600, 0x964600, 0x964600, 0x964600, 0x964600, 0x964600],
         [0x443b31, 0x443b31, 0x443b31, 0x443b31, 0x443b31, 0x443b31, 0x443b31, 0x964600],
         [0x443b31, 0x000000, 0x646464, 0x443b31, 0x000000, 0x646464, 0x443b31, 0x964600],
         [0x443b31, 0x646464, 0x646464, 0x443b31, 0x646464, 0x646464, 0x443b31, 0x964600],
         [0x443b31, 0x443b31, 0x443b31, 0x443b31, 0x443b31, 0x443b31, 0x443b31, 0x443b31],
         [0x443b31, 0x443b31, 0x000000, 0x000000, 0x443b31, 0x443b31, 0x443b31, 0x443b31],
         [0x443b31, 0x443b31, 0x000000, 0x000000, 0x443b31, 0x443b31, 0x443b31, 0x964600],
         [0x000000, 0x443b31, 0x443b31, 0x443b31, 0x443b31, 0x443b31, 0x443b31, 0x000000]]
    
    draw_8x8_pattern(T)
    
    if disp:
        disp.LCD_ShowImage(image, 0, 0)
