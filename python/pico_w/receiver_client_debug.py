# Enhanced receiver with network scanning details
import network
import socket
import json
import time
from machine import Pin

class ReceiverClient:
    def __init__(self):
        self.wlan = network.WLAN(network.STA_IF)
        self.wlan.active(True)
        self.led = Pin(25, Pin.OUT)
        
        controller_ssid = "PicoController"
        controller_password = "pico1234"
        
        print(f"🔍 Enhanced receiver starting...")
        print(f"Looking for: '{controller_ssid}'")
        
        # Detailed network scan
        if self.scan_and_connect(controller_ssid, controller_password):
            print("✅ Connected to controller!")
            self.setup_client()
            self.ready = True
        else:
            print("❌ Could not connect to controller")
            self.ready = False
    
    def scan_and_connect(self, target_ssid, password):
        """Enhanced network scanning and connection"""
        
        for attempt in range(3):  # Try 3 times
            print(f"\n🔍 Network scan attempt {attempt + 1}/3...")
            
            try:
                networks = self.wlan.scan()
                print(f"Found {len(networks)} networks:")
                
                target_found = False
                
                for i, net in enumerate(networks):
                    ssid = net[0].decode('utf-8') if net[0] else "Hidden"
                    bssid = ':'.join(['%02x' % b for b in net[1]])
                    channel = net[2]
                    rssi = net[3]
                    authmode = net[4]
                    hidden = net[5]
                    
                    print(f"  {i+1:2d}. SSID: '{ssid}'")
                    print(f"      RSSI: {rssi} dBm")
                    print(f"      Channel: {channel}")
                    print(f"      Auth: {authmode} ({'Open' if authmode == 0 else 'Secured'})")
                    print(f"      Hidden: {hidden}")
                    print(f"      BSSID: {bssid}")
                    
                    if ssid == target_ssid:
                        target_found = True
                        print(f"  ✅ FOUND TARGET NETWORK!")
                        
                        # Try to connect
                        print(f"\n🔗 Attempting connection to '{target_ssid}'...")
                        
                        # Disconnect first if connected
                        if self.wlan.isconnected():
                            self.wlan.disconnect()
                            time.sleep(2)
                        
                        # Try connection with and without password
                        connection_methods = []
                        if authmode == 0:  # Open network
                            connection_methods.append(("Open", lambda: self.wlan.connect(target_ssid)))
                        else:  # Secured network
                            connection_methods.extend([
                                ("With password", lambda: self.wlan.connect(target_ssid, password)),
                                ("Without password", lambda: self.wlan.connect(target_ssid))
                            ])
                        
                        for method_name, connect_func in connection_methods:
                            print(f"   Trying: {method_name}")
                            
                            try:
                                connect_func()
                                
                                # Wait for connection
                                timeout = 15
                                for i in range(timeout):
                                    if self.wlan.isconnected():
                                        print(f"   ✅ Connected with {method_name}!")
                                        config = self.wlan.ifconfig()
                                        print(f"   IP: {config[0]}")
                                        print(f"   Gateway: {config[2]}")
                                        return True
                                    
                                    status = self.wlan.status()
                                    if i % 3 == 0:
                                        print(f"   Status: {status} ({i+1}s)")
                                    
                                    time.sleep(1)
                                
                                print(f"   ❌ {method_name} timed out")
                                
                            except Exception as e:
                                print(f"   ❌ {method_name} failed: {e}")
                    
                    print()  # Blank line between networks
                
                if not target_found:
                    print(f"❌ Target network '{target_ssid}' not found in scan")
                    print("💡 Make sure:")
                    print("   1. Controller Pico W is running")
                    print("   2. Controller is nearby (< 10 feet)")
                    print("   3. No interference from other devices")
                
                # Wait before retry
                if attempt < 2:
                    print(f"⏳ Waiting 5 seconds before retry...")
                    time.sleep(5)
                
            except Exception as e:
                print(f"❌ Scan attempt {attempt + 1} failed: {e}")
                time.sleep(2)
        
        return False
    
    def setup_client(self):
        """Setup UDP client"""
        self.sock = socket.socket(socket.AF_INET, socket.SOCK_DGRAM)
        self.controller_ip = "192.168.4.1"  # Default AP IP
        self.controller_port = 8888
        
        # Discover controller
        self.discover_controller()
        
        self.gamepad_state = None
        self.last_update = 0
    
    def discover_controller(self):
        """Discover controller"""
        print("📢 Announcing to controller...")
        
        for attempt in range(5):
            try:
                print(f"   Attempt {attempt + 1}/5...")
                self.sock.sendto(b"DISCOVER_CONTROLLER", (self.controller_ip, self.controller_port))
                
                self.sock.settimeout(3)
                response, addr = self.sock.recvfrom(1024)
                
                if response == b"CONTROLLER_FOUND":
                    print(f"✅ Controller responded from {addr[0]}!")
                    self.sock.settimeout(0.1)
                    return True
                    
            except Exception as e:
                print(f"   Discovery attempt {attempt + 1} failed: {e}")
                time.sleep(1)
        
        print("⚠️ Controller didn't respond, but continuing...")
        self.sock.settimeout(0.1)
        return False
    
    def run(self):
        """Main receiver loop"""
        if not self.ready:
            return
            
        print("🎮 Receiver ready! Waiting for controller input...")
        
        while True:
            try:
                # Just show we're alive for now
                self.led.value(1)
                time.sleep(0.1)
                self.led.value(0)
                time.sleep(2)
                
            except KeyboardInterrupt:
                print("\n👋 Receiver stopped")
                break

if __name__ == "__main__":
    receiver = ReceiverClient()
    receiver.run() 