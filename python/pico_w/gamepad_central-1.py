# Modified from Rui Santos & Sara Santos - Random Nerd Tutorials
# Adapted for 8BitDo Zero 2 Bluetooth gamepad connection

from micropython import const
import uasyncio as asyncio
import aioble
import bluetooth
import struct

# HID Service UUID (Human Interface Device)
_HID_SERVICE_UUID = bluetooth.UUID(0x1812)
# HID Report Characteristic UUID
_HID_REPORT_UUID = bluetooth.UUID(0x2A4D)
# HID Report Map Characteristic UUID
_HID_REPORT_MAP_UUID = bluetooth.UUID(0x2A4B)

# Name patterns for 8BitDo Zero 2 gamepad (it might appear with different names)
gamepad_names = ["8BitDo Zero 2", "Zero 2", "8BitDo"]

class GamepadState:
    def __init__(self):
        self.left_stick_x = 128  # Center position (0-255)
        self.left_stick_y = 128
        self.right_stick_x = 128
        self.right_stick_y = 128
        self.buttons = 0  # Bitmask for buttons
        self.dpad = 0     # D-pad state
    
    def update_from_report(self, data):
        """Update gamepad state from HID report data"""
        if len(data) >= 8:  # Typical gamepad report length
            # Parse the HID report (format may vary)
            # This is a common format for many gamepads
            self.left_stick_x = data[0] if len(data) > 0 else 128
            self.left_stick_y = data[1] if len(data) > 1 else 128
            self.right_stick_x = data[2] if len(data) > 2 else 128
            self.right_stick_y = data[3] if len(data) > 3 else 128
            
            # Button data (may be in bytes 4-7)
            if len(data) > 4:
                self.buttons = struct.unpack("<H", data[4:6])[0] if len(data) >= 6 else data[4]
            if len(data) > 6:
                self.dpad = data[6]
    
    def get_button_state(self, button_bit):
        """Check if a specific button is pressed"""
        return bool(self.buttons & (1 << button_bit))
    
    def get_stick_position(self, stick):
        """Get normalized stick position (-1.0 to 1.0)"""
        if stick == 'left_x':
            return (self.left_stick_x - 128) / 128.0
        elif stick == 'left_y':
            return (self.left_stick_y - 128) / 128.0
        elif stick == 'right_x':
            return (self.right_stick_x - 128) / 128.0
        elif stick == 'right_y':
            return (self.right_stick_y - 128) / 128.0
        return 0.0
    
    def print_state(self):
        """Print current gamepad state"""
        print(f"Left Stick: ({self.get_stick_position('left_x'):.2f}, {self.get_stick_position('left_y'):.2f})")
        print(f"Right Stick: ({self.get_stick_position('right_x'):.2f}, {self.get_stick_position('right_y'):.2f})")
        print(f"Buttons: 0x{self.buttons:04X}")
        
        # Common button mappings (bit positions may vary)
        button_names = ['A', 'B', 'X', 'Y', 'L1', 'R1', 'L2', 'R2', 
                       'Select', 'Start', 'L3', 'R3']
        pressed_buttons = []
        for i, name in enumerate(button_names):
            if self.get_button_state(i):
                pressed_buttons.append(name)
        
        if pressed_buttons:
            print(f"Pressed: {', '.join(pressed_buttons)}")

async def find_gamepad():
    """Scan for 8BitDo Zero 2 gamepad"""
    print("Scanning for 8BitDo Zero 2 gamepad...")
    # Scan for 10 seconds with active scanning
    async with aioble.scan(10000, interval_us=30000, window_us=30000, active=True) as scanner:
        async for result in scanner:
            device_name = result.name()
            print(f"Found device: {device_name}")
            
            # Check if it matches any of our gamepad name patterns
            if device_name:
                for pattern in gamepad_names:
                    if pattern.lower() in device_name.lower():
                        print(f"Found matching gamepad: {device_name}")
                        # Check if it has HID service
                        if _HID_SERVICE_UUID in result.services():
                            print("Device has HID service")
                            return result.device
                        else:
                            print("Device found but no HID service detected")
    return None

async def main():
    gamepad_state = GamepadState()
    
    while True:
        device = await find_gamepad()
        if not device:
            print("8BitDo Zero 2 gamepad not found. Retrying...")
            await asyncio.sleep_ms(5000)
            continue

        try:
            print("Connecting to gamepad:", device)
            connection = await device.connect()
            print("Connected successfully!")
        except asyncio.TimeoutError:
            print("Timeout during connection. Retrying...")
            await asyncio.sleep_ms(5000)
            continue
        except Exception as e:
            print("Connection error:", e)
            await asyncio.sleep_ms(5000)
            continue

        async with connection:
            try:
                print("Discovering HID service...")
                hid_service = await connection.service(_HID_SERVICE_UUID)
                print("HID service found")
                
                # Get HID report characteristic
                report_characteristic = await hid_service.characteristic(_HID_REPORT_UUID)
                print("HID report characteristic found")
                
                # Try to get report map for debugging
                try:
                    report_map_char = await hid_service.characteristic(_HID_REPORT_MAP_UUID)
                    report_map = await report_map_char.read()
                    print(f"Report map length: {len(report_map) if report_map else 'None'}")
                except:
                    print("Could not read report map")
                
            except asyncio.TimeoutError:
                print("Timeout discovering services/characteristics. Retrying...")
                await asyncio.sleep_ms(5000)
                continue
            except Exception as e:
                print("Service discovery error:", e)
                await asyncio.sleep_ms(5000)
                continue

            print("Starting gamepad input reading...")
            while True:
                try:
                    # Read HID report data
                    report_data = await report_characteristic.read()
                    if report_data is not None and len(report_data) > 0:
                        # Update gamepad state
                        gamepad_state.update_from_report(report_data)
                        
                        # Print current state (you can modify this for your needs)
                        gamepad_state.print_state()
                        print("---")
                        
                        # Raw data for debugging
                        print(f"Raw data: {[hex(b) for b in report_data]}")
                    else:
                        print("No data received from gamepad")
                        
                except Exception as e:
                    print("Error reading gamepad data:", e)
                    break

                await asyncio.sleep_ms(100)  # Read at 10Hz

# Create an Event Loop
loop = asyncio.get_event_loop()
# Create a task to run the main function
loop.create_task(main())

try:
    # Run the event loop indefinitely
    loop.run_forever()
except Exception as e:
    print('Error occurred: ', e)
except KeyboardInterrupt:
    print('Program Interrupted by the user')