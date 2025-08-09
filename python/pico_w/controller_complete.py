# Complete controller with joystick/button input and WiFi transmission
import network
import socket
import json
import time
from machine import Pin

# Input pins - adjust these for your Waveshare module
JOYSTICK_UP = Pin(2, Pin.IN, Pin.PULL_UP)
JOYSTICK_DOWN = Pin(18, Pin.IN, Pin.PULL_UP)
JOYSTICK_LEFT = Pin(16, Pin.IN, Pin.PULL_UP)
JOYSTICK_RIGHT = Pin(20, Pin.IN, Pin.PULL_UP)
JOYSTICK_CENTER = Pin(3, Pin.IN, Pin.PULL_UP)
BUTTON_A = Pin(15, Pin.IN, Pin.PULL_UP)
BUTTON_B = Pin(17, Pin.IN, Pin.PULL_UP)

class GameController:
    def __init__(self):
        self.led = Pin(25, Pin.OUT)
        self.led.value(0)
        
        print("🎮 PicoController with Input Handling")
        print("=" * 40)
        
        # Create Access Point (using the method that worked)
        if not self.setup_access_point():
            print("❌ Failed to setup Access Point")
            return
        
        # Create UDP server
        if not self.setup_udp_server():
            print("❌ Failed to setup UDP server")
            return
        
        # Initialize controller state
        self.state = {
            'joystick': {
                'up': False,
                'down': False, 
                'left': False,
                'right': False,
                'center': False
            },
            'buttons': {
                'A': False,
                'B': False
            },
            'timestamp': 0
        }
        
        self.clients = set()
        self.last_state = None
        
        print("🎮 Controller ready! Press buttons and move joystick!")
        
    def setup_access_point(self):
        """Setup the Access Point with multiple fallback configs"""
        self.ap = network.WLAN(network.AP_IF)
        self.ap.active(True)
        time.sleep(1)
        
        if not self.ap.active():
            print("❌ Failed to activate AP interface")
            return False
        
        print("✅ AP interface activated")
        
        # Try multiple configurations (same as working standalone test)
        configs = [
            {"essid": "PicoController", "password": "pico1234", "authmode": 3},
            {"essid": "PicoController", "password": "pico1234"},
            {"essid": "PicoController"}
        ]
        
        for i, config in enumerate(configs):
            try:
                print(f"🔧 Trying AP config {i+1}: {config}")
                self.ap.config(**config)
                time.sleep(2)  # Wait for config to take effect
                
                # Test if we can get network info
                net_config = self.ap.ifconfig()
                print(f"✅ AP Config {i+1} SUCCESS!")
                print(f"   Network: {config['essid']}")
                if 'password' in config:
                    print(f"   Password: {config['password']}")
                    print(f"   Security: WPA2")
                else:
                    print(f"   Security: Open")
                print(f"   IP: {net_config[0]}")
                
                # Success blinks
                for _ in range(3):
                    self.led.value(1)
                    time.sleep(0.2)
                    self.led.value(0)
                    time.sleep(0.2)
                
                return True
                
            except Exception as e:
                print(f"❌ Config {i+1} failed: {e}")
                continue
        
        print("❌ All AP configurations failed!")
        return False
        
    def setup_udp_server(self):
        """Setup UDP server for communication"""
        try:
            self.sock = socket.socket(socket.AF_INET, socket.SOCK_DGRAM)
            self.sock.bind(('', 8888))
            self.sock.settimeout(0.01)  # Non-blocking
            print("📡 UDP server ready on port 8888")
            return True
        except Exception as e:
            print(f"❌ UDP server setup failed: {e}")
            return False
        
    def read_inputs(self):
        """Read all joystick and button inputs"""
        # Read joystick (active low - pressed = False)
        self.state['joystick']['up'] = not JOYSTICK_UP.value()
        self.state['joystick']['down'] = not JOYSTICK_DOWN.value()
        self.state['joystick']['left'] = not JOYSTICK_LEFT.value()
        self.state['joystick']['right'] = not JOYSTICK_RIGHT.value()
        self.state['joystick']['center'] = not JOYSTICK_CENTER.value()
        
        # Read buttons (active low - pressed = False)
        self.state['buttons']['A'] = not BUTTON_A.value()
        self.state['buttons']['B'] = not BUTTON_B.value()
        
        # Add timestamp
        self.state['timestamp'] = time.ticks_ms()
    
    def check_for_clients(self):
        """Listen for client discovery messages"""
        try:
            data, addr = self.sock.recvfrom(1024)
            message = data.decode()
            
            if message == "DISCOVER_CONTROLLER":
                if addr not in self.clients:
                    print(f"🎉 New receiver connected: {addr[0]}")
                    # Happy blink pattern
                    for _ in range(3):
                        self.led.value(1)
                        time.sleep(0.1)
                        self.led.value(0)
                        time.sleep(0.1)
                
                self.clients.add(addr)
                # Send acknowledgment
                self.sock.sendto(b"CONTROLLER_FOUND", addr)
                
        except OSError:
            pass  # Timeout - normal
        except Exception as e:
            print(f"Client check error: {e}")
    
    def broadcast_input_state(self):
        """Send current input state to all connected receivers"""
        if not self.clients:
            return
            
        # Convert state to JSON
        message = json.dumps(self.state).encode()
        
        # Send to all clients
        dead_clients = set()
        for client_addr in self.clients:
            try:
                self.sock.sendto(message, client_addr)
            except Exception as e:
                print(f"Failed to send to {client_addr}: {e}")
                dead_clients.add(client_addr)
        
        # Remove dead clients
        self.clients -= dead_clients
        
        # Activity blink
        if self.clients:
            self.led.value(1)
            time.sleep_ms(10)
            self.led.value(0)
    
    def print_active_inputs(self):
        """Print currently active inputs to console"""
        active_inputs = []
        
        # Check joystick
        for direction, active in self.state['joystick'].items():
            if active:
                active_inputs.append(f"Joy-{direction}")
        
        # Check buttons  
        for button, active in self.state['buttons'].items():
            if active:
                active_inputs.append(f"Btn-{button}")
        
        if active_inputs:
            clients_text = f"→ {len(self.clients)} clients" if self.clients else "→ no clients"
            print(f"📍 {', '.join(active_inputs)} {clients_text}")
    
    def run(self):
        """Main controller loop"""
        print("\n🚀 Starting main loop...")
        print("Press buttons and move joystick to see input!")
        print("Connect receiver to see data transmission!")
        
        status_timer = 0
        
        while True:
            try:
                # Check for new receivers
                self.check_for_clients()
                
                # Read current input state
                self.read_inputs()
                
                # Only process and send if state changed
                if self.state != self.last_state:
                    # Print active inputs
                    self.print_active_inputs()
                    
                    # Send to receivers
                    self.broadcast_input_state()
                    
                    # Update last state
                    self.last_state = self.state.copy()
                
                # Periodic status update
                current_time = time.ticks_ms()
                if time.ticks_diff(current_time, status_timer) > 10000:  # Every 10 seconds
                    print(f"💓 Status: {len(self.clients)} receivers connected")
                    status_timer = current_time
                
                time.sleep(0.02)  # 50Hz update rate
                
            except KeyboardInterrupt:
                print("\n👋 Controller stopped")
                break
            except Exception as e:
                print(f"❌ Error: {e}")
                time.sleep(1)

# Simple input test function
def test_inputs_only():
    """Test just the input pins without networking"""
    print("🎮 Testing Input Pins Only")
    print("Press buttons and move joystick...")
    print("Press Ctrl+C to stop")
    
    led = Pin(25, Pin.OUT)
    
    while True:
        try:
            inputs = []
            
            if not JOYSTICK_UP.value():
                inputs.append("UP")
            if not JOYSTICK_DOWN.value():
                inputs.append("DOWN")
            if not JOYSTICK_LEFT.value():
                inputs.append("LEFT")
            if not JOYSTICK_RIGHT.value():
                inputs.append("RIGHT")
            if not JOYSTICK_CENTER.value():
                inputs.append("CENTER")
            if not BUTTON_A.value():
                inputs.append("A")
            if not BUTTON_B.value():
                inputs.append("B")
            
            if inputs:
                print(f"📍 Active: {', '.join(inputs)}")
                led.value(1)
                time.sleep(0.1)
                led.value(0)
            
            time.sleep(0.1)
            
        except KeyboardInterrupt:
            print("\nInput test stopped")
            break

if __name__ == "__main__":
    # CHOOSE ONE:
    
    # Test inputs only (no networking)
    # test_inputs_only()
    
    # Run full controller
    controller = GameController()
    if hasattr(controller, 'sock'):  # Only run if setup succeeded
        controller.run()
    else:
        print("❌ Controller setup failed, cannot run") 