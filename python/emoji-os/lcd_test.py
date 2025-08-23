# -*- coding:utf-8 -*-
# lcd_test.py - Simple LCD test to debug display issues
# Tests basic LCD functionality without complex menu logic

import RPi.GPIO as GPIO
import time
from PIL import Image, ImageDraw, ImageFont, ImageColor

# GPIO pin definitions for Waveshare LCD HAT
KEY_UP_PIN     = 6 
KEY_DOWN_PIN   = 19
KEY_LEFT_PIN   = 5
KEY_RIGHT_PIN  = 26
KEY_PRESS_PIN  = 13
KEY1_PIN       = 21
KEY2_PIN       = 20
KEY3_PIN       = 16

# Initialize GPIO FIRST - before any LCD operations
GPIO.setmode(GPIO.BCM) 
GPIO.setup(KEY_UP_PIN,      GPIO.IN, pull_up_down=GPIO.PUD_UP)
GPIO.setup(KEY_DOWN_PIN,    GPIO.IN, pull_up_down=GPIO.PUD_UP)
GPIO.setup(KEY_LEFT_PIN,    GPIO.IN, pull_up_down=GPIO.PUD_UP)
GPIO.setup(KEY_RIGHT_PIN,   GPIO.IN, pull_up_down=GPIO.PUD_UP)
GPIO.setup(KEY_PRESS_PIN,   GPIO.IN, pull_up_down=GPIO.PUD_UP)
GPIO.setup(KEY1_PIN,        GPIO.IN, pull_up_down=GPIO.PUD_UP)
GPIO.setup(KEY2_PIN,        GPIO.IN, pull_up_down=GPIO.PUD_UP)
GPIO.setup(KEY3_PIN,        GPIO.IN, pull_up_down=GPIO.PUD_UP)

print("GPIO initialized successfully")

# Try to import LCD library after GPIO setup
try:
    import LCD_1in44
    import LCD_Config
    
    # Initialize LCD display
    disp = LCD_1in44.LCD()
    Lcd_ScanDir = LCD_1in44.SCAN_DIR_DFT
    disp.LCD_Init(Lcd_ScanDir)
    disp.LCD_Clear()
    LCD_AVAILABLE = True
    print("LCD display initialized successfully")
except Exception as e:
    print(f"LCD display not available: {e}")
    print("Running in terminal-only mode")
    LCD_AVAILABLE = False

if LCD_AVAILABLE:
    # Create blank image for drawing
    width = 128
    height = 128
    image = Image.new('RGB', (width, height))
    draw = ImageDraw.Draw(image)
    
    print("PIL image created successfully")
    
    # Test 1: Clear to black
    print("Test 1: Clearing to black...")
    draw.rectangle((0, 0, width, height), outline=0, fill=0)
    disp.LCD_ShowImage(image, 0, 0)
    print("Black screen displayed")
    time.sleep(2)
    
    # Test 2: Draw white rectangle
    print("Test 2: Drawing white rectangle...")
    draw.rectangle((20, 20, 108, 108), outline=255, fill=255)
    disp.LCD_ShowImage(image, 0, 0)
    print("White rectangle displayed")
    time.sleep(2)
    
    # Test 3: Draw colored shapes
    print("Test 3: Drawing colored shapes...")
    # Clear first
    draw.rectangle((0, 0, width, height), outline=0, fill=0)
    
    # Red circle
    draw.ellipse((20, 20, 60, 60), outline=255, fill=0xff0000)
    
    # Green rectangle
    draw.rectangle((70, 20, 110, 60), outline=255, fill=0x00ff00)
    
    # Blue triangle
    draw.polygon([(20, 80), (60, 80), (40, 120)], outline=255, fill=0x0000ff)
    
    # Yellow text
    draw.text((70, 80), "TEST", fill=0xffff00)
    
    disp.LCD_ShowImage(image, 0, 0)
    print("Colored shapes displayed")
    time.sleep(3)
    
    # Test 4: Menu-like layout
    print("Test 4: Menu layout...")
    # Clear first
    draw.rectangle((0, 0, width, height), outline=0, fill=0)
    
    # Left side - menu
    draw.rectangle((0, 0, 63, 127), outline=255, fill=0)
    draw.text((5, 5), "MENU", fill=255)
    draw.text((5, 25), "0: Emojis", fill=255)
    draw.text((5, 45), "1: Animations", fill=255)
    draw.text((5, 65), "2: Characters", fill=255)
    draw.text((5, 85), "3: Symbols", fill=255)
    
    # Right side - emoji
    draw.rectangle((64, 0, 127, 127), outline=255, fill=0)
    
    # Simple 8x8 smiley face (scaled)
    # Each pixel becomes 6x6 pixels
    scale = 6
    x_offset = 64 + 16  # Center on right side
    y_offset = 32
    
    # Face outline
    for y in range(8):
        for x in range(8):
            if (x >= 2 and x <= 5 and y >= 2 and y <= 5) or \
               (x == 1 and y == 1) or (x == 6 and y == 1) or \
               (x == 1 and y == 6) or (x == 6 and y == 6):
                start_x = x_offset + (x * scale)
                start_y = y_offset + (y * scale)
                end_x = start_x + scale
                end_y = start_y + scale
                draw.rectangle((start_x, start_y, end_x, end_y), outline=255, fill=255)
    
    disp.LCD_ShowImage(image, 0, 0)
    print("Menu layout displayed")
    time.sleep(5)
    
    print("All tests completed!")
    
    # Wait for any button press to exit
    print("Press any button to exit...")
    while True:
        if (GPIO.input(KEY_UP_PIN) == 0 or 
            GPIO.input(KEY_DOWN_PIN) == 0 or
            GPIO.input(KEY_LEFT_PIN) == 0 or
            GPIO.input(KEY_RIGHT_PIN) == 0 or
            GPIO.input(KEY_PRESS_PIN) == 0 or
            GPIO.input(KEY1_PIN) == 0 or
            GPIO.input(KEY2_PIN) == 0 or
            GPIO.input(KEY3_PIN) == 0):
            print("Button pressed, exiting...")
            break
        time.sleep(0.1)

else:
    print("Cannot run LCD tests - LCD not available")
