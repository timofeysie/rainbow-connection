# Controller connects to home WiFi instead of creating AP
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

def connect_to_wifi():
    """Connect to home WiFi network"""
    wlan = network.WLAN(network.STA_IF)
    wlan.active(True)
    
    # Use a different WiFi network that works with Pico W
    # You mentioned your router has WPA3 issues - try guest network or 2.4GHz
    wifi_networks = [
        ("Lucienne Home", "your_wifi_password"),  # Replace with actual password
        # Add other networks you can try
    ]
    
    for ssid, password in wifi_networks:
        print(f"🔗 Trying to connect to '{ssid}'...")
        
        try:
            wlan.connect(ssid, password)
            
            # Wait for connection
            for i in range(20):
                if wlan.isconnected():
                    config = wlan.ifconfig()
                    print(f"✅ Connected to '{ssid}'!")
                    print(f"   Controller IP: {config[0]}")
                    return wlan, config[0]
                
                time.sleep(1)
                if i % 5 == 0:
                    print(f"   Connecting... ({i+1}s)")
            
            print(f"❌ Connection to '{ssid}' timed out")
            
        except Exception as e:
            print(f"❌ Connection to '{ssid}' failed: {e}")
    
    return None, None

def setup_controller():
    """Setup controller using home WiFi"""
    print("🎮 PicoController - Home WiFi Mode")
    print("=" * 40)
    
    # Connect to home WiFi
    wlan, controller_ip = connect_to_wifi()
    if not wlan or not controller_ip:
        print("❌ Failed to connect to WiFi")
        return
    
    # Create UDP server
    print("📡 Setting up UDP server...")
    try:
        sock = socket.socket(socket.AF_INET, socket.SOCK_DGRAM)
        sock.bind(('', 8888))
        sock.settimeout(0.01)
        print(f"✅ UDP server ready on {controller_ip}:8888")
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
    
    print(f"🚀 Controller ready!")
    print(f"📍 Controller IP: {controller_ip}")
    print(f"🎮 Receiver should connect to this IP")
    
    # Main loop
    while True:
        try:
            # Check WiFi connection
            if not wlan.isconnected():
                print("⚠️ WiFi disconnected, trying to reconnect...")
                wlan, controller_ip = connect_to_wifi()
                if not controller_ip:
                    print("❌ WiFi reconnection failed")
                    time.sleep(5)
                    continue
            
            # Check for clients
            try:
                data, addr = sock.recvfrom(1024)
                message = data.decode()
                
                if message == "DISCOVER_CONTROLLER":
                    if addr not in clients:
                        print(f"🎉 New receiver: {addr[0]}")
                    clients.add(addr)
                    sock.sendto(f"CONTROLLER_AT_{controller_ip}".encode(), addr)
                    
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
                    if v: active.append(f"Joy-{k}")
                for k, v in state['buttons'].items():
                    if v: active.append(f"Btn-{k}")
                
                if active:
                    print(f"📍 {', '.join(active)} → {len(clients)} receivers")
                
                last_state = state.copy()
            
            # Status update
            current_time = time.ticks_ms()
            if time.ticks_diff(current_time, status_timer) > 15000:
                print(f"💓 Status: {len(clients)} receivers | IP: {controller_ip}")
                status_timer = current_time
            
            time.sleep(0.02)
            
        except Exception as e:
            print(f"❌ Error: {e}")
            time.sleep(1)

print("🔄 Controller starting (WiFi client mode)...")
setup_controller() 