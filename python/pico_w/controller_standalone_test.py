# Simple standalone controller test - no receiver needed
import network
import time
from machine import Pin

def test_controller_ap():
    """Test just the controller AP creation"""
    led = Pin(25, Pin.OUT)
    
    print("🎮 Testing PicoController Access Point...")
    print("=" * 50)
    
    # Create AP
    ap = network.WLAN(network.AP_IF)
    ap.active(True)
    time.sleep(1)
    
    if not ap.active():
        print("❌ Failed to activate AP interface")
        return False
    
    print("✅ AP interface activated")
    
    # Configure AP
    configs = [
        {"essid": "PicoController", "password": "pico1234", "authmode": 3},
        {"essid": "PicoController", "password": "pico1234"},
        {"essid": "PicoController"}
    ]
    
    for i, config in enumerate(configs):
        try:
            print(f"\n🔧 Trying config {i+1}: {config}")
            ap.config(**config)
            time.sleep(3)  # Wait for config
            
            # Check if we can get network info
            net_config = ap.ifconfig()
            print(f"✅ SUCCESS! AP configured:")
            print(f"   Network: {config['essid']}")
            if 'password' in config:
                print(f"   Password: {config['password']}")
                print(f"   Security: WPA2")
            else:
                print(f"   Security: Open")
            print(f"   IP: {net_config[0]}")
            print(f"   Status: {ap.status()}")
            
            # Success blinks
            for _ in range(5):
                led.value(1)
                time.sleep(0.2)
                led.value(0)
                time.sleep(0.2)
            
            print(f"\n🎯 SUCCESS! Your WiFi network 'PicoController' should now be visible!")
            print(f"📱 Check your phone/computer WiFi settings")
            print(f"🔍 Look for network: {config['essid']}")
            if 'password' in config:
                print(f"🔑 Password: {config['password']}")
            
            # Keep AP running and show status
            print(f"\n⏳ Keeping AP active for 60 seconds...")
            print(f"💡 Check your phone's WiFi list now!")
            
            for countdown in range(60, 0, -5):
                print(f"   {countdown} seconds remaining...")
                
                # Heartbeat
                led.value(1)
                time.sleep(0.1)
                led.value(0)
                
                time.sleep(4.9)
            
            print(f"✅ Test completed successfully!")
            return True
            
        except Exception as e:
            print(f"❌ Config {i+1} failed: {e}")
    
    print(f"❌ All configurations failed")
    return False

if __name__ == "__main__":
    test_controller_ap() 