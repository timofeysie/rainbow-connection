# Working receiver that connects to PicoController and receives input data
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
        
        print("🎮 Gamepad Receiver Starting...")
        
        # Connect to controller's network
        if self.connect_to_controller():
            print("✅ Connected to PicoController!")
            self.setup_udp_client()
            self.discover_controller()
            self.ready = True
        else:
            print("❌ Failed to connect to controller")
            self.ready = False
    
    def connect_to_controller(self):
        """Connect to the PicoController WiFi network"""
        controller_ssid = "PicoController"
        controller_password = "pico1234"
        
        print(f"🔍 Looking for '{controller_ssid}' network...")
        
        # Scan for networks
        networks = self.wlan.scan()
        controller_found = False
        
        for net in networks:
            ssid = net[0].decode('utf-8')
            if ssid == controller_ssid:
                controller_found = True
                rssi = net[3]
                print(f"📡 Found controller network (Signal: {rssi} dBm)")
                break
        
        if not controller_found:
            print(f"❌ Controller network '{controller_ssid}' not found!")
            print("Make sure the controller is running and nearby")
            return False
        
        # Connect to network
        print("🔗 Connecting to controller...")
        self.wlan.connect(controller_ssid, controller_password)
        
        # Wait for connection
        timeout = 15
        for i in range(timeout):
            if self.wlan.isconnected():
                config = self.wlan.ifconfig()
                print(f"✅ Connected successfully!")
                print(f"   My IP: {config[0]}")
                print(f"   Controller IP: {config[2]}")  # Gateway = controller
                return True
            
            time.sleep(1)
            if i % 3 == 0:
                print(f"   Waiting... ({i+1}s)")
        
        print("❌ Connection timeout")
        return False
    
    def setup_udp_client(self):
        """Setup UDP client for receiving data"""
        self.sock = socket.socket(socket.AF_INET, socket.SOCK_DGRAM)
        self.controller_ip = "192.168.4.1"  # Default AP IP
        self.controller_port = 8888
        
        self.gamepad_state = None
        self.last_update = 0
    
    def discover_controller(self):
        """Announce ourselves to the controller"""
        print("📢 Announcing to controller...")
        
        for attempt in range(5):
            try:
                # Send discovery message
                self.sock.sendto(b"DISCOVER_CONTROLLER", (self.controller_ip, self.controller_port))
                
                # Wait for response
                self.sock.settimeout(2)
                response, addr = self.sock.recvfrom(1024)
                
                if response == b"CONTROLLER_FOUND":
                    print(f"✅ Controller acknowledged connection!")
                    self.sock.settimeout(0.1)  # Set for normal operation
                    return True
                    
            except Exception as e:
                print(f"   Attempt {attempt + 1} failed: {e}")
                time.sleep(1)
        
        print("⚠️ Controller didn't respond, but continuing...")
        self.sock.settimeout(0.1)
        return False
    
    def receive_gamepad_data(self):
        """Receive and parse gamepad data"""
        try:
            data, addr = self.sock.recvfrom(1024)
            self.gamepad_state = json.loads(data.decode())
            self.last_update = time.ticks_ms()
            
            # Activity blink
            self.led.value(1)
            time.sleep_ms(10)
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
    
    def is_pressed(self, input_type, input_name):
        """Check if a specific input is currently pressed"""
        if self.gamepad_state and input_type in self.gamepad_state:
            return self.gamepad_state[input_type].get(input_name, False)
        return False
    
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
    
    def run(self):
        """Main receiver loop"""
        if not self.ready:
            print("❌ Receiver not ready")
            return
        
        print("🎮 Receiver ready! Waiting for controller input...")
        print("Press buttons on the controller to see data!")
        
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
                if self.gamepad_state and time.ticks_diff(time.ticks_ms(), self.last_update) > 3000:
                    print("⚠️  Controller timeout - no data received")
                    self.gamepad_state = None
                
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