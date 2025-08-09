# USB HID gamepad reader for Pico W
# This approach uses USB instead of Bluetooth

import time
import usb_hid
import struct

class USBGamepadReader:
    def __init__(self):
        self.last_report = None
    
    def read_gamepad_data(self):
        """Read HID report from USB gamepad"""
        try:
            # This is pseudocode - actual USB HID implementation
            # would need the adafruit_hid library or similar
            report = usb_hid.get_last_received_report()
            
            if report and report != self.last_report:
                self.last_report = report
                return self.parse_hid_report(report)
        except Exception as e:
            print(f"USB read error: {e}")
        
        return None
    
    def parse_hid_report(self, data):
        """Parse HID report into gamepad state"""
        if len(data) >= 8:
            return {
                'left_x': data[0],
                'left_y': data[1], 
                'right_x': data[2],
                'right_y': data[3],
                'buttons': struct.unpack('<H', data[4:6])[0],
                'dpad': data[6]
            }
        return None

def main():
    reader = USBGamepadReader()
    
    print("Connect 8BitDo Zero 2 via USB cable...")
    print("Press buttons to see input!")
    
    while True:
        gamepad_state = reader.read_gamepad_data()
        
        if gamepad_state:
            print(f"Left stick: ({gamepad_state['left_x']}, {gamepad_state['left_y']})")
            print(f"Right stick: ({gamepad_state['right_x']}, {gamepad_state['right_y']})")
            print(f"Buttons: 0x{gamepad_state['buttons']:04X}")
            print("---")
        
        time.sleep(0.05)  # 20Hz

if __name__ == "__main__":
    main() 