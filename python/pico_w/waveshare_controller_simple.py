# Simple Waveshare 1.8" LCD + Joystick Controller for Pico W
# Uses only built-in MicroPython libraries

import machine
import time
import json
import network
import socket
from machine import Pin, SPI
import framebuf

# Pin definitions for Waveshare 1.8" LCD module
# These are typical pins - adjust based on your module's actual pinout
LCD_DC = Pin(8, Pin.OUT)
LCD_CS = Pin(9, Pin.OUT)
LCD_RST = Pin(12, Pin.OUT)
LCD_BL = Pin(13, Pin.OUT)  # Backlight

# Joystick pins (5-way joystick)
JOYSTICK_UP = Pin(2, Pin.IN, Pin.PULL_UP)
JOYSTICK_DOWN = Pin(18, Pin.IN, Pin.PULL_UP)
JOYSTICK_LEFT = Pin(16, Pin.IN, Pin.PULL_UP)
JOYSTICK_RIGHT = Pin(20, Pin.IN, Pin.PULL_UP)
JOYSTICK_CENTER = Pin(3, Pin.IN, Pin.PULL_UP)

# Button pins (adjust based on your module)
BUTTON_A = Pin(15, Pin.IN, Pin.PULL_UP)
BUTTON_B = Pin(17, Pin.IN, Pin.PULL_UP)

class SimpleDisplay:
    """Simple display driver using basic SPI and framebuf"""
    
    def __init__(self):
        # Initialize SPI
        self.spi = SPI(1, baudrate=10000000, sck=Pin(10), mosi=Pin(11))
        
        # Initialize control pins
        LCD_CS.value(1)
        LCD_DC.value(0)
        LCD_RST.value(1)
        LCD_BL.value(1)  # Turn on backlight
        
        # Simple 128x160 buffer (you might need to adjust size)
        self.width = 128
        self.height = 160
        self.buffer = bytearray(self.width * self.height // 8)  # 1-bit buffer for simplicity
        self.framebuf = framebuf.FrameBuffer(self.buffer, self.width, self.height, framebuf.MONO_HLSB)
        
        self.init_display()
    
    def init_display(self):
        """Basic display initialization"""
        # Reset sequence
        LCD_RST.value(0)
        time.sleep_ms(10)
        LCD_RST.value(1)
        time.sleep_ms(10)
        
        print("Display initialized (basic mode)")
    
    def clear(self):
        """Clear the display buffer"""
        self.framebuf.fill(0)
    
    def text(self, text, x, y):
        """Draw text at position"""
        self.framebuf.text(text, x, y, 1)
    
    def show(self):
        """Update display (placeholder - would need proper ST7735 commands)"""
        # This is simplified - actual ST7735 would need proper command sequence
        print("Display updated (console mode)")

class GameController:
    def __init__(self):
        # Try to initialize display, but continue without it if it fails
        try:
            self.display = SimpleDisplay()
            self.has_display = True
        except Exception as e:
            print(f"Display init failed, continuing without display: {e}")
            self.has_display = False
        
        # Controller state
        self.state = {
            'joystick': {'up': False, 'down': False, 'left': False, 'right': False, 'center': False},
            'buttons': {'A': False, 'B': False},
            'timestamp': 0
        }
        
        # Network setup
        self.wlan = network.WLAN(network.STA_IF)
        self.target_ip = "192.168.1.100"  # Change to your receiver Pico W IP
        self.target_port = 8888
        
        # Connect to WiFi
        self.connect_wifi("YOUR_WIFI_SSID", "YOUR_WIFI_PASSWORD")
        
        # Create UDP socket
        self.sock = socket.socket(socket.AF_INET, socket.SOCK_DGRAM)
        
        # Status LED
        self.status_led = Pin(25, Pin.OUT)  # Built-in LED
    
    def connect_wifi(self, ssid, password):
        """Connect to WiFi"""
        self.wlan.active(True)
        self.wlan.connect(ssid, password)
        
        print("Connecting to WiFi...")
        timeout = 20
        while not self.wlan.isconnected() and timeout > 0:
            time.sleep(1)
            timeout -= 1
            print(".", end="")
        
        if self.wlan.isconnected():
            print(f"\nConnected! IP: {self.wlan.ifconfig()[0]}")
            self.update_display("WiFi OK", self.wlan.ifconfig()[0])
            return True
        else:
            print("\nWiFi connection failed!")
            return False
    
    def read_inputs(self):
        """Read all controller inputs"""
        # Read digital joystick (active low)
        self.state['joystick']['up'] = not JOYSTICK_UP.value()
        self.state['joystick']['down'] = not JOYSTICK_DOWN.value()
        self.state['joystick']['left'] = not JOYSTICK_LEFT.value()
        self.state['joystick']['right'] = not JOYSTICK_RIGHT.value()
        self.state['joystick']['center'] = not JOYSTICK_CENTER.value()
        
        # Read buttons (active low)
        self.state['buttons']['A'] = not BUTTON_A.value()
        self.state['buttons']['B'] = not BUTTON_B.value()
        
        self.state['timestamp'] = time.ticks_ms()
    
    def send_state(self):
        """Send controller state via UDP"""
        try:
            message = json.dumps(self.state)
            self.sock.sendto(message.encode(), (self.target_ip, self.target_port))
            
            # Blink LED on successful send
            self.status_led.value(1)
            time.sleep_ms(10)
            self.status_led.value(0)
            
            return True
        except Exception as e:
            print(f"Send error: {e}")
            return False
    
    def update_display(self, line1, line2=""):
        """Update display with status info"""
        if not self.has_display:
            print(f"Status: {line1} {line2}")
            return
        
        try:
            self.display.clear()
            self.display.text(line1, 0, 0)
            if line2:
                self.display.text(line2, 0, 20)
            
            # Show current inputs
            y_pos = 50
            active_inputs = []
            
            # Show joystick state
            for direction, pressed in self.state['joystick'].items():
                if pressed:
                    active_inputs.append(direction)
            
            if active_inputs:
                self.display.text(f"Joy: {','.join(active_inputs)}", 0, y_pos)
                y_pos += 20
            
            # Show button state
            active_buttons = []
            for button, pressed in self.state['buttons'].items():
                if pressed:
                    active_buttons.append(button)
            
            if active_buttons:
                self.display.text(f"Btn: {','.join(active_buttons)}", 0, y_pos)
            
            self.display.show()
            
        except Exception as e:
            print(f"Display error: {e}")
    
    def run(self):
        """Main controller loop"""
        print("Waveshare Controller Started!")
        print(f"Sending to: {self.target_ip}:{self.target_port}")
        print("Press Ctrl+C to stop")
        
        self.update_display("Controller", "Ready!")
        
        last_state = None
        send_failures = 0
        
        while True:
            try:
                # Read inputs
                self.read_inputs()
                
                # Only send if state changed (reduce network traffic)
                if self.state != last_state:
                    if self.send_state():
                        send_failures = 0
                        self.update_display("Active", f"Target: {self.target_ip}")
                    else:
                        send_failures += 1
                        if send_failures > 5:
                            self.update_display("Send Error", "Check network")
                    
                    last_state = self.state.copy()
                    
                    # Print to console for debugging
                    active_items = []
                    for k, v in self.state['joystick'].items():
                        if v:
                            active_items.append(f"Joy-{k}")
                    for k, v in self.state['buttons'].items():
                        if v:
                            active_items.append(f"Btn-{k}")
                    
                    if active_items:
                        print(f"Input: {', '.join(active_items)}")
                
                time.sleep(0.05)  # 20Hz update rate
                
            except KeyboardInterrupt:
                print("\nController stopped by user")
                break
            except Exception as e:
                print(f"Controller error: {e}")
                time.sleep(1)

# Simple test function to check pins without networking
def test_inputs():
    """Test function to check if your pins are working"""
    print("Testing inputs... Press Ctrl+C to stop")
    print("Pin assignments:")
    print(f"Joystick: UP={JOYSTICK_UP}, DOWN={JOYSTICK_DOWN}, LEFT={JOYSTICK_LEFT}, RIGHT={JOYSTICK_RIGHT}, CENTER={JOYSTICK_CENTER}")
    print(f"Buttons: A={BUTTON_A}, B={BUTTON_B}")
    
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
                print(f"Active: {', '.join(inputs)}")
            
            time.sleep(0.1)
            
        except KeyboardInterrupt:
            print("\nTest stopped")
            break

# Run the controller
if __name__ == "__main__":
    # Uncomment the next line to test inputs first
    # test_inputs()
    
    # Run the full controller
    controller = GameController()
    controller.run() 