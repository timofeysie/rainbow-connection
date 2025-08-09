# Enhanced controller with better AP debugging
import network
import socket
import json
import time
from machine import Pin

class ControllerAccessPoint:
    def __init__(self):
        self.led = Pin(25, Pin.OUT)
        self.led.value(0)
        
        print("🎮 PicoController starting with enhanced debugging...")
        
        # Create Access Point with detailed logging
        self.ap = network.WLAN(network.AP_IF)
        
        print("📡 Activating AP interface...")
        self.ap.active(True)
        time.sleep(1)
        
        if self.ap.active():
            print("✅ AP interface is active")
        else:
            print("❌ AP interface failed to activate!")
            return
        
        # Try different configurations with more details
        configs = [
            {"essid": "PicoController", "password": "pico1234", "authmode": 3, "channel": 6},
            {"essid": "PicoController", "password": "pico1234", "authmode": 3},
            {"essid": "PicoController", "password": "pico1234"},
            {"essid": "PicoController"}  # Open network
        ]
        
        ap_success = False
        for i, config in enumerate(configs):
            try:
                print(f"🔧 Trying AP config {i+1}: {config}")
                self.ap.config(**config)
                
                # Wait a bit for config to take effect
                time.sleep(2)
                
                # Check if we can get network info
                try:
                    net_config = self.ap.ifconfig()
                    print(f"✅ Config {i+1} SUCCESS!")
                    print(f"   IP: {net_config[0]}")
                    print(f"   Netmask: {net_config[1]}")
                    print(f"   Gateway: {net_config[2]}")
                    print(f"   DNS: {net_config[3]}")
                    ap_success = True
                    self.final_config = config
                    break
                except Exception as e:
                    print(f"❌ Config {i+1} failed to get network info: {e}")
                    
            except Exception as e:
                print(f"❌ Config {i+1} failed: {e}")
        
        if not ap_success:
            print("❌ ALL AP configurations failed!")
            self.blink_error()
            return
        
        # Additional AP status checks
        print(f"\n📊 Final AP Status:")
        print(f"   Active: {self.ap.active()}")
        try:
            status = self.ap.status()
            print(f"   Status code: {status}")
        except:
            print("   Status: Unknown")
        
        # Wait longer for AP to fully initialize
        print("⏳ Waiting for AP to fully initialize...")
        for i in range(10):
            time.sleep(1)
            print(f"   {i+1}/10 seconds...")
            
            # Blink LED to show we're alive
            self.led.value(1)
            time.sleep(0.1)
            self.led.value(0)
        
        print(f"🎯 Access Point should now be broadcasting!")
        print(f"   Network Name: {self.final_config['essid']}")
        if 'password' in self.final_config:
            print(f"   Password: {self.final_config['password']}")
            print(f"   Security: WPA2")
        else:
            print(f"   Security: OPEN (no password)")
        
        # Create UDP server
        try:
            self.sock = socket.socket(socket.AF_INET, socket.SOCK_DGRAM)
            self.sock.bind(('', 8888))
            self.sock.settimeout(0.01)
            print("✅ UDP server started on port 8888")
        except Exception as e:
            print(f"❌ UDP server failed: {e}")
            return
        
        # Initialize state
        self.state = {
            'joystick': {'up': False, 'down': False, 'left': False, 'right': False, 'center': False},
            'buttons': {'A': False, 'B': False},
            'timestamp': 0
        }
        
        self.clients = set()
        
        print("🚀 Controller ready and waiting for clients!")
        print("📱 Check your other device for 'PicoController' WiFi network")
        
        # Success pattern - 3 long blinks
        for _ in range(3):
            self.led.value(1)
            time.sleep(0.5)
            self.led.value(0)
            time.sleep(0.3)
    
    def blink_error(self):
        """SOS error pattern"""
        # S-O-S pattern
        for _ in range(3):
            self.led.value(1)
            time.sleep(0.2)
            self.led.value(0)
            time.sleep(0.2)
        for _ in range(3):
            self.led.value(1)
            time.sleep(0.6)
            self.led.value(0)
            time.sleep(0.2)
        for _ in range(3):
            self.led.value(1)
            time.sleep(0.2)
            self.led.value(0)
            time.sleep(0.2)
    
    def check_for_clients(self):
        """Check for new clients with logging"""
        try:
            data, addr = self.sock.recvfrom(1024)
            message = data.decode()
            
            if message == "DISCOVER_CONTROLLER":
                if addr not in self.clients:
                    print(f"🎉 NEW CLIENT CONNECTED: {addr[0]}")
                    # Happy blinks
                    for _ in range(5):
                        self.led.value(1)
                        time.sleep(0.1)
                        self.led.value(0)
                        time.sleep(0.1)
                
                self.clients.add(addr)
                self.sock.sendto(b"CONTROLLER_FOUND", addr)
                print(f"📤 Sent acknowledgment to {addr[0]}")
                
        except OSError:
            pass  # Timeout - normal
        except Exception as e:
            print(f"❌ Client check error: {e}")
    
    def run(self):
        """Main loop with periodic status"""
        print("🔄 Starting main controller loop...")
        
        last_status = 0
        
        while True:
            try:
                # Check for clients
                self.check_for_clients()
                
                # Periodic status update
                current_time = time.ticks_ms()
                if time.ticks_diff(current_time, last_status) > 30000:  # Every 30 seconds
                    print(f"💓 Status: {len(self.clients)} clients connected")
                    print(f"   AP Active: {self.ap.active()}")
                    try:
                        net_config = self.ap.ifconfig()
                        print(f"   IP: {net_config[0]}")
                    except:
                        print(f"   IP: Error getting IP")
                    
                    last_status = current_time
                    
                    # Heartbeat blink
                    self.led.value(1)
                    time.sleep(0.05)
                    self.led.value(0)
                
                time.sleep(0.1)
                
            except KeyboardInterrupt:
                print("\n👋 Controller stopped by user")
                break
            except Exception as e:
                print(f"❌ Main loop error: {e}")
                time.sleep(1)

if __name__ == "__main__":
    controller = ControllerAccessPoint()
    controller.run() 