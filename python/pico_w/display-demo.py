from machine import Pin,SPI,PWM
import framebuf
import time

#color is BGR
RED = 0x00F8
GREEN = 0xE007
BLUE = 0x1F00
WHITE = 0xFFFF
BLACK = 0x0000

class LCD_1inch14(framebuf.FrameBuffer):
    def __init__(self):
        self.width = 240
        self.height = 135
        
        # Initialize SPI first with slower speed
        self.spi = SPI(1, baudrate=10000000, 
                      polarity=0, phase=0,
                      sck=Pin(10), mosi=Pin(11), miso=None)
        
        # Initialize pins
        self.cs = Pin(9, Pin.OUT)
        self.rst = Pin(12, Pin.OUT)
        self.dc = Pin(8, Pin.OUT)
        
        # Initialize backlight
        self.bl = Pin(13, Pin.OUT)
        self.bl.value(1)
        
        # Create the framebuffer
        self.buffer = bytearray(self.height * self.width * 2)
        super().__init__(self.buffer, self.width, self.height, framebuf.RGB565)
        
        # Initialize display
        self.init_display()
        
    def reset(self):
        self.rst.value(1)
        time.sleep(0.2)
        self.rst.value(0)
        time.sleep(0.2)
        self.rst.value(1)
        time.sleep(0.2)
        
    def write_cmd(self, cmd):
        self.cs.value(0)
        self.dc.value(0)
        self.spi.write(bytearray([cmd]))
        self.cs.value(1)
        
    def write_data(self, data):
        self.cs.value(0)
        self.dc.value(1)
        self.spi.write(bytearray([data]))
        self.cs.value(1)
        
    def init_display(self):
        """Initialize display with minimal setup"""
        self.reset()
        
        # Basic initialization sequence
        self.write_cmd(0x36)    # Memory Access Control
        self.write_data(0x70)   # RGB -> BGR, MY=1, MX=1, ML=1
        
        self.write_cmd(0x3A)    # Interface Pixel Format
        self.write_data(0x05)   # 16-bit/pixel
        
        self.write_cmd(0x21)    # Display Inversion On
        self.write_cmd(0x11)    # Sleep Out
        time.sleep(0.12)        # Wait for sleep out
        
        self.write_cmd(0x29)    # Display ON
        time.sleep(0.02)        # Wait for display on
        
    def show(self):
        self.write_cmd(0x2A)    # Column Address Set
        self.write_data(0x00)   # Start column high
        self.write_data(0x00)   # Start column low
        self.write_data(0x00)   # End column high
        self.write_data(0xEF)   # End column low
        
        self.write_cmd(0x2B)    # Row Address Set
        self.write_data(0x00)   # Start row high
        self.write_data(0x00)   # Start row low
        self.write_data(0x00)   # End row high
        self.write_data(0x85)   # End row low
        
        self.write_cmd(0x2C)    # Memory Write
        
        self.cs.value(0)
        self.dc.value(1)
        self.spi.write(self.buffer)
        self.cs.value(1)

if __name__=='__main__':
    try:
        lcd = LCD_1inch14()
        print("LCD initialized")
        
        # Clear to black
        lcd.fill(BLACK)
        lcd.show()
        print("Screen cleared to black")
        time.sleep(1)
        
        # Draw blue rectangle
        margin = 5
        rect_x = margin
        rect_y = margin
        rect_width = lcd.width - (2 * margin)
        rect_height = lcd.height - (2 * margin)
        
        lcd.fill_rect(rect_x, rect_y, rect_width, rect_height, BLUE)
        lcd.show()
        print("Blue rectangle drawn")
        
        while True:
            time.sleep(1)
            
    except Exception as e:
        print("Error:", str(e))
    
    
