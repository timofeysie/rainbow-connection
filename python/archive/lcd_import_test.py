# -*- coding:utf-8 -*-
# lcd_import_test.py - Test to isolate LCD import conflict

import time

print("Starting LCD import test...")

try:
    print("Test 1: Importing LCD_Config...")
    import LCD_Config
    print("✓ LCD_Config import successful")
except Exception as e:
    print(f"✗ LCD_Config import failed: {e}")
    exit(1)

try:
    print("Test 2: Importing LCD_1in44...")
    import LCD_1in44
    print("✓ LCD_1in44 import successful")
except Exception as e:
    print(f"✗ LCD_1in44 import failed: {e}")
    exit(1)

try:
    print("Test 3: Creating LCD object...")
    disp = LCD_1in44.LCD()
    print("✓ LCD object creation successful")
except Exception as e:
    print(f"✗ LCD object creation failed: {e}")
    exit(1)

try:
    print("Test 4: LCD initialization...")
    Lcd_ScanDir = LCD_1in44.SCAN_DIR_DFT
    disp.LCD_Init(Lcd_ScanDir)
    print("✓ LCD initialization successful")
except Exception as e:
    print(f"✗ LCD initialization failed: {e}")
    exit(1)

try:
    print("Test 5: LCD clear...")
    disp.LCD_Clear()
    print("✓ LCD clear successful")
except Exception as e:
    print(f"✗ LCD clear failed: {e}")
    exit(1)

print("\n🎉 ALL LCD TESTS PASSED!")
print("The LCD library itself is working correctly.")
print("The conflict must be when we try to use both LCD and GPIO together.")
