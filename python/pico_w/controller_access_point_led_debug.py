# Controller with LED-based debugging (no display needed)
import network
import socket
import json
import time
from machine import Pin

# Joystick and button pins - ADJUST THESE FOR YOUR MODULE
JOYSTICK_UP = Pin(2, Pin.IN, Pin.PULL_UP)
JOYSTICK_DOWN = Pin(18, Pin.IN, Pin.PULL_UP)
JOYSTICK_LEFT = Pin(16, Pin.IN, Pin.PULL_UP)
JOYSTICK_RIGHT = Pin(20, Pin.IN, Pin.PULL_UP)
JOYSTICK_CENTER = Pin(3, Pin.IN, Pin.PULL_UP)
BUTTON_A = Pin(15, Pin.IN, Pin.PULL_UP)
BUTTON_B = Pin(17, Pin.IN, Pin.PULL_UP)

class LEDDebugger:
    """Use built-in LED to show status"""
    
    def __init__(self):
        self.led = Pin(25, Pin.OUT)
        self.led.value(0)
    
    def blink_pattern(self, pattern, repeat=1):
        """Blink LED in pattern. 1=short, 2=long, 0=pause"""
        for _ in range(repeat):
            for duration in pattern:
                if duration == 0:
                    time.sleep(0.5)  # Pause
                elif duration == 1:
                    self.led.value(1)
                    time.sleep(0.2)  # Short blink
                    self.led.value(0)
                    time.sleep(0.2)
                elif duration == 2:
                    self.led.value(1)
                    time.sleep(0.6)  # Long blink
                    self.led.value(0)
                    time.sleep(0.2)
            time.sleep(1)  # Pause between repeats
    
    def startup_ok(self):
        """3 short blinks = startup OK"""
        self.blink_pattern([1, 1, 1])
    
    def ap_created(self):
        """2 long blinks = AP created"""
        self.blink_pattern([2, 2])
    
    def client_connected(self):
        """5 fast blinks = new client"""
        for _ in range(5):
            self.led.value(1)
            time.sleep(0.1)
            self.led.value(0)
            time.sleep(0.1)
    
    def error(self):
        """SOS pattern = error"""
        # S-O-S: ...---...
        self.blink_pattern([1, 1, 1, 0, 2, 2, 2, 0, 1, 1, 1])
    
    def heartbeat(self):
        """Quick flash for activity"""
        self.led.value(1)
        time.sleep(0.05)
        self.led.value(0)

class ControllerAccessPoint:
    def __init__(self):
        self.debug = LEDDebugger()
        
        print("🎮 PicoController Starting...")
        print("Watch the LED for status:")
        print("  3 short blinks = Startup OK")
        print("  2 long blinks = Access Point created")
        print("  5 fast blinks = Client connected")
        print("  SOS pattern = Error")
        
        # Create Access Point
        self.ap = network.WLAN(network.AP_IF)
        self.ap.active(True)
        print("✅ AP interface activated")
        
        # Try different configurations
        ap_success = False
        configs = [
            {"essid": "PicoController", "password": "pico1234", "authmode": 3},
            {"essid": "PicoController", "password": "pico1234"},
            {"essid": "PicoController"}
        ]
        
        for i, config in enumerate(configs):
            try:
                print(f"Trying config {i+1}: {config}")
                self.ap.config(**config)
                print(f"✅ AP configured with method {i+1}")
                ap_success = True
                break
            except Exception as e:
                print(f"❌ Config {i+1} failed: {e}")
        
        if not ap_success:
            print("❌ All AP configurations failed!")
            self.debug.error()
            return
        
        # Wait for AP to be ready
        time.sleep(3)
        
        # Get IP info
        try:
            config = self.ap.ifconfig()
            print(f"📡 Access Point ready!")
            print(f"   Network: PicoController")
            print(f"   IP: {config[0]}")
            print(f"   Netmask: {config[1]}")
            print(f"   Gateway: {config[2]}")
            self.debug.ap_created()
        except Exception as e:
            print(f"❌ Could not get AP info: {e}")
            self.debug.error()
            return
        
        # Create UDP server
        try:
            self.sock = socket.socket(socket.AF_INET, socket.SOCK_DGRAM)
            self.sock.bind(('', 8888))
            self.sock.settimeout(0.01)
            print("✅ UDP server started on port 8888")
        except Exception as e:
            print(f"❌ UDP server failed: {e}")
            self.debug.error()
            return
        
        # Initialize state
        self.state = {
            'joystick': {'up': False, 'down': False, 'left': False, 'right': False, 'center': False},
            'buttons': {'A': False, 'B': False},
            'timestamp': 0
        }
        
        self.clients = set()
        self.debug.startup_ok()
        
        print("🎮 Controller ready! Waiting for clients...")
        print("📱 Look for 'PicoController' WiFi network on other devices")
    
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
    
    def broadcast_state(self):
        """Send state to all clients"""
        if not self.clients:
            return
        
        message = json.dumps(self.state).encode()
        dead_clients = set()
        
        for client_addr in self.clients:
            try:
                self.sock.sendto(message, client_addr)
            except Exception as e:
                print(f"Failed to send to {client_addr}: {e}")
                dead_clients.add(client_addr)
        
        self.clients -= dead_clients
        
        if self.clients:
            self.debug.heartbeat()
    
    def check_for_clients(self):
        """Listen for client discovery"""
        try:
            data, addr = self.sock.recvfrom(1024)
            message = data.decode()
            
            if message == "DISCOVER_CONTROLLER":
                if addr not in self.clients:
                    print(f"📱 New client connected: {addr[0]}")
                    self.debug.client_connected()
                
                self.clients.add(addr)
                self.sock.sendto(b"CONTROLLER_FOUND", addr)
                
        except OSError:
            pass  # Timeout - normal
        except Exception as e:
            print(f"Client check error: {e}")
    
    def run(self):
        """Main loop"""
        print("🔄 Main loop started")
        
        last_state = None
        last_status = 0
        
        while True:
            try:
                # Check for clients
                self.check_for_clients()
                
                # Read inputs
                self.read_inputs()
                
                # Send if state changed
                if self.state != last_state:
                    self.broadcast_state()
                    last_state = self.state.copy()
                    
                    # Print active inputs
                    active = []
                    for k, v in self.state['joystick'].items():
                        if v: active.append(f"Joy-{k}")
                    for k, v in self.state['buttons'].items():
                        if v: active.append(f"Btn-{k}")
                    
                    if active:
                        print(f"📍 Input: {', '.join(active)} → {len(self.clients)} clients")
                
                # Status update every 10 seconds
                current_time = time.ticks_ms()
                if time.ticks_diff(current_time, last_status) > 10000:
                    print(f"💓 Status: {len(self.clients)} clients connected")
                    last_status = current_time
                
                time.sleep(0.02)  # 50Hz
                
            except KeyboardInterrupt:
                print("\n👋 Controller stopped by user")
                break
            except Exception as e:
                print(f"❌ Main loop error: {e}")
                self.debug.error()
                time.sleep(1)

# Simple input test
def test_inputs():
    """Test just the input pins"""
    print("=== Input Pin Test ===")
    print("Press buttons and move joystick...")
    print("Press Ctrl+C to stop")
    
    led = Pin(25, Pin.OUT)
    
    while True:
        try:
            inputs = []
            
            if not JOYSTICK_UP.value(): inputs.append("UP")
            if not JOYSTICK_DOWN.value(): inputs.append("DOWN")
            if not JOYSTICK_LEFT.value(): inputs.append("LEFT")
            if not JOYSTICK_RIGHT.value(): inputs.append("RIGHT")
            if not JOYSTICK_CENTER.value(): inputs.append("CENTER")
            if not BUTTON_A.value(): inputs.append("A")
            if not BUTTON_B.value(): inputs.append("B")
            
            if inputs:
                print(f"Active: {', '.join(inputs)}")
                led.value(1)
                time.sleep(0.1)
                led.value(0)
            
            time.sleep(0.1)
            
        except KeyboardInterrupt:
            print("\nInput test stopped")
            break

if __name__ == "__main__":
    # CHOOSE ONE:
    
    # Test inputs first
    # test_inputs()
    
    # Run controller
    controller = ControllerAccessPoint()
    controller.run() 