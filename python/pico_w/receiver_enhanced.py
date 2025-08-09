# Enhanced receiver - modified to connect to PICO3B73
import network
import socket
import json
import time
from machine import Pin

class GamepadReceiver:
    def __init__(self):
        self.led = Pin(25, Pin.OUT)
        self.wlan = network.WLAN(network.STA_IF)
        self.wlan.active(True)
        
        print("🎮 Enhanced Gamepad Receiver Starting...")
        print("=" * 45)
        
        # Connect to PICO3B73 (the actual network name)
        if self.connect_to_controller():
            print("✅ Connected to controller!")
            self.setup_udp_client()
            self.discover_controller()
            self.ready = True
        else:
            print("❌ Failed to connect to controller")
            self.ready = False
    
    def connect_to_controller(self):
        """Connect to controller network - try PicoController first"""
        # Try networks in order of preference
        network_attempts = [
            ("PicoController", "pico1234"),     # Our intended name with password
            ("PicoController", None),           # Our intended name open
            ("PICO3B73", "pico1234"),          # Fallback name with password
            ("PICO3B73", "micropythoN"),       # Fallback with default password
            ("PICO3B73", None),                # Fallback open
        ]
        
        print("🔍 Looking for controller network...")
        
        # Scan to see what's available
        networks = self.wlan.scan()
        available_networks = {}
        
        for net in networks:
            ssid = net[0].decode('utf-8')
            if ssid in ["PicoController", "PICO3B73"]:
                available_networks[ssid] = {'rssi': net[3], 'auth': net[4]}
                print(f"📡 Found '{ssid}' (Signal: {net[3]} dBm, Auth: {net[4]})")
        
        if not available_networks:
            print("❌ No controller networks found!")
            print("💡 Make sure controller is powered and main.py is saved correctly")
            return False
        
        # Try connecting to each available network
        for ssid, password in network_attempts:
            if ssid not in available_networks:
                continue  # Skip if not available
                
            print(f"\n🔗 Trying '{ssid}' with password: {'None (Open)' if password is None else repr(password)}")
            
            try:
                if self.wlan.isconnected():
                    self.wlan.disconnect()
                    time.sleep(2)
                
                if password is None:
                    self.wlan.connect(ssid)
                else:
                    self.wlan.connect(ssid, password)
                
                for i in range(15):
                    if self.wlan.isconnected():
                        config = self.wlan.ifconfig()
                        print(f"✅ Connected to '{ssid}'!")
                        print(f"   My IP: {config[0]}")
                        print(f"   Controller IP: {config[2]}")
                        return True
                    
                    time.sleep(1)
                    if i % 3 == 0:
                        print(f"   Connecting... ({i+1}s)")
                
                print(f"❌ Connection to '{ssid}' timed out")
                
            except Exception as e:
                print(f"❌ Connection to '{ssid}' failed: {e}")
        
        return False
    
    def setup_udp_client(self):
        """Setup UDP client for receiving gamepad data"""
        self.sock = socket.socket(socket.AF_INET, socket.SOCK_DGRAM)
        
        # Get the controller IP from our network config
        config = self.wlan.ifconfig()
        self.controller_ip = config[2]  # Gateway = controller IP
        self.controller_port = 8888
        
        print(f"📡 UDP client setup - Controller IP: {self.controller_ip}:8888")
        
        self.gamepad_state = None
        self.last_update = 0
    
    def discover_controller(self):
        """Announce ourselves to the controller"""
        print(f"\n📢 Announcing to controller at {self.controller_ip}...")
        
        for attempt in range(5):
            try:
                print(f"   Discovery attempt {attempt + 1}/5...")
                self.sock.sendto(b"DISCOVER_CONTROLLER", (self.controller_ip, self.controller_port))
                
                self.sock.settimeout(3)
                response, addr = self.sock.recvfrom(1024)
                
                if response == b"CONTROLLER_FOUND":
                    print(f"✅ Controller responded from {addr[0]}!")
                    self.sock.settimeout(0.1)  # Set for normal operation
                    return True
                else:
                    print(f"   Unexpected response: {response}")
                    
            except Exception as e:
                print(f"   Discovery attempt {attempt + 1} failed: {e}")
                time.sleep(1)
        
        print("⚠️ Controller didn't respond to discovery")
        print("💡 Will continue anyway - controller might still send data")
        self.sock.settimeout(0.1)
        return False
    
    def receive_gamepad_data(self):
        """Receive and parse gamepad data from controller"""
        try:
            data, addr = self.sock.recvfrom(1024)
            self.gamepad_state = json.loads(data.decode())
            self.last_update = time.ticks_ms()
            
            # Activity blink
            self.led.value(1)
            time.sleep_ms(20)
            self.led.value(0)
            
            return self.gamepad_state
            
        except OSError:
            return None  # Timeout - normal
        except json.JSONDecodeError:
            print("❌ Received invalid JSON data")
            return None
        except Exception as e:
            print(f"❌ Receive error: {e}")
            return None
    
    def print_gamepad_state(self, data):
        """Print current gamepad state"""
        active_inputs = []
        
        # Check joystick
        if 'joystick' in data:
            for direction, pressed in data['joystick'].items():
                if pressed:
                    active_inputs.append(f"Joy-{direction}")
        
        # Check buttons
        if 'buttons' in data:
            for button, pressed in data['buttons'].items():
                if pressed:
                    active_inputs.append(f"Btn-{button}")
        
        if active_inputs:
            timestamp = data.get('timestamp', 0)
            print(f"🎮 Input: {', '.join(active_inputs)} (t:{timestamp})")
    
    def is_pressed(self, input_type, input_name):
        """Check if a specific input is currently pressed"""
        if self.gamepad_state and input_type in self.gamepad_state:
            return self.gamepad_state[input_type].get(input_name, False)
        return False
    
    def run(self):
        """Main receiver loop"""
        if not self.ready:
            print("\n❌ Receiver not ready - connection failed")
            return
            
        print("\n🎮 Receiver ready! Waiting for controller input...")
        print("Press buttons and move joystick on the controller!")
        
        last_heartbeat = 0
        
        while True:
            try:
                # Receive gamepad data
                data = self.receive_gamepad_data()
                
                if data:
                    # Print received data
                    self.print_gamepad_state(data)
                    
                    # Example usage - customize this for your application:
                    if self.is_pressed('buttons', 'A'):
                        print("🅰️  A button action triggered!")
                    
                    if self.is_pressed('buttons', 'B'):
                        print("🅱️  B button action triggered!")
                    
                    if self.is_pressed('joystick', 'up'):
                        print("⬆️  Moving up!")
                    
                    if self.is_pressed('joystick', 'down'):
                        print("⬇️  Moving down!")
                    
                    if self.is_pressed('joystick', 'left'):
                        print("⬅️  Moving left!")
                    
                    if self.is_pressed('joystick', 'right'):
                        print("➡️  Moving right!")
                    
                    if self.is_pressed('joystick', 'center'):
                        print("🎯 Joystick center pressed!")
                
                # Check for controller timeout
                current_time = time.ticks_ms()
                if self.gamepad_state and time.ticks_diff(current_time, self.last_update) > 3000:
                    print("⚠️  Controller timeout - no data received")
                    self.gamepad_state = None
                
                # Heartbeat every 5 seconds
                if time.ticks_diff(current_time, last_heartbeat) > 5000:
                    print("💓 Receiver active, waiting for input...")
                    last_heartbeat = current_time
                
                time.sleep(0.01)  # Small delay
                
            except KeyboardInterrupt:
                print("\n👋 Receiver stopped")
                break
            except Exception as e:
                print(f"❌ Receiver error: {e}")
                time.sleep(1)

if __name__ == "__main__":
    receiver = GamepadReceiver()
    receiver.run() 