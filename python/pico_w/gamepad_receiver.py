# Gamepad data receiver for Pico W
# Receives controller input from Waveshare controller via WiFi

import network
import socket
import json
import time
from machine import Pin

class GamepadReceiver:
    def __init__(self):
        self.wlan = network.WLAN(network.STA_IF)
        self.server_port = 8888
        
        # Connect to WiFi
        self.connect_wifi("YOUR_WIFI_SSID", "YOUR_WIFI_PASSWORD")
        
        # Create UDP server socket
        self.sock = socket.socket(socket.AF_INET, socket.SOCK_DGRAM)
        self.sock.bind(('', self.server_port))
        self.sock.settimeout(0.1)  # Non-blocking with timeout
        
        print(f"Gamepad receiver listening on port {self.server_port}")
        print(f"Controller should send to: {self.wlan.ifconfig()[0]}:{self.server_port}")
        
        # Current gamepad state
        self.gamepad_state = None
        self.last_update = 0
        
        # Optional: LED to show activity
        self.activity_led = Pin(25, Pin.OUT)  # Built-in LED
        self.led_state = False
    
    def connect_wifi(self, ssid, password):
        """Connect to WiFi"""
        self.wlan.active(True)
        self.wlan.connect(ssid, password)
        
        print("Connecting to WiFi...")
        while not self.wlan.isconnected():
            time.sleep(1)
            print(".", end="")
        
        print(f"\nConnected! IP: {self.wlan.ifconfig()[0]}")
    
    def receive_gamepad_data(self):
        """Receive and parse gamepad data"""
        try:
            data, addr = self.sock.recvfrom(1024)
            gamepad_data = json.loads(data.decode())
            
            self.gamepad_state = gamepad_data
            self.last_update = time.ticks_ms()
            
            # Blink LED to show activity
            self.led_state = not self.led_state
            self.activity_led.value(self.led_state)
            
            return gamepad_data
            
        except socket.timeout:
            # No data received (normal)
            return None
        except Exception as e:
            print(f"Receive error: {e}")
            return None
    
    def is_button_pressed(self, button_name):
        """Check if a specific button is pressed"""
        if self.gamepad_state and 'buttons' in self.gamepad_state:
            return self.gamepad_state['buttons'].get(button_name, False)
        return False
    
    def is_joystick_direction(self, direction):
        """Check if joystick is pressed in a direction"""
        if self.gamepad_state and 'joystick' in self.gamepad_state:
            return self.gamepad_state['joystick'].get(direction, False)
        return False
    
    def get_analog_value(self, axis):
        """Get analog stick value if available"""
        if self.gamepad_state and 'analog' in self.gamepad_state:
            return self.gamepad_state['analog'].get(axis, 0)
        return 0
    
    def print_state(self):
        """Print current gamepad state"""
        if not self.gamepad_state:
            return
        
        # Print active inputs
        active_inputs = []
        
        # Check joystick
        for direction, pressed in self.gamepad_state['joystick'].items():
            if pressed:
                active_inputs.append(f"Joy-{direction}")
        
        # Check buttons
        for button, pressed in self.gamepad_state['buttons'].items():
            if pressed:
                active_inputs.append(f"Btn-{button}")
        
        if active_inputs:
            print(f"Active: {', '.join(active_inputs)}")
        
        # Check for timeout (controller disconnected)
        if time.ticks_diff(time.ticks_ms(), self.last_update) > 2000:
            print("Controller timeout - no data received")
    
    def run(self):
        """Main receiver loop"""
        print("Gamepad receiver started!")
        
        while True:
            # Receive gamepad data
            data = self.receive_gamepad_data()
            
            if data:
                self.print_state()
                
                # Example: Use the gamepad data for your application
                if self.is_button_pressed('A'):
                    print("A button pressed - do something!")
                
                if self.is_joystick_direction('up'):
                    print("Joystick up - move forward!")
                
                # Add your game/application logic here
                
            time.sleep(0.01)  # Small delay

# Run the receiver
if __name__ == "__main__":
    receiver = GamepadReceiver()
    receiver.run() 