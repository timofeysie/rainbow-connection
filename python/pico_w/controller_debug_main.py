# Debug controller to see what's happening with AP naming
import network
import socket
import json
import time
from machine import Pin

# Input pins
JOYSTICK_UP = Pin(2, Pin.IN, Pin.PULL_UP)
JOYSTICK_DOWN = Pin(18, Pin.IN, Pin.PULL_UP)
JOYSTICK_LEFT = Pin(16, Pin.IN, Pin.PULL_UP)
JOYSTICK_RIGHT = Pin(20, Pin.IN, Pin.PULL_UP)
JOYSTICK_CENTER = Pin(3, Pin.IN, Pin.PULL_UP)
BUTTON_A = Pin(15, Pin.IN, Pin.PULL_UP)
BUTTON_B = Pin(17, Pin.IN, Pin.PULL_UP)

def debug_controller():
    led = Pin(25, Pin.OUT)
    
    # Startup blinks
    for _ in range(5):
        led.value(1)
        time.sleep(0.1)
        led.value(0)
        time.sleep(0.1)
    
    print("🎮 DEBUG Controller Starting...")
    print("=" * 40)
    
    # Create AP
    ap = network.WLAN(network.AP_IF)
    ap.active(True)
    time.sleep(2)
    
    print(f"AP active: {ap.active()}")
    
    # Try our configurations and see what actually gets set
    configs = [
        {"essid": "PicoController", "password": "pico1234", "authmode": 3},
        {"essid": "PicoController", "password": "pico1234"},
        {"essid": "PicoController"}
    ]
    
    for i, config in enumerate(configs):
        try:
            print(f"\n🔧 Trying config {i+1}: {config}")
            ap.config(**config)
            time.sleep(3)
            
            # Check what actually got configured
            net_config = ap.ifconfig()
            print(f"✅ Config {i+1} applied successfully")
            print(f"   IP: {net_config[0]}")
            print(f"   Status: {ap.status()}")
            
            # Try to get the actual SSID (this might not work in MicroPython)
            try:
                # Some versions support getting the config back
                current_config = ap.config('essid')
                print(f"   Actual SSID: {current_config}")
            except:
                print(f"   Cannot read back SSID (normal)")
            
            # Success - break and continue
            break
            
        except Exception as e:
            print(f"❌ Config {i+1} failed: {e}")
            continue
    
    print(f"\n📡 Access Point should be broadcasting...")
    print(f"🔍 Check your phone - what network name do you see?")
    
    # Create UDP server
    try:
        sock = socket.socket(socket.AF_INET, socket.SOCK_DGRAM)
        sock.bind(('', 8888))
        sock.settimeout(0.01)
        print("📡 UDP server ready on port 8888")
    except Exception as e:
        print(f"❌ UDP failed: {e}")
        return
    
    # Controller state
    state = {
        'joystick': {'up': False, 'down': False, 'left': False, 'right': False, 'center': False},
        'buttons': {'A': False, 'B': False},
        'timestamp': 0
    }
    
    clients = set()
    last_state = None
    status_timer = 0
    
    print(f"\n🚀 Debug controller running!")
    print(f"📱 Network name on phone: ? (tell me what you see)")
    
    # Main loop
    while True:
        try:
            # Check for clients
            try:
                data, addr = sock.recvfrom(1024)
                message = data.decode()
                
                if message == "DISCOVER_CONTROLLER":
                    if addr not in clients:
                        print(f"🎉 NEW CLIENT: {addr[0]}")
                        # Happy blinks
                        for _ in range(5):
                            led.value(1)
                            time.sleep(0.1)
                            led.value(0)
                            time.sleep(0.1)
                    
                    clients.add(addr)
                    sock.sendto(b"CONTROLLER_FOUND", addr)
                    
            except OSError:
                pass
            
            # Read inputs
            state['joystick']['up'] = not JOYSTICK_UP.value()
            state['joystick']['down'] = not JOYSTICK_DOWN.value()
            state['joystick']['left'] = not JOYSTICK_LEFT.value()
            state['joystick']['right'] = not JOYSTICK_RIGHT.value()
            state['joystick']['center'] = not JOYSTICK_CENTER.value()
            state['buttons']['A'] = not BUTTON_A.value()
            state['buttons']['B'] = not BUTTON_B.value()
            state['timestamp'] = time.ticks_ms()
            
            # Send data if changed
            if state != last_state and clients:
                message = json.dumps(state).encode()
                for client_addr in clients:
                    try:
                        sock.sendto(message, client_addr)
                    except:
                        pass
                
                # Show active inputs
                active = []
                for k, v in state['joystick'].items():
                    if v: active.append(f"J-{k}")
                for k, v in state['buttons'].items():
                    if v: active.append(f"B-{k}")
                
                if active:
                    print(f"📍 {','.join(active)} → {len(clients)} clients")
                
                last_state = state.copy()
                led.value(1)
                time.sleep_ms(10)
                led.value(0)
            
            # Status update
            current_time = time.ticks_ms()
            if time.ticks_diff(current_time, status_timer) > 15000:  # Every 15 seconds
                print(f"💓 Status: {len(clients)} clients | AP: {ap.active()}")
                status_timer = current_time
            
            time.sleep(0.02)
            
        except Exception as e:
            print(f"❌ Error: {e}")
            time.sleep(1)

if __name__ == "__main__":
    debug_controller() 