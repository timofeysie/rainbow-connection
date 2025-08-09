# Save this EXACTLY as main.py on the Pico W
# Fixed controller that auto-starts on power-up (no LED code)
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

def setup_controller():
    """Setup and run the controller"""
    print("🎮 AUTO-START PicoController")
    print("=" * 35)
    print("Running from main.py!")
    
    # Setup Access Point
    print("📡 Creating Access Point...")
    ap = network.WLAN(network.AP_IF)
    ap.active(False)
    time.sleep(1)
    ap.active(True)
    time.sleep(2)
    
    if not ap.active():
        print("❌ AP activation failed")
        return False
    
    try:
        # Configure AP
        print("🔧 Configuring AP...")
        ap.config(essid="PicoController", password="pico1234")
        time.sleep(3)
        
        net_config = ap.ifconfig()
        print(f"✅ PicoController network created!")
        print(f"   SSID: PicoController")
        print(f"   Password: pico1234")
        print(f"   IP: {net_config[0]}")
        
    except Exception as e:
        print(f"❌ AP config failed: {e}")
        return False
    
    # Setup UDP server
    print("📡 Setting up UDP server...")
    try:
        sock = socket.socket(socket.AF_INET, socket.SOCK_DGRAM)
        sock.bind(('', 8888))
        sock.settimeout(0.01)
        print("✅ UDP server ready on port 8888")
    except Exception as e:
        print(f"❌ UDP failed: {e}")
        return False
    
    # Controller state
    state = {
        'joystick': {'up': False, 'down': False, 'left': False, 'right': False, 'center': False},
        'buttons': {'A': False, 'B': False},
        'timestamp': 0
    }
    
    clients = set()
    last_state = None
    status_timer = 0
    
    print("🚀 Controller running from main.py!")
    print("📱 'PicoController' should now appear in WiFi lists")
    print("🎮 Ready for button presses and receiver connections!")
    
    # Main loop
    while True:
        try:
            # Check for clients
            try:
                data, addr = sock.recvfrom(1024)
                message = data.decode()
                
                if message == "DISCOVER_CONTROLLER":
                    if addr not in clients:
                        print(f"🎉 New receiver connected: {addr[0]}")
                    
                    clients.add(addr)
                    sock.sendto(b"CONTROLLER_FOUND", addr)
                    
            except OSError:
                pass  # Timeout - normal
            
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
                    if v: active.append(f"Joy-{k}")
                for k, v in state['buttons'].items():
                    if v: active.append(f"Btn-{k}")
                
                if active:
                    print(f"📍 Input: {', '.join(active)} → {len(clients)} receivers")
                
                last_state = state.copy()
            
            # Status update every 15 seconds
            current_time = time.ticks_ms()
            if time.ticks_diff(current_time, status_timer) > 15000:
                print(f"💓 Status: {len(clients)} receivers connected")
                print(f"   AP Active: {ap.active()}")
                try:
                    print(f"   IP: {ap.ifconfig()[0]}")
                except:
                    print(f"   IP: Error getting IP")
                status_timer = current_time
            
            time.sleep(0.02)  # 50Hz update rate
            
        except KeyboardInterrupt:
            print("👋 Controller stopped")
            break
        except Exception as e:
            print(f"❌ Main loop error: {e}")
            time.sleep(1)

# This runs automatically when main.py is loaded
print("🔄 main.py starting...")
setup_controller() 