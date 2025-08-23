# -*- coding:utf-8 -*-
# combined_test.py - Test to find exact conflict point between GPIO and LCD

import time

print("Starting combined GPIO + LCD test...")

try:
    print("Test 1: Importing libraries...")
    import LCD_Config
    import LCD_1in44
    print("✓ All imports successful")
except Exception as e:
    print(f"✗ Import failed: {e}")
    exit(1)

try:
    print("Test 2: Creating LCD object...")
    disp = LCD_1in44.LCD()
    print("✓ LCD object created")
except Exception as e:
    print(f"✗ LCD object creation failed: {e}")
    exit(1)

try:
    print("Test 3: LCD initialization...")
    Lcd_ScanDir = LCD_1in44.SCAN_DIR_DFT
    disp.LCD_Init(Lcd_ScanDir)
    disp.LCD_Clear()
    print("✓ LCD initialized and cleared")
except Exception as e:
    print(f"✗ LCD initialization failed: {e}")
    exit(1)

try:
    print("Test 4: GPIO setup...")
    import RPi.GPIO as GPIO
    
    # GPIO pin definitions
    KEY_UP_PIN = 6
    KEY_DOWN_PIN = 19
    KEY_LEFT_PIN = 5
    KEY_RIGHT_PIN = 26
    KEY_PRESS_PIN = 13
    KEY1_PIN = 21
    KEY2_PIN = 20
    KEY3_PIN = 16
    
    GPIO.setmode(GPIO.BCM)
    print("✓ GPIO.setmode successful")
    
    GPIO.cleanup()
    print("✓ GPIO.cleanup successful")
    
    GPIO.setup(KEY_UP_PIN, GPIO.IN, pull_up_down=GPIO.PUD_UP)
    print("✓ First GPIO pin setup successful")
    
    print("Test 4 PASSED - GPIO setup works after LCD")
    
except Exception as e:
    print(f"Test 4 FAILED: {e}")
    print("This is the conflict point!")
    GPIO.cleanup()
    exit(1)

try:
    print("Test 5: All GPIO pins...")
    GPIO.setup(KEY_DOWN_PIN, GPIO.IN, pull_up_down=GPIO.PUD_UP)
    GPIO.setup(KEY_LEFT_PIN, GPIO.IN, pull_up_down=GPIO.PUD_UP)
    GPIO.setup(KEY_RIGHT_PIN, GPIO.IN, pull_up_down=GPIO.PUD_UP)
    GPIO.setup(KEY_PRESS_PIN, GPIO.IN, pull_up_down=GPIO.PUD_UP)
    GPIO.setup(KEY1_PIN, GPIO.IN, pull_up_down=GPIO.PUD_UP)
    GPIO.setup(KEY2_PIN, GPIO.IN, pull_up_down=GPIO.PUD_UP)
    GPIO.setup(KEY3_PIN, GPIO.IN, pull_up_down=GPIO.PUD_UP)
    print("✓ All GPIO pins setup successful")
    
    print("Test 5 PASSED - All GPIO pins work after LCD")
    
except Exception as e:
    print(f"Test 5 FAILED: {e}")
    GPIO.cleanup()
    exit(1)

print("\n🎉 ALL TESTS PASSED!")
print("The combination of LCD + GPIO is working correctly.")
print("The issue must be elsewhere in our emoji-menu.py file.")

GPIO.cleanup()
print("GPIO cleanup completed.")
