# -*- coding:utf-8 -*-
# gpio_test.py - Minimal GPIO test to isolate the conflict

import RPi.GPIO as GPIO
import time

# GPIO pin definitions for Waveshare LCD HAT
KEY_UP_PIN     = 6 
KEY_DOWN_PIN   = 19
KEY_LEFT_PIN   = 5
KEY_RIGHT_PIN  = 26
KEY_PRESS_PIN  = 13
KEY1_PIN       = 21
KEY2_PIN       = 20
KEY3_PIN       = 16

print("Starting GPIO test...")

try:
    # Test 1: Just GPIO setup
    print("Test 1: Basic GPIO setup")
    GPIO.setmode(GPIO.BCM)
    print("✓ GPIO.setmode(GPIO.BCM) successful")
    
    GPIO.cleanup()
    print("✓ GPIO.cleanup() successful")
    
    GPIO.setup(KEY_UP_PIN, GPIO.IN, pull_up_down=GPIO.PUD_UP)
    print("✓ GPIO.setup(KEY_UP_PIN) successful")
    
    print("Test 1 PASSED - Basic GPIO works")
    
except Exception as e:
    print(f"Test 1 FAILED: {e}")
    GPIO.cleanup()
    exit(1)

try:
    # Test 2: All GPIO pins
    print("\nTest 2: All GPIO pins setup")
    GPIO.setup(KEY_DOWN_PIN, GPIO.IN, pull_up_down=GPIO.PUD_UP)
    GPIO.setup(KEY_LEFT_PIN, GPIO.IN, pull_up_down=GPIO.PUD_UP)
    GPIO.setup(KEY_RIGHT_PIN, GPIO.IN, pull_up_down=GPIO.PUD_UP)
    GPIO.setup(KEY_PRESS_PIN, GPIO.IN, pull_up_down=GPIO.PUD_UP)
    GPIO.setup(KEY1_PIN, GPIO.IN, pull_up_down=GPIO.PUD_UP)
    GPIO.setup(KEY2_PIN, GPIO.IN, pull_up_down=GPIO.PUD_UP)
    GPIO.setup(KEY3_PIN, GPIO.IN, pull_up_down=GPIO.PUD_UP)
    print("✓ All GPIO pins setup successful")
    
    print("Test 2 PASSED - All GPIO pins work")
    
except Exception as e:
    print(f"Test 2 FAILED: {e}")
    GPIO.cleanup()
    exit(1)

try:
    # Test 3: GPIO input reading
    print("\nTest 3: GPIO input reading")
    for i in range(5):
        up_val = GPIO.input(KEY_UP_PIN)
        print(f"  KEY_UP_PIN value: {up_val}")
        time.sleep(0.5)
    
    print("Test 3 PASSED - GPIO input reading works")
    
except Exception as e:
    print(f"Test 3 FAILED: {e}")
    GPIO.cleanup()
    exit(1)

print("\n🎉 ALL TESTS PASSED! GPIO is working correctly.")
print("The issue must be with the LCD library, not GPIO itself.")

GPIO.cleanup()
print("GPIO cleanup completed.")
