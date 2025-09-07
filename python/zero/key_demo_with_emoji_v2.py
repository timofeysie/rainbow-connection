# -*- coding:utf-8 -*-
import LCD_1in44
import LCD_Config
import RPi.GPIO as GPIO
import time
from PIL import Image, ImageDraw, ImageFont, ImageColor

KEY_UP_PIN     = 6 
KEY_DOWN_PIN   = 19
KEY_LEFT_PIN   = 5
KEY_RIGHT_PIN  = 26
KEY_PRESS_PIN  = 13
KEY1_PIN       = 21
KEY2_PIN       = 20
KEY3_PIN       = 16

#init GPIO
GPIO.setmode(GPIO.BCM) 
GPIO.setup(KEY_UP_PIN,      GPIO.IN, pull_up_down=GPIO.PUD_UP)    # Input with pull-up
GPIO.setup(KEY_DOWN_PIN,    GPIO.IN, pull_up_down=GPIO.PUD_UP)  # Input with pull-up
GPIO.setup(KEY_LEFT_PIN,    GPIO.IN, pull_up_down=GPIO.PUD_UP)  # Input with pull-up
GPIO.setup(KEY_RIGHT_PIN,   GPIO.IN, pull_up_down=GPIO.PUD_UP) # Input with pull-up
GPIO.setup(KEY_PRESS_PIN,   GPIO.IN, pull_up_down=GPIO.PUD_UP) # Input with pull-up
GPIO.setup(KEY1_PIN,        GPIO.IN, pull_up_down=GPIO.PUD_UP)      # Input with pull-up
GPIO.setup(KEY2_PIN,        GPIO.IN, pull_up_down=GPIO.PUD_UP)      # Input with pull-up
GPIO.setup(KEY3_PIN,        GPIO.IN, pull_up_down=GPIO.PUD_UP)      # Input with pull-up

# 240x240 display with hardware SPI:
disp = LCD_1in44.LCD()
Lcd_ScanDir = LCD_1in44.SCAN_DIR_DFT  #SCAN_DIR_DFT = D2U_L2R
disp.LCD_Init(Lcd_ScanDir)
disp.LCD_Clear()

# Create blank image for drawing.
# Make sure to create image with mode '1' for 1-bit color.
width = 128
height = 128
image = Image.new('RGB', (width, height))

# Get drawing object to draw on image.
draw = ImageDraw.Draw(image)

# Draw a black filled box to clear the image.
draw.rectangle((0,0,width,height), outline=0, fill=0)
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

# === Function to draw main emoji at bottom half ===
def draw_main_emoji():
    # Clear bottom half of screen
    draw.rectangle((0, 64, 128, 128), outline=0, fill=0)
    
    # Draw main emoji in bottom half
    scale = 7
    emoji_width = scale * 8
    emoji_height = scale * 8
    start_x = (width - emoji_width) // 2
    start_y = 64 + (64 - emoji_height) // 2  # Center in bottom half
    draw_emoji(draw, smiley_matrix, color_map, scale, start_x, start_y)

# === Function to draw joystick indicators in top half ===
def draw_joystick_indicators():
    # Clear top half of screen
    draw.rectangle((0, 0, 128, 64), outline=0, fill=0)
    
    # Draw joystick indicators in top half
    if GPIO.input(KEY_UP_PIN) == 0: # button is released       
        draw.polygon([(20, 20), (30, 2), (40, 20)], outline=255, fill=0xff00)  #Up        
        print('Up')        
    else: # button is pressed:
        draw.polygon([(20, 20), (30, 2), (40, 20)], outline=255, fill=0)  #Up filled
        
    if GPIO.input(KEY_LEFT_PIN) == 0: # button is released
        draw.polygon([(0, 30), (18, 21), (18, 41)], outline=255, fill=0xff00)  #left
        print('left')        
    else: # button is pressed:       
        draw.polygon([(0, 30), (18, 21), (18, 41)], outline=255, fill=0)  #left filled
        
    if GPIO.input(KEY_RIGHT_PIN) == 0: # button is released
        draw.polygon([(60, 30), (42, 21), (42, 41)], outline=255, fill=0xff00) #right
        print('right')
    else: # button is pressed:
        draw.polygon([(60, 30), (42, 21), (42, 41)], outline=255, fill=0) #right filled       
        
    if GPIO.input(KEY_DOWN_PIN) == 0: # button is released
        draw.polygon([(30, 60), (40, 42), (20, 42)], outline=255, fill=0xff00) #down
        print('down')
    else: # button is pressed:
        draw.polygon([(30, 60), (40, 42), (20, 42)], outline=255, fill=0) #down filled
        
    if GPIO.input(KEY_PRESS_PIN) == 0: # button is released
        draw.rectangle((20, 22,40,40), outline=255, fill=0xff00) #center 
        print('center')
    else: # button is pressed:
        draw.rectangle((20, 22,40,40), outline=255, fill=0) #center filled
        
    if GPIO.input(KEY1_PIN) == 0: # button is released
        draw.ellipse((70,0,90,20), outline=255, fill=0xff00) #A button
        print('KEY1')
    else: # button is pressed:
        draw.ellipse((70,0,90,20), outline=255, fill=0) #A button filled
        
    if GPIO.input(KEY2_PIN) == 0: # button is released
        draw.ellipse((100,20,120,40), outline=255, fill=0xff00) #B button]
        print('KEY2')
    else: # button is pressed:
        draw.ellipse((100,20,120,40), outline=255, fill=0) #B button filled
        
    if GPIO.input(KEY3_PIN) == 0: # button is released
        draw.ellipse((70,40,90,60), outline=255, fill=0xff00) #A button
        print('KEY3')
    else: # button is pressed:
        draw.ellipse((70,40,90,60), outline=255, fill=0) #A button filled

# Main loop
while 1:
    # Draw joystick indicators in top half
    draw_joystick_indicators()
    
    # Draw main emoji in bottom half
    draw_main_emoji()
    
    # Update display
    disp.LCD_ShowImage(image,0,0)
