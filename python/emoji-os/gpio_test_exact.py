# -*- coding:utf-8 -*-
# gpio_test_exact.py - GPIO test that EXACTLY mimics key_demo.py

import RPi.GPIO as GPIO
import time

# GPIO pin definitions for Waveshare LCD HAT - EXACTLY like key_demo.py
KEY_UP_PIN     = 6 
KEY_DOWN_PIN   = 19
KEY_LEFT_PIN   = 5
KEY_RIGHT_PIN  = 26
KEY_PRESS_PIN  = 13
KEY1_PIN       = 21
KEY2_PIN       = 20
KEY3_PIN       = 16

print("Starting GPIO test - EXACTLY like key_demo.py...")

try:
    # EXACTLY like key_demo.py - init GPIO
    print("Test 1: GPIO setup EXACTLY like key_demo.py")
    GPIO.setmode(GPIO.BCM) 
    print("✓ GPIO.setmode(GPIO.BCM) successful")
    
    GPIO.cleanup()
    print("✓ GPIO.cleanup() successful")
    
    # EXACTLY like key_demo.py - setup all pins
    GPIO.setup(KEY_UP_PIN,      GPIO.IN, pull_up_down=GPIO.PUD_UP)    # Input with pull-up
    GPIO.setup(KEY_DOWN_PIN,    GPIO.IN, pull_up_down=GPIO.PUD_UP)  # Input with pull-up
    GPIO.setup(KEY_LEFT_PIN,    GPIO.IN, pull_up_down=GPIO.PUD_UP)  # Input with pull-up
    GPIO.setup(KEY_RIGHT_PIN,   GPIO.IN, pull_up_down=GPIO.PUD_UP) # Input with pull-up
    GPIO.setup(KEY_PRESS_PIN,   GPIO.IN, pull_up_down=GPIO.PUD_UP) # Input with pull-up
    GPIO.setup(KEY1_PIN,        GPIO.IN, pull_up_down=GPIO.PUD_UP)      # Input with pull-up
    GPIO.setup(KEY2_PIN,        GPIO.IN, pull_up_down=GPIO.PUD_UP)      # Input with pull-up
    GPIO.setup(KEY3_PIN,        GPIO.IN, pull_up_down=GPIO.PUD_UP)      # Input with pull-up
    
    print("✓ All GPIO pins setup successful - EXACTLY like key_demo.py")
    
except Exception as e:
    print(f"✗ GPIO setup failed: {e}")
    print("This explains why emoji-menu.py fails!")
    GPIO.cleanup()
    exit(1)

try:
    # Test 2: GPIO input reading - EXACTLY like key_demo.py
    print("\nTest 2: GPIO input reading - EXACTLY like key_demo.py")
    print("Press buttons to see values (or wait 10 seconds)...")
    
    for i in range(10):
        up_val = GPIO.input(KEY_UP_PIN)
        down_val = GPIO.input(KEY_DOWN_PIN)
        left_val = GPIO.input(KEY_LEFT_PIN)
        right_val = GPIO.input(KEY_RIGHT_PIN)
        center_val = GPIO.input(KEY_PRESS_PIN)
        key1_val = GPIO.input(KEY1_PIN)
        key2_val = GPIO.input(KEY2_PIN)
        key3_val = GPIO.input(KEY3_PIN)
        
        print(f"  {i+1}/10: UP:{up_val} DOWN:{down_val} LEFT:{left_val} RIGHT:{right_val} CENTER:{center_val} KEY1:{key1_val} KEY2:{key2_val} KEY3:{key3_val}")
        time.sleep(1)
    
    print("Test 2 PASSED - GPIO input reading works")
    
except Exception as e:
    print(f"Test 2 FAILED: {e}")
    GPIO.cleanup()
    exit(1)

print("\n🎉 ALL TESTS PASSED!")
print("GPIO is working correctly when using key_demo.py's exact sequence.")
print("The issue must be elsewhere in our emoji-menu.py file.")

GPIO.cleanup()
print("GPIO cleanup completed.")
