# Controller Pico W with Waveshare 1.14" LCD - Creates its own WiFi network
import network
import socket
import json
import time
from machine import Pin, SPI
import framebuf

# Pin definitions for Waveshare 1.14" LCD Module
# Adjust these based on your specific module's pinout
LCD_DC = Pin(8, Pin.OUT)
LCD_CS = Pin(9, Pin.OUT)
LCD_SCK = Pin(10)
LCD_MOSI = Pin(11)
LCD_RST = Pin(12, Pin.OUT)
LCD_BL = Pin(13, Pin.OUT)  # Backlight

# Joystick and button pins for Waveshare module
JOYSTICK_UP = Pin(2, Pin.IN, Pin.PULL_UP)
JOYSTICK_DOWN = Pin(18, Pin.IN, Pin.PULL_UP)
JOYSTICK_LEFT = Pin(16, Pin.IN, Pin.PULL_UP)
JOYSTICK_RIGHT = Pin(20, Pin.IN, Pin.PULL_UP)
JOYSTICK_CENTER = Pin(3, Pin.IN, Pin.PULL_UP)
BUTTON_A = Pin(15, Pin.IN, Pin.PULL_UP)
BUTTON_B = Pin(17, Pin.IN, Pin.PULL_UP)
BUTTON_X = Pin(19, Pin.IN, Pin.PULL_UP)
BUTTON_Y = Pin(21, Pin.IN, Pin.PULL_UP)

class ST7789Display:
    """Simple ST7789 display driver for 1.14" LCD"""
    
    def __init__(self, width=240, height=135):
        self.width = width
        self.height = height
        
        # Define colors FIRST
        self.BLACK = 0x0000
        self.WHITE = 0xFFFF
        self.RED = 0xF800
        self.GREEN = 0x07E0
        self.BLUE = 0x001F
        self.YELLOW = 0xFFE0
        self.CYAN = 0x07FF
        self.MAGENTA = 0xF81F
        
        # Initialize SPI
        self.spi = SPI(1, baudrate=40000000, sck=LCD_SCK, mosi=LCD_MOSI)
        
        # Initialize pins
        LCD_CS.value(1)
        LCD_DC.value(0)
        LCD_RST.value(1)
        LCD_BL.value(1)
        
        # Create frame buffer
        self.buffer_width = 120
        self.buffer_height = 68
        self.buffer = bytearray(self.buffer_width * self.buffer_height * 2)
        self.framebuf = framebuf.FrameBuffer(self.buffer, self.buffer_width, self.buffer_height, framebuf.RGB565)
        
        self.init_display()
        
        # Console-like display for debugging
        self.console_lines = []
        self.max_lines = 8  # How many lines fit on screen
        
        print("📺 ST7789 Display initialized")
    
    def init_display(self):
        """Initialize ST7789 display"""
        try:
            LCD_RST.value(0)
            time.sleep_ms(50)
            LCD_RST.value(1)
            time.sleep_ms(50)
            
            self.write_cmd(0x01)  # Software reset
            time.sleep_ms(150)
            
            self.write_cmd(0x11)  # Sleep out
            time.sleep_ms(50)
            
            self.write_cmd(0x3A)  # Color mode
            self.write_data(0x55)  # 16-bit color
            
            self.write_cmd(0x29)  # Display on
            time.sleep_ms(50)
            
            self.clear()
            self.show()
            
        except Exception as e:
            print(f"Display init error: {e}")
    
    def write_cmd(self, cmd):
        LCD_CS.value(0)
        LCD_DC.value(0)
        self.spi.write(bytes([cmd]))
        LCD_CS.value(1)
    
    def write_data(self, data):
        LCD_CS.value(0)
        LCD_DC.value(1)
        if isinstance(data, int):
            self.spi.write(bytes([data]))
        else:
            self.spi.write(data)
        LCD_CS.value(1)
    
    def clear(self, color=None):
        if color is None:
            color = self.BLACK
        self.framebuf.fill(color)
    
    def text(self, text, x, y, color=None):
        if color is None:
            color = self.WHITE
        self.framebuf.text(text, x, y, color)
    
    def fill_rect(self, x, y, w, h, color=None):
        if color is None:
            color = self.WHITE
        self.framebuf.fill_rect(x, y, w, h, color)
    
    def show(self):
        try:
            self.write_cmd(0x2A)  # Column address set
            self.write_data(0x00)
            self.write_data(0x28)
            self.write_data(0x00)
            self.write_data(0x28 + self.buffer_width - 1)
            
            self.write_cmd(0x2B)  # Row address set  
            self.write_data(0x00)
            self.write_data(0x35)
            self.write_data(0x00)
            self.write_data(0x35 + self.buffer_height - 1)
            
            self.write_cmd(0x2C)  # Memory write
            self.write_data(self.buffer)
            
        except Exception as e:
            print(f"Display update error: {e}")
    
    def console_print(self, message, color=None):
        """Add a line to the console display"""
        if color is None:
            color = self.WHITE
        
        # Add new line
        self.console_lines.append((str(message)[:18], color))  # Truncate long lines
        
        # Keep only recent lines
        if len(self.console_lines) > self.max_lines:
            self.console_lines = self.console_lines[-self.max_lines:]
        
        # Update display
        self.clear()
        for i, (line, line_color) in enumerate(self.console_lines):
            self.text(line, 2, i * 8 + 2, line_color)
        self.show()
        
        # Also print to regular console for debugging
        print(message)

class ControllerAccessPoint:
    def __init__(self):
        # Initialize display first
        try:
            self.display = ST7789Display()
            self.has_display = True
            self.log = self.display.console_print
        except Exception as e:
            print(f"Display init failed: {e}")
            self.has_display = False
            self.log = print  # Fallback to regular print
        
        self.log("PicoController", self.display.CYAN if self.has_display else None)
        self.log("Starting up...")
        
        # Create Access Point
        self.ap = network.WLAN(network.AP_IF)
        self.ap.active(True)
        self.log("AP interface ON", self.display.GREEN if self.has_display else None)
        
        # Configure AP with error handling
        ap_success = False
        configs = [
            {"essid": "PicoController", "password": "pico1234", "authmode": 3, "channel": 6},
            {"essid": "PicoController", "password": "pico1234"},
            {"essid": "PicoController"}
        ]
        
        for i, config in enumerate(configs):
            try:
                self.ap.config(**config)
                if "password" in config:
                    self.log(f"AP: WPA2 mode", self.display.GREEN if self.has_display else None)
                else:
                    self.log(f"AP: OPEN mode", self.display.YELLOW if self.has_display else None)
                ap_success = True
                break
            except Exception as e:
                self.log(f"Config {i+1} fail", self.display.RED if self.has_display else None)
        
        if not ap_success:
            self.log("AP CONFIG FAIL!", self.display.RED if self.has_display else None)
            return
        
        # Wait for AP to be ready
        time.sleep(2)
        
        # Get and display IP
        try:
            ip = self.ap.ifconfig()[0]
            self.log(f"IP: {ip}", self.display.CYAN if self.has_display else None)
        except:
            self.log("IP: Unknown", self.display.RED if self.has_display else None)
            ip = "Unknown"
        
        # Create UDP server
        try:
            self.sock = socket.socket(socket.AF_INET, socket.SOCK_DGRAM)
            self.sock.bind(('', 8888))
            self.sock.settimeout(0.01)
            self.log("UDP: Port 8888", self.display.GREEN if self.has_display else None)
        except Exception as e:
            self.log(f"UDP FAIL: {str(e)[:10]}", self.display.RED if self.has_display else None)
            return
        
        # Initialize state
        self.state = {
            'joystick': {'up': False, 'down': False, 'left': False, 'right': False, 'center': False},
            'buttons': {'A': False, 'B': False, 'X': False, 'Y': False},
            'timestamp': 0
        }
        
        self.led = Pin(25, Pin.OUT)
        self.clients = set()
        
        self.log("READY!", self.display.GREEN if self.has_display else None)
        self.log("Waiting clients...", self.display.WHITE if self.has_display else None)
        
        # Clear display and show status screen after setup
        time.sleep(3)
        self.show_status_screen()
    
    def show_status_screen(self):
        """Show the main status screen"""
        if not self.has_display:
            return
        
        try:
            self.display.clear()
            
            # Title
            self.display.text("PicoController", 2, 2, self.display.CYAN)
            
            # Network info
            try:
                ip = self.ap.ifconfig()[0]
                self.display.text(f"IP:{ip}", 2, 12, self.display.WHITE)
            except:
                self.display.text("IP:Unknown", 2, 12, self.display.RED)
            
            # Client count
            client_color = self.display.GREEN if self.clients else self.display.RED
            self.display.text(f"Clients:{len(self.clients)}", 2, 22, client_color)
            
            # Input area
            self.display.text("Inputs:", 2, 32, self.display.YELLOW)
            
            # Status
            status_text = "ACTIVE" if self.clients else "WAITING"
            status_color = self.display.GREEN if self.clients else self.display.YELLOW
            self.display.text(status_text, 2, 58, status_color)
            
            self.display.show()
            
        except Exception as e:
            self.log(f"Status err: {str(e)[:10]}", self.display.RED)
    
    def update_inputs_display(self):
        """Update just the input area of the display"""
        if not self.has_display:
            return
        
        try:
            # Clear input area (lines 42-56)
            self.display.fill_rect(2, 42, 116, 14, self.display.BLACK)
            
            # Show active inputs
            active = []
            for k, v in self.state['joystick'].items():
                if v:
                    active.append(k[0].upper())  # First letter: U,D,L,R,C
            for k, v in self.state['buttons'].items():
                if v:
                    active.append(k)
            
            if active:
                input_text = ','.join(active)[:18]  # Truncate if too long
                self.display.text(input_text, 2, 42, self.display.MAGENTA)
            else:
                self.display.text("none", 2, 42, self.display.WHITE)
            
            # Update client count
            self.display.fill_rect(2, 22, 116, 8, self.display.BLACK)
            client_color = self.display.GREEN if self.clients else self.display.RED
            self.display.text(f"Clients:{len(self.clients)}", 2, 22, client_color)
            
            # Update status
            self.display.fill_rect(2, 58, 116, 8, self.display.BLACK)
            status_text = "ACTIVE" if self.clients else "WAITING"
            status_color = self.display.GREEN if self.clients else self.display.YELLOW
            self.display.text(status_text, 2, 58, status_color)
            
            self.display.show()
            
        except Exception as e:
            print(f"Input display error: {e}")
    
    def read_inputs(self):
        """Read controller inputs"""
        self.state['joystick']['up'] = not JOYSTICK_UP.value()
        self.state['joystick']['down'] = not JOYSTICK_DOWN.value()
        self.state['joystick']['left'] = not JOYSTICK_LEFT.value()
        self.state['joystick']['right'] = not JOYSTICK_RIGHT.value()
        self.state['joystick']['center'] = not JOYSTICK_CENTER.value()
        self.state['buttons']['A'] = not BUTTON_A.value()
        self.state['buttons']['B'] = not BUTTON_B.value()
        self.state['buttons']['X'] = not BUTTON_X.value()
        self.state['buttons']['Y'] = not BUTTON_Y.value()
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
            except Exception as e:
                self.log(f"Send fail:{client_addr[0]}", self.display.RED if self.has_display else None)
                dead_clients.add(client_addr)
        
        self.clients -= dead_clients
        
        if self.clients:
            self.led.value(1)
            time.sleep_ms(2)
            self.led.value(0)
    
    def check_for_clients(self):
        """Check for new clients"""
        try:
            data, addr = self.sock.recvfrom(1024)
            message = data.decode()
            
            if message == "DISCOVER_CONTROLLER":
                if addr not in self.clients:
                    self.log(f"New:{addr[0]}", self.display.GREEN if self.has_display else None)
                    time.sleep(0.5)  # Show the message briefly
                
                self.clients.add(addr)
                self.sock.sendto(b"CONTROLLER_FOUND", addr)
                
        except OSError:
            pass
        except Exception as e:
            self.log(f"Client err:{str(e)[:8]}", self.display.RED if self.has_display else None)
    
    def run(self):
        """Main controller loop"""
        self.log("CONTROLLER RUNNING", self.display.GREEN if self.has_display else None)
        
        last_state = None
        last_display_update = 0
        display_mode = "status"  # "status" or "console"
        
        while True:
            try:
                # Check for clients
                self.check_for_clients()
                
                # Read inputs
                self.read_inputs()
                
                # Send data if changed
                if self.state != last_state:
                    self.broadcast_state()
                    last_state = self.state.copy()
                
                # Update display periodically
                current_time = time.ticks_ms()
                if time.ticks_diff(current_time, last_display_update) > 200:  # 5Hz
                    if display_mode == "status":
                        self.update_inputs_display()
                    last_display_update = current_time
                
                time.sleep(0.02)  # 50Hz main loop
                
            except KeyboardInterrupt:
                self.log("STOPPED", self.display.RED if self.has_display else None)
                break
            except Exception as e:
                self.log(f"ERROR:{str(e)[:10]}", self.display.RED if self.has_display else None)
                time.sleep(1)

# Test function for just AP
def test_access_point_only():
    """Test AP with display output"""
    display = ST7789Display()
    log = display.console_print
    
    log("AP Test Starting", display.CYAN)
    
    ap = network.WLAN(network.AP_IF)
    ap.active(True)
    log("AP activated", display.GREEN)
    
    try:
        ap.config(essid="PicoController", password="pico1234")
        log("Config: WPA2", display.GREEN)
    except Exception as e:
        log(f"Config fail:{str(e)[:8]}", display.RED)
        return
    
    time.sleep(3)
    
    try:
        ip = ap.ifconfig()[0]
        log(f"IP: {ip}", display.CYAN)
        log("Network visible!", display.GREEN)
        log("Check WiFi scan", display.WHITE)
        log("Ctrl+C to stop", display.YELLOW)
        
        while True:
            time.sleep(1)
            
    except KeyboardInterrupt:
        log("Test stopped", display.RED)
    except Exception as e:
        log(f"Error: {str(e)[:12]}", display.RED)

if __name__ == "__main__":
    # CHOOSE ONE:
    
    # Test just the access point
    # test_access_point_only()
    
    # Run full controller
    controller = ControllerAccessPoint()
    controller.run()