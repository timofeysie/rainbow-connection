# Simple gamepad receiver - no special libraries needed
import network
import socket
import json
import time
from machine import Pin

class GamepadReceiver:
    def __init__(self):
        self.wlan = network.WLAN(network.STA_IF)
        self.server_port = 8888
        
        # Connect to WiFi - UPDATE THESE WITH YOUR ACTUAL WIFI CREDENTIALS
        if self.connect_wifi("YOUR_ACTUAL_WIFI_SSID", "YOUR_ACTUAL_WIFI_PASSWORD"):
            print(f"Receiver IP: {self.wlan.ifconfig()[0]}")
            print("Configure your controller to send to this IP")
            
            # Create UDP server socket
            self.sock = socket.socket(socket.AF_INET, socket.SOCK_DGRAM)
            self.sock.bind(('', self.server_port))
            # Fix the timeout issue - use settimeout method properly
            try:
                self.sock.settimeout(0.1)
            except:
                print("Note: Socket timeout not supported, using blocking mode")
            
            # Status LED
            self.led = Pin(25, Pin.OUT)
            
            # Gamepad state
            self.gamepad_state = None
            self.last_update = 0
            
            self.socket_ready = True
        else:
            print("WiFi connection failed! Check your credentials.")
            self.socket_ready = False
    
    def connect_wifi(self, ssid, password):
        """Connect to WiFi with WPA2 compatibility mode"""
        if ssid == "YOUR_ACTUAL_WIFI_SSID" or password == "YOUR_ACTUAL_WIFI_PASSWORD":
            print("ERROR: Please update WiFi credentials in the code!")
            return False
            
        self.wlan.active(True)
        
        # Disconnect if already connected
        if self.wlan.isconnected():
            self.wlan.disconnect()
            time.sleep(2)
        
        # Get network info
        print(f"Looking for network: '{ssid}'")
        networks = self.wlan.scan()
        target_network = None
        
        for net in networks:
            net_ssid = net[0].decode('utf-8')
            if net_ssid == ssid:
                target_network = net
                break
        
        if target_network:
            authmode = target_network[4]
            rssi = target_network[3]
            channel = target_network[2]
            
            print(f"Network found:")
            print(f"  Signal: {rssi} dBm (good: > -70)")
            print(f"  Channel: {channel} (2.4GHz: 1-14)")
            print(f"  Auth mode: {authmode}")
            
            if authmode == 5:
                print("⚠️  Auth mode 5 detected (likely WPA3)")
                print("   Pico W may have limited WPA3 support")
                print("   Trying compatibility mode...")
        
        # Try multiple connection methods
        connection_methods = [
            ("Standard", lambda: self.wlan.connect(ssid, password)),
            ("With auth hint", lambda: self.wlan.connect(ssid, password, 0)),  # Force auth mode
        ]
        
        for method_name, connect_func in connection_methods:
            print(f"\nTrying {method_name} connection...")
            
            try:
                connect_func()
            except Exception as e:
                print(f"Connection method failed: {e}")
                continue
            
            # Wait for connection with detailed status
            timeout = 25
            for i in range(timeout):
                if self.wlan.isconnected():
                    print(f"\n✅ Connected with {method_name}!")
                    config = self.wlan.ifconfig()
                    print(f"  IP: {config[0]}")
                    print(f"  Gateway: {config[2]}")
                    return True
                
                status = self.wlan.status()
                if i % 5 == 0:
                    print(f"\n  Status {i}s: {status}", end="")
                else:
                    print(".", end="")
                
                # Check for definitive failures
                if status in [-2, -3] and i > 10:
                    print(f"\n  Method failed (status {status})")
                    break
                    
                time.sleep(1)
            
            # Disconnect before trying next method
            self.wlan.disconnect()
            time.sleep(2)
        
        print(f"\n❌ All connection methods failed")
        print("\n💡 SOLUTIONS:")
        print("1. Router Settings (BEST):")
        print("   - Log into your router admin panel")
        print("   - Find WiFi security settings")
        print("   - Change 'Lucienne Home' from WPA3 to WPA2-PSK")
        print("   - Or create a new 2.4GHz network with WPA2")
        print()
        print("2. Alternative Networks:")
        print("   - Try connecting to a mobile hotspot first")
        print("   - Use a different WiFi network with WPA2")
        print()
        print("3. Check if you have a guest network (often WPA2)")
        
        return False
    
    def receive_data(self):
        """Receive data with better error handling"""
        if not self.socket_ready:
            return None
            
        try:
            data, addr = self.sock.recvfrom(1024)
            self.gamepad_state = json.loads(data.decode())
            self.last_update = time.ticks_ms()
            
            # Blink LED to show activity
            self.led.value(1)
            time.sleep_ms(10)
            self.led.value(0)
            
            return self.gamepad_state
            
        except OSError as e:
            # Handle timeout and other socket errors
            if e.errno == 11:  # EAGAIN - would block (timeout)
                return None
            else:
                print(f"Socket error: {e}")
                return None
        except json.JSONDecodeError:
            print("Received invalid JSON data")
            return None
        except Exception as e:
            print(f"Unexpected receive error: {e}")
            return None
    
    def is_pressed(self, input_type, input_name):
        """Check if button/joystick direction is pressed"""
        if self.gamepad_state and input_type in self.gamepad_state:
            return self.gamepad_state[input_type].get(input_name, False)
        return False
    
    def run(self):
        """Main receiver loop"""
        if not self.socket_ready:
            print("Cannot start receiver - network not ready")
            return
            
        print(f"🎮 Gamepad receiver listening on port {self.server_port}")
        print("Waiting for controller data...")
        print("Press Ctrl+C to stop")
        
        try:
            while True:
                data = self.receive_data()
                
                if data:
                    # Print active inputs
                    active = []
                    
                    # Check joystick inputs
                    if 'joystick' in data:
                        for direction, pressed in data['joystick'].items():
                            if pressed:
                                active.append(f"Joy-{direction}")
                    
                    # Check button inputs
                    if 'buttons' in data:
                        for button, pressed in data['buttons'].items():
                            if pressed:
                                active.append(f"Btn-{button}")
                    
                    if active:
                        print(f"📍 Input: {', '.join(active)}")
                    
                    # Example usage - you can customize this:
                    if self.is_pressed('buttons', 'A'):
                        print("🅰️  A button action!")
                    if self.is_pressed('buttons', 'B'):
                        print("🅱️  B button action!")
                    if self.is_pressed('joystick', 'up'):
                        print("⬆️  Moving up!")
                    if self.is_pressed('joystick', 'down'):
                        print("⬇️  Moving down!")
                    if self.is_pressed('joystick', 'left'):
                        print("⬅️  Moving left!")
                    if self.is_pressed('joystick', 'right'):
                        print("➡️  Moving right!")
                    if self.is_pressed('joystick', 'center'):
                        print("🎯 Center button pressed!")
                
                # Check for controller timeout
                if self.gamepad_state and time.ticks_diff(time.ticks_ms(), self.last_update) > 2000:
                    print("⚠️  Controller disconnected (timeout)")
                    self.gamepad_state = None
                
                time.sleep(0.01)  # Small delay to prevent busy waiting
                
        except KeyboardInterrupt:
            print("\n👋 Receiver stopped by user")
        except Exception as e:
            print(f"❌ Receiver error: {e}")
        finally:
            if hasattr(self, 'sock'):
                self.sock.close()
            print("🔌 Socket closed")

# Simple test to check network connectivity
def test_network():
    """Test network connectivity without starting the full receiver"""
    print("=== Network Test ===")
    wlan = network.WLAN(network.STA_IF)
    wlan.active(True)
    
    print("Scanning for available networks...")
    networks = wlan.scan()
    
    print("Available WiFi networks:")
    for net in networks:
        ssid = net[0].decode('utf-8')
        print(f"  - {ssid}")
    
    print("\nUpdate your WiFi credentials in the code and try again!")

if __name__ == "__main__":
    # Uncomment the next line to scan for available WiFi networks first
    # test_network()
    
    # Run the receiver
    receiver = GamepadReceiver()
    receiver.run()