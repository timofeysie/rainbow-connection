# Quick test - run this to verify controller works before saving as main.py
import network
import time
from machine import Pin

def quick_controller_test():
    led = Pin(25, Pin.OUT)
    
    print("🎮 Quick Controller Test")
    print("This will run for 60 seconds...")
    
    # Create AP
    ap = network.WLAN(network.AP_IF)
    ap.active(True)
    time.sleep(2)
    
    # Configure (use the method that worked)
    ap.config(essid="PicoController", password="pico1234")
    time.sleep(3)
    
    try:
        ip = ap.ifconfig()[0]
        print(f"✅ PicoController network created!")
        print(f"   IP: {ip}")
        print(f"📱 Check your phone - you should see 'PicoController'")
        
        # Run for 60 seconds with heartbeat
        for i in range(60):
            led.value(1)
            time.sleep(0.1)
            led.value(0)
            time.sleep(0.9)
            
            if i % 10 == 0:
                print(f"   Running... {60-i} seconds left")
        
        print("✅ Test complete!")
        
    except Exception as e:
        print(f"❌ Test failed: {e}")

if __name__ == "__main__":
    quick_controller_test() 