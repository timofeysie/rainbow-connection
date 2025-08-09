# Controller with Waveshare 1.14" LCD support - Multiple pin configurations
import network
import socket
import json
import time
from machine import Pin, SPI
import framebuf

# Multiple possible pin configurations for Waveshare 1.14" LCD
LCD_CONFIGS = [
    # Config 1: Standard Waveshare pinout
    {"dc": 8, "cs": 9, "sck": 10, "mosi": 11, "rst": 12, "bl": 13},
    # Config 2: Alternative pinout
    {"dc": 6, "cs": 7, "sck": 10, "mosi": 11, "rst": 8, "bl": 9},
    # Config 3: Another common configuration  
    {"dc": 20, "cs": 17, "sck": 18, "mosi": 19, "rst": 21, "bl": 22},
]

# Input pins - adjust these for your specific module
JOYSTICK_UP = Pin(2, Pin.IN, Pin.PULL_UP)
JOYSTICK_DOWN = Pin(18, Pin.IN, Pin.PULL_UP) 
JOYSTICK_LEFT = Pin(16, Pin.IN, Pin.PULL_UP)
JOYSTICK_RIGHT = Pin(20, Pin.IN, Pin.PULL_UP)
JOYSTICK_CENTER = Pin(3, Pin.IN, Pin.PULL_UP)
BUTTON_A = Pin(15, Pin.IN, Pin.PULL_UP)
BUTTON_B = Pin(17, Pin.IN, Pin.PULL_UP)

class WaveshareLCD:
    """Simple driver for Waveshare 1.14" LCD with auto-detection"""
    
    def __init__(self):
        self.width = 240
        self.height = 135
        self.working_config = None
        
        # Colors (RGB565)
        self.BLACK = 0x0000
        self.WHITE = 0xFFFF
        self.RED = 0xF800
        self.GREEN = 0x07E0
        self.BLUE = 0x001F
        self.YELLOW = 0xFFE0
        self.CYAN = 0x07FF
        self.MAGENTA = 0xF81F
        
        # Try different pin configurations
        for i, config in enumerate(LCD_CONFIGS):
            print(f"Trying LCD config {i+1}: {config}")
            if self.try_init_config(config):
                self.working_config = config
                print(f"✅ LCD working with config {i+1}")
                break
        
        if not self.working_config:
            raise Exception("No working LCD configuration found")
        
        # Create a simple text buffer for console output
        self.text_lines = []
        self.max_lines = 16  # Lines that fit on screen
        
        # Show startup message
        self.console_print("Waveshare LCD OK", self.GREEN)
    
    def try_init_config(self, config):
        """Try to initialize LCD with given pin configuration"""
        try:
            # Initialize pins
            self.dc = Pin(config["dc"], Pin.OUT)
            self.cs = Pin(config["cs"], Pin.OUT) 
            self.rst = Pin(config["rst"], Pin.OUT)
            self.bl = Pin(config["bl"], Pin.OUT)
            
            # Initialize SPI
            self.spi = SPI(1, baudrate=40000000, 
                          sck=Pin(config["sck"]), 
                          mosi=Pin(config["mosi"]))
            
            # Reset sequence
            self.cs.value(1)
            self.rst.value(0)
            time.sleep_ms(20)
            self.rst.value(1)
            time.sleep_ms(20)
            self.bl.value(1)  # Turn on backlight
            
            # Try basic ST7789 initialization
            self.write_cmd(0x01)  # Software reset
            time.sleep_ms(150)
            
            self.write_cmd(0x11)  # Sleep out
            time.sleep_ms(50)
            
            self.write_cmd(0x3A)  # Color mode
            self.write_data(0x55)  # 16-bit
            
            self.write_cmd(0x29)  # Display on
            time.sleep_ms(50)
            
            # Test if we can write to display
            self.clear_screen(self.BLACK)
            time.sleep_ms(100)
            self.clear_screen(self.RED)
            time.sleep_ms(100)
            self.clear_screen(self.BLACK)
            
            return True
            
        except Exception as e:
            print(f"Config failed: {e}")
            return False
    
    def write_cmd(self, cmd):
        """Write command to display"""
        self.cs.value(0)
        self.dc.value(0)  # Command mode
        self.spi.write(bytes([cmd]))
        self.cs.value(1)
    
    def write_data(self, data):
        """Write data to display"""
        self.cs.value(0)
        self.dc.value(1)  # Data mode
        if isinstance(data, int):
            self.spi.write(bytes([data]))
        else:
            self.spi.write(data)
        self.cs.value(1)
    
    def clear_screen(self, color):
        """Clear entire screen with color"""
        try:
            # Set full screen window
            self.write_cmd(0x2A)  # Column address
            self.write_data(0x00)
            self.write_data(0x00)
            self.write_data(0x00)
            self.write_data(0xEF)  # 239
            
            self.write_cmd(0x2B)  # Row address
            self.write_data(0x00)
            self.write_data(0x00)
            self.write_data(0x00)
            self.write_data(0x87)  # 135
            
            self.write_cmd(0x2C)  # Memory write
            
            # Send color data
            color_bytes = bytes([color >> 8, color & 0xFF])
            for _ in range(240 * 135):
                self.write_data(color_bytes)
                
        except Exception as e:
            print(f"Clear screen error: {e}")
    
    def console_print(self, text, color=None):
        """Add text to console display"""
        if color is None:
            color = self.WHITE
        
        # Add to text buffer
        self.text_lines.append((str(text)[:30], color))
        
        # Keep only recent lines
        if len(self.text_lines) > self.max_lines:
            self.text_lines = self.text_lines[-self.max_lines:]
        
        # Update display
        self.update_console()
        
        # Also print to regular console
        print(text)
    
    def update_console(self):
        """Update the console display"""
        try:
            # Clear screen
            self.clear_screen(self.BLACK)
            
            # For now, just flash the backlight to show activity
            # (Full text rendering would require font data)
            self.bl.value(0)
            time.sleep_ms(50)
            self.bl.value(1)
            
            # Show status with colors
            if len(self.text_lines) > 0:
                last_line = self.text_lines[-1]
                if "ERROR" in last_line[0] or "FAIL" in last_line[0]:
                    self.clear_screen(self.RED)
                    time.sleep_ms(100)
                    self.clear_screen(self.BLACK)
                elif "OK" in last_line[0] or "SUCCESS" in last_line[0]:
                    self.clear_screen(self.GREEN)
                    time.sleep_ms(100)
                    self.clear_screen(self.BLACK)
                elif "NEW" in last_line[0] or "CLIENT" in last_line[0]:
                    self.clear_screen(self.BLUE)
                    time.sleep_ms(100)
                    self.clear_screen(self.BLACK)
            
        except Exception as e:
            print(f"Console update error: {e}")

class ControllerAccessPoint:
    def __init__(self):
        # Initialize status LED first
        self.led = Pin(25, Pin.OUT)
        self.led.value(0)
        
        print("🎮 PicoController with Waveshare LCD starting...")
        
        # Try to initialize LCD
        try:
            self.display = WaveshareLCD()
            self.has_display = True
            self.log = self.display.console_print
            self.log("PicoController", self.display.CYAN)
        except Exception as e:
            print(f"❌ LCD init failed: {e}")
            self.has_display = False
            self.log = print
        
        self.log("Starting AP...")
        
        # Create Access Point
        self.ap = network.WLAN(network.AP_IF)
        self.ap.active(True)
        self.log("AP interface ON")
        
        # Configure AP
        ap_success = False
        configs = [
            {"essid": "PicoController", "password": "pico1234", "authmode": 3},
            {"essid": "PicoController", "password": "pico1234"},
            {"essid": "PicoController"}
        ]
        
        for i, config in enumerate(configs):
            try:
                self.ap.config(**config)
                if "password" in config:
                    self.log("AP: WPA2 mode")
                else:
                    self.log("AP: OPEN mode")
                ap_success = True
                break
            except Exception as e:
                self.log(f"Config {i+1} FAIL")
        
        if not ap_success:
            self.log("AP CONFIG FAILED!")
            return
        
        time.sleep(2)
        
        # Get IP
        try:
            ip = self.ap.ifconfig()[0]
            self.log(f"IP: {ip}")
        except:
            self.log("IP: Unknown")
            ip = "Unknown"
        
        # Create UDP server
        try:
            self.sock = socket.socket(socket.AF_INET, socket.SOCK_DGRAM)
            self.sock.bind(('', 8888))
            self.sock.settimeout(0.01)
            self.log("UDP: Port 8888")
        except Exception as e:
            self.log("UDP FAILED!")
            return
        
        # Initialize state
        self.state = {
            'joystick': {'up': False, 'down': False, 'left': False, 'right': False, 'center': False},
            'buttons': {'A': False, 'B': False},
            'timestamp': 0
        }
        
        self.clients = set()
        self.log("READY!")
        self.log("Waiting clients...")
    
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
        """Send state to clients"""
        if not self.clients:
            return
        
        message = json.dumps(self.state).encode()
        dead_clients = set()
        
        for client_addr in self.clients:
            try:
                self.sock.sendto(message, client_addr)
            except Exception:
                dead_clients.add(client_addr)
        
        self.clients -= dead_clients
        
        if self.clients:
            self.led.value(1)
            time.sleep_ms(5)
            self.led.value(0)
    
    def check_for_clients(self):
        """Check for new clients"""
        try:
            data, addr = self.sock.recvfrom(1024)
            message = data.decode()
            
            if message == "DISCOVER_CONTROLLER":
                if addr not in self.clients:
                    self.log(f"NEW CLIENT: {addr[0]}")
                
                self.clients.add(addr)
                self.sock.sendto(b"CONTROLLER_FOUND", addr)
                
        except OSError:
            pass
        except Exception as e:
            self.log(f"Client error: {str(e)[:15]}")
    
    def run(self):
        """Main loop"""
        self.log("CONTROLLER RUNNING")
        
        last_state = None
        status_timer = 0
        
        while True:
            try:
                # Check for clients
                self.check_for_clients()
                
                # Read inputs
                self.read_inputs()
                
                # Send if changed
                if self.state != last_state:
                    self.broadcast_state()
                    last_state = self.state.copy()
                    
                    # Show active inputs
                    active = []
                    for k, v in self.state['joystick'].items():
                        if v: active.append(f"J-{k[0]}")
                    for k, v in self.state['buttons'].items():
                        if v: active.append(f"B-{k}")
                    
                    if active:
                        self.log(f"Input: {','.join(active)}")
                
                # Status update every 10 seconds
                current_time = time.ticks_ms()
                if time.ticks_diff(current_time, status_timer) > 10000:
                    self.log(f"Status: {len(self.clients)} clients")
                    status_timer = current_time
                
                time.sleep(0.02)
                
            except KeyboardInterrupt:
                self.log("STOPPED")
                break
            except Exception as e:
                self.log(f"ERROR: {str(e)[:15]}")
                time.sleep(1)

# Test display only
def test_display_only():
    """Test just the display"""
    print("=== Display Test ===")
    try:
        display = WaveshareLCD()
        
        colors = [display.RED, display.GREEN, display.BLUE, display.YELLOW, display.CYAN]
        color_names = ["RED", "GREEN", "BLUE", "YELLOW", "CYAN"]
        
        for color, name in zip(colors, color_names):
            display.console_print(f"Testing {name}")
            display.clear_screen(color)
            time.sleep(1)
        
        display.console_print("Display test complete!")
        
    except Exception as e:
        print(f"Display test failed: {e}")

if __name__ == "__main__":
    # CHOOSE ONE:
    
    # Test display only
    # test_display_only()
    
    # Run full controller
    controller = ControllerAccessPoint()
    controller.run() 