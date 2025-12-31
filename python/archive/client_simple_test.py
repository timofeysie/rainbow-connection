"""
Simple BLE Advertising Test for Pico 2 W
This script just advertises without the full UART service to test basic BLE functionality
"""

import bluetooth
import time
from machine import Pin
from ble_advertising import advertising_payload

# Initialize LED
led = Pin("LED", Pin.OUT)
led.off()

def main():
    """Simple advertising test"""
    print("BLE Advertising Test")
    print("=" * 30)
    
    # Initialize BLE
    ble = bluetooth.BLE()
    ble.active(True)
    
    # Create advertising payload
    payload = advertising_payload(name="Pico-Client", services=[])
    
    print("Starting simple advertising...")
    print("Device name: Pico-Client")
    print("Press Ctrl+C to stop")
    
    try:
        # Start advertising
        ble.gap_advertise(500000, adv_data=payload)
        
        # Blink LED to show it's working
        while True:
            led.on()
            time.sleep(0.5)
            led.off()
            time.sleep(0.5)
            
    except KeyboardInterrupt:
        print("\nStopping advertising...")
        ble.gap_advertise(None)  # Stop advertising
        ble.active(False)
        led.off()
        print("Done")


if __name__ == "__main__":
    main()
