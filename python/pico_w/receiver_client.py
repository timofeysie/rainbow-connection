# Receiver Pico W - Connects to controller's network
import network
import socket
import json
import time
from machine import Pin

class ReceiverClient:
    def __init__(self):
        # Connect to controller's access point
        self.wlan = network.WLAN(network.STA_IF)
        self.wlan.active(True)
        
        # Controller's network details
        controller_ssid = "PicoController"
        controller_password = "pico1234"
        
        print(f"🔍 Looking for controller network: {controller_ssid}")
        
        # Connect to controller
        if self.connect_to_controller(controller_ssid, controller_password):
            print("✅ Connected to controller!")
            
            # Set up UDP client
            self.sock = socket.socket(socket.AF_INET, socket.SOCK_DGRAM)
            self.controller_ip = "192.168.4.1"  # Default AP IP
            self.controller_port = 8888
            
            # Discover controller
            self.discover_controller()
            
            # Status
            self.led = Pin(25, Pin.OUT)
            self.gamepad_state = None
            self.last_update = 0
            
            self.ready = True
        else:
            print("❌ Could not connect to controller")
            self.ready = False
    
    def connect_to_controller(self, ssid, password):
        """Connect to controller's access point"""
        # Scan for the controller network
        print("Scanning for networks...")
        networks = self.wlan.scan()
        
        found = False
        for net in networks:
            if net[0].decode('utf-8') == ssid:
                found = True
                print(f"📡 Found controller network (Signal: {net[3]} dBm)")
                break
        
        if not found:
            print(f"❌ Controller network '{ssid}' not found!")
            print("Make sure the controller Pico W is running and nearby")
            return False
        
        # Connect
        print("Connecting to controller...")
        self.wlan.connect(ssid, password)
        
        timeout = 20
        while not self.wlan.isconnected() and timeout > 0:
            time.sleep(1)
            timeout -= 1
            print(".", end="")
        
        if self.wlan.isconnected():
            print(f"\n✅ Connected! IP: {self.wlan.ifconfig()[0]}")
            return True
        else:
            print(f"\n❌ Connection failed")
            return False
    
    def discover_controller(self):
        """Announce ourselves to the controller"""
        print("📢 Announcing to controller...")
        
        for attempt in range(5):
            try:
                # Send discovery message
                self.sock.sendto(b"DISCOVER_CONTROLLER", (self.controller_ip, self.controller_port))
                
                # Wait for acknowledgment
                self.sock.settimeout(2)
                response, addr = self.sock.recvfrom(1024)
                
                if response == b"CONTROLLER_FOUND":
                    print("🤝 Controller acknowledged!")
                    self.sock.settimeout(0.1)  # Set for normal operation
                    return True
                    
            except Exception as e:
                print(f"Discovery attempt {attempt + 1} failed: {e}")
                time.sleep(1)
        
        print("⚠️ Controller didn't respond, but continuing anyway...")
        self.sock.settimeout(0.1)
        return False
    
    def receive_data(self):
        """Receive controller data"""
        try:
            data, addr = self.sock.recvfrom(1024)
            self.gamepad_state = json.loads(data.decode())
            self.last_update = time.ticks_ms()
            
            # Blink LED
            self.led.value(1)
            time.sleep_ms(5)
            self.led.value(0)
            
            return self.gamepad_state
            
        except OSError:
            return None  # Timeout
        except Exception as e:
            print(f"Receive error: {e}")
            return None
    
    def is_pressed(self, input_type, input_name):
        """Check if input is pressed"""
        if self.gamepad_state and input_type in self.gamepad_state:
            return self.gamepad_state[input_type].get(input_name, False)
        return False
    
    def run(self):
        """Main receiver loop"""
        if not self.ready:
            return
            
        print("🎮 Receiver ready! Waiting for controller input...")
        
        while True:
            try:
                data = self.receive_data()
                
                if data:
                    # Print active inputs
                    active = []
                    for direction, pressed in data['joystick'].items():
                        if pressed: active.append(f"Joy-{direction}")
                    for button, pressed in data['buttons'].items():
                        if pressed: active.append(f"Btn-{button}")
                    
                    if active:
                        print(f"📍 Input: {', '.join(active)}")
                    
                    # Your game logic here:
                    if self.is_pressed('buttons', 'A'):
                        print("🅰️ A button action!")
                    if self.is_pressed('joystick', 'up'):
                        print("⬆️ Moving up!")
                
                # Check timeout
                if self.gamepad_state and time.ticks_diff(time.ticks_ms(), self.last_update) > 2000:
                    print("⚠️ Controller timeout")
                    self.gamepad_state = None
                
                time.sleep(0.01)
                
            except KeyboardInterrupt:
                print("\n👋 Receiver stopped")
                break
            except Exception as e:
                print(f"Receiver error: {e}")
                time.sleep(1)

if __name__ == "__main__":
    receiver = ReceiverClient()
    receiver.run() 