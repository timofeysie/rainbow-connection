# -*- coding:utf-8 -*-
# gpio_debug.py - Debug GPIO busy error

import time
import subprocess
import os

print("🔍 GPIO Debug - Let's find what's using GPIO...")

# Check 1: What processes are using GPIO
print("\n1️⃣ Checking for processes using GPIO...")
try:
    result = subprocess.run(['sudo', 'lsof', '/dev/gpiomem'], capture_output=True, text=True)
    if result.stdout:
        print("Processes using /dev/gpiomem:")
        print(result.stdout)
    else:
        print("No processes using /dev/gpiomem")
except Exception as e:
    print(f"Couldn't check /dev/gpiomem: {e}")

# Check 2: GPIO device status
print("\n2️⃣ Checking GPIO device status...")
try:
    result = subprocess.run(['ls', '-la', '/dev/gpiomem'], capture_output=True, text=True)
    if result.stdout:
        print("GPIO device status:")
        print(result.stdout)
    else:
        print("GPIO device not found")
except Exception as e:
    print(f"Couldn't check GPIO device: {e}")

# Check 3: Try to import libraries one by one
print("\n3️⃣ Testing library imports...")

try:
    print("Importing RPi.GPIO...")
    import RPi.GPIO as GPIO
    print("✓ RPi.GPIO imported successfully")
except Exception as e:
    print(f"✗ RPi.GPIO import failed: {e}")

try:
    print("Importing LCD_Config...")
    import LCD_Config
    print("✓ LCD_Config imported successfully")
except Exception as e:
    print(f"✗ LCD_Config import failed: {e}")

try:
    print("Importing LCD_1in44...")
    import LCD_1in44
    print("✓ LCD_1in44 imported successfully")
except Exception as e:
    print(f"✗ LCD_1in44 import failed: {e}")

# Check 4: Try GPIO setup step by step
print("\n4️⃣ Testing GPIO setup step by step...")

try:
    print("Setting GPIO mode...")
    GPIO.setmode(GPIO.BCM)
    print("✓ GPIO.setmode(GPIO.BCM) successful")
except Exception as e:
    print(f"✗ GPIO.setmode failed: {e}")
    exit(1)

try:
    print("Calling GPIO.cleanup()...")
    GPIO.cleanup()
    print("✓ GPIO.cleanup() successful")
except Exception as e:
    print(f"✗ GPIO.cleanup failed: {e}")
    exit(1)

try:
    print("Setting GPIO mode again...")
    GPIO.setmode(GPIO.BCM)
    print("✓ GPIO.setmode(GPIO.BCM) again successful")
except Exception as e:
    print(f"✗ Second GPIO.setmode failed: {e}")
    exit(1)

try:
    print("Setting up first GPIO pin...")
    GPIO.setup(6, GPIO.IN, pull_up_down=GPIO.PUD_UP)
    print("✓ First GPIO pin setup successful")
except Exception as e:
    print(f"✗ GPIO pin setup failed: {e}")
    print("This is where the GPIO busy error occurs!")
    GPIO.cleanup()
    exit(1)

print("\n🎉 All GPIO tests passed!")
print("The issue must be elsewhere...")

GPIO.cleanup()
print("GPIO cleanup completed.")
