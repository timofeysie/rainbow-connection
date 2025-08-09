# Fixed controller - save this as main.py on your controller Pico W
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

class GameController:
    def __init__(self):
        self.led = Pin(25, Pin.OUT)
        self.led.value(0)
        
        print("🎮 Fixed PicoController Starting")
        print("=" * 40)
        
        # Create Access Point with simpler, more reliable method
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
                'up': False, 'down': False, 'left': False, 'right': False, 'center': False
            },
            'buttons': {
                'A': False, 'B': False
            },
            'timestamp': 0
        }
        
        self.clients = set()
        self.last_state = None
        
        print("🎮 Controller ready!")
        
    def setup_access_point(self):
        """Setup AP with the simplest method that works"""
        print("📡 Setting up Access Point...")
        
        # Deactivate first to ensure clean state
        ap = network.WLAN(network.AP_IF)
        ap.active(False)
        time.sleep(1)
        
        # Activate
        ap.active(True)
        time.sleep(2)
        
        if not ap.active():
            print("❌ Failed to activate AP")
            return False
        
        print("✅ AP interface activated")
        
        # Try the simplest configuration first (just SSID and password)
        try:
            print("🔧 Configuring AP with simple method...")
            ap.config(essid="PicoController", password="pico1234")
            time.sleep(3)  # Give it time to apply
            
            # Verify configuration worked
            net_config = ap.ifconfig()
            print(f"✅ AP configured successfully!")
            print(f"   Network: PicoController")
            print(f"   Password: pico1234")
            print(f"   IP: {net_config[0]}")
            
            self.ap = ap
            
            # Success blinks
            for _ in range(5):
                self.led.value(1)
                time.sleep(0.2)
                self.led.value(0)
                time.sleep(0.2)
            
            return True
            
        except Exception as e:
            print(f"❌ Simple config failed: {e}")
            
            # Fallback: try open network
            try:
                print("🔧 Trying open network as fallback...")
                ap.config(essid="PicoController")
                time.sleep(3)
                
                net_config = ap.ifconfig()
                print(f"✅ Open AP configured!")
                print(f"   Network: PicoController (OPEN - no password)")
                print(f"   IP: {net_config[0]}")
                
                self.ap = ap
                
                # Different blink pattern for open network
                for _ in range(3):
                    self.led.value(1)
                    time.sleep(0.5)
                    self.led.value(0)
                    time.sleep(0.2)
                
                return True
                
            except Exception as e2:
                print(f"❌ Open config also failed: {e2}")
                return False
        
    def setup_udp_server(self):
        """Setup UDP server"""
        try:
            self.sock = socket.socket(socket.AF_INET, socket.SOCK_DGRAM)
            self.sock.bind(('', 8888))
            self.sock.settimeout(0.01)
            print("📡 UDP server ready on port 8888")
            return True
        except Exception as e:
            print(f"❌ UDP server failed: {e}")
            return False
        
    def read_inputs(self):
        """Read all inputs"""
        self.state['joystick']['up'] = not JOYSTICK_UP.value()
        self.state['joystick']['down'] = not JOYSTICK_DOWN.value()
        self.state['joystick']['left'] = not JOYSTICK_LEFT.value()
        self.state['joystick']['right'] = not JOYSTICK_RIGHT.value()
        self.state['joystick']['center'] = not JOYSTICK_CENTER.value()
        self.state['buttons']['A'] = not BUTTON_A.value()
        self.state['buttons']['B'] = not BUTTON_B.value()
        self.state['timestamp'] = time.ticks_ms()
    
    def check_for_clients(self):
        """Check for new clients"""
        try:
            data, addr = self.sock.recvfrom(1024)
            message = data.decode()
            
            if message == "DISCOVER_CONTROLLER":
                if addr not in self.clients:
                    print(f"🎉 New receiver: {addr[0]}")
                    # Happy blinks
                    for _ in range(3):
                        self.led.value(1)
                        time.sleep(0.1)
                        self.led.value(0)
                        time.sleep(0.1)
                
                self.clients.add(addr)
                self.sock.sendto(b"CONTROLLER_FOUND", addr)
                
        except OSError:
            pass
        except Exception as e:
            print(f"Client error: {e}")
    
    def broadcast_input_state(self):
        """Send input state to receivers"""
        if not self.clients:
            return
            
        message = json.dumps(self.state).encode()
        
        dead_clients = set()
        for client_addr in self.clients:
            try:
                self.sock.sendto(message, client_addr)
            except Exception as e:
                dead_clients.add(client_addr)
        
        self.clients -= dead_clients
        
        if self.clients:
            self.led.value(1)
            time.sleep_ms(10)
            self.led.value(0)
    
    def print_active_inputs(self):
        """Print active inputs"""
        active = []
        for k, v in self.state['joystick'].items():
            if v: active.append(f"Joy-{k}")
        for k, v in self.state['buttons'].items():
            if v: active.append(f"Btn-{k}")
        
        if active:
            print(f"📍 {','.join(active)} → {len(self.clients)} clients")
    
    def run(self):
        """Main loop"""
        print("\n🚀 Controller running!")
        status_timer = 0
        
        while True:
            try:
                self.check_for_clients()
                self.read_inputs()
                
                if self.state != self.last_state:
                    self.print_active_inputs()
                    self.broadcast_input_state()
                    self.last_state = self.state.copy()
                
                current_time = time.ticks_ms()
                if time.ticks_diff(current_time, status_timer) > 10000:
                    print(f"💓 Status: {len(self.clients)} receivers")
                    status_timer = current_time
                
                time.sleep(0.02)
                
            except KeyboardInterrupt:
                print("\n👋 Controller stopped")
                break
            except Exception as e:
                print(f"❌ Error: {e}")
                time.sleep(1)

if __name__ == "__main__":
    controller = GameController()
    if hasattr(controller, 'sock'):
        controller.run()
    else:
        print("❌ Setup failed")