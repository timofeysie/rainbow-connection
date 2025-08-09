# Waveshare 1.8" LCD + Joystick Controller for Pico W
# Sends controller input to another Pico W via WiFi

import machine
import time
import json
import network
import socket
from machine import Pin, SPI, ADC
import st7735  # You'll need to install this library for the display

# Pin definitions for Waveshare 1.8" LCD module
# Adjust these based on your specific module's pinout
LCD_DC = 8
LCD_CS = 9
LCD_SCK = 10
LCD_MOSI = 11
LCD_RST = 12
LCD_BL = 13

# Joystick pins (5-way joystick)
JOYSTICK_UP = Pin(2, Pin.IN, Pin.PULL_UP)
JOYSTICK_DOWN = Pin(18, Pin.IN, Pin.PULL_UP)
JOYSTICK_LEFT = Pin(16, Pin.IN, Pin.PULL_UP)
JOYSTICK_RIGHT = Pin(20, Pin.IN, Pin.PULL_UP)
JOYSTICK_CENTER = Pin(3, Pin.IN, Pin.PULL_UP)

# Button pins
BUTTON_A = Pin(15, Pin.IN, Pin.PULL_UP)
BUTTON_B = Pin(17, Pin.IN, Pin.PULL_UP)
BUTTON_X = Pin(19, Pin.IN, Pin.PULL_UP)
BUTTON_Y = Pin(21, Pin.IN, Pin.PULL_UP)

# Analog joystick pins (if your module has analog sticks)
# ANALOG_X = ADC(Pin(26))
# ANALOG_Y = ADC(Pin(27))

class GameController:
    def __init__(self):
        # Initialize display
        self.init_display()
        
        # Controller state
        self.state = {
            'joystick': {'up': False, 'down': False, 'left': False, 'right': False, 'center': False},
            'buttons': {'A': False, 'B': False, 'X': False, 'Y': False},
            'analog': {'x': 0, 'y': 0},  # If you have analog sticks
            'timestamp': 0
        }
        
        # Network setup
        self.wlan = network.WLAN(network.STA_IF)
        self.target_ip = "192.168.1.100"  # IP of your target Pico W
        self.target_port = 8888
        
        # Connect to WiFi
        self.connect_wifi("YOUR_WIFI_SSID", "YOUR_WIFI_PASSWORD")
        
        # Create UDP socket for fast communication
        self.sock = socket.socket(socket.AF_INET, socket.SOCK_DGRAM)
        
    def init_display(self):
        """Initialize the ST7735 display"""
        try:
            # Initialize SPI
            spi = SPI(1, baudrate=40000000, sck=Pin(LCD_SCK), mosi=Pin(LCD_MOSI))
            
            # Initialize display (you'll need to install st7735 library)
            # This is pseudocode - actual initialization depends on your library
            self.display = st7735.ST7735(
                spi, cs=Pin(LCD_CS), dc=Pin(LCD_DC), 
                rst=Pin(LCD_RST), bl=Pin(LCD_BL),
                width=128, height=160
            )
            self.display.init()
            self.display.fill(st7735.BLACK)
            self.display_ready = True
        except Exception as e:
            print(f"Display init error: {e}")
            self.display_ready = False
    
    def connect_wifi(self, ssid, password):
        """Connect to WiFi"""
        self.wlan.active(True)
        self.wlan.connect(ssid, password)
        
        print("Connecting to WiFi...")
        while not self.wlan.isconnected():
            time.sleep(1)
            print(".", end="")
        
        print(f"\nConnected! IP: {self.wlan.ifconfig()[0]}")
        self.update_display_status("WiFi Connected", self.wlan.ifconfig()[0])
    
    def read_inputs(self):
        """Read all controller inputs"""
        # Read digital joystick
        self.state['joystick']['up'] = not JOYSTICK_UP.value()
        self.state['joystick']['down'] = not JOYSTICK_DOWN.value()
        self.state['joystick']['left'] = not JOYSTICK_LEFT.value()
        self.state['joystick']['right'] = not JOYSTICK_RIGHT.value()
        self.state['joystick']['center'] = not JOYSTICK_CENTER.value()
        
        # Read buttons
        self.state['buttons']['A'] = not BUTTON_A.value()
        self.state['buttons']['B'] = not BUTTON_B.value()
        self.state['buttons']['X'] = not BUTTON_X.value()
        self.state['buttons']['Y'] = not BUTTON_Y.value()
        
        # Read analog inputs if available
        # self.state['analog']['x'] = ANALOG_X.read_u16()
        # self.state['analog']['y'] = ANALOG_Y.read_u16()
        
        self.state['timestamp'] = time.ticks_ms()
    
    def send_state(self):
        """Send controller state via UDP"""
        try:
            message = json.dumps(self.state)
            self.sock.sendto(message.encode(), (self.target_ip, self.target_port))
        except Exception as e:
            print(f"Send error: {e}")
    
    def update_display_status(self, line1, line2=""):
        """Update display with status info"""
        if not self.display_ready:
            return
        
        try:
            self.display.fill(st7735.BLACK)
            self.display.text(line1, 10, 10, st7735.WHITE)
            if line2:
                self.display.text(line2, 10, 30, st7735.WHITE)
            
            # Show current input state
            y_pos = 60
            if any(self.state['joystick'].values()):
                active_directions = [k for k, v in self.state['joystick'].items() if v]
                self.display.text(f"Joy: {','.join(active_directions)}", 10, y_pos, st7735.GREEN)
                y_pos += 20
            
            if any(self.state['buttons'].values()):
                active_buttons = [k for k, v in self.state['buttons'].items() if v]
                self.display.text(f"Btn: {','.join(active_buttons)}", 10, y_pos, st7735.YELLOW)
            
        except Exception as e:
            print(f"Display error: {e}")
    
    def run(self):
        """Main controller loop"""
        print("Waveshare Controller Started!")
        self.update_display_status("Controller Ready", "Press buttons!")
        
        last_state = None
        
        while True:
            # Read inputs
            self.read_inputs()
            
            # Only send if state changed (reduce network traffic)
            if self.state != last_state:
                self.send_state()
                self.update_display_status("Controller Active", f"Target: {self.target_ip}")
                last_state = self.state.copy()
            
            time.sleep(0.05)  # 20Hz update rate

# Run the controller
if __name__ == "__main__":
    controller = GameController()
    controller.run() 