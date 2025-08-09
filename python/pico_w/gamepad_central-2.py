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

async def scan_all_devices():
    """Scan and list all nearby Bluetooth devices for debugging"""
    print("Scanning for ALL Bluetooth devices...")
    devices_found = []
    
    async with aioble.scan(15000, interval_us=30000, window_us=30000, active=True) as scanner:
        async for result in scanner:
            device_name = result.name()
            device_addr = result.device.addr_hex() if hasattr(result.device, 'addr_hex') else str(result.device)
            services = list(result.services())
            
            # Avoid duplicates
            if device_addr not in [d['addr'] for d in devices_found]:
                device_info = {
                    'name': device_name,
                    'addr': device_addr,
                    'services': [str(s) for s in services]
                }
                devices_found.append(device_info)
                
                print(f"Device: {device_name or 'No Name'}")
                print(f"  Address: {device_addr}")
                print(f"  Services: {device_info['services']}")
                print(f"  Has HID: {'Yes' if _HID_SERVICE_UUID in services else 'No'}")
                print("---")
    
    print(f"Total devices found: {len(devices_found)}")
    return devices_found

async def find_gamepad_interactive():
    """Interactive gamepad finding - shows all devices and lets you choose"""
    devices = await scan_all_devices()
    
    if not devices:
        print("No devices found!")
        return None
    
    # Look for likely candidates
    candidates = []
    for i, device in enumerate(devices):
        is_candidate = False
        reasons = []
        
        # Check for HID service
        if any('1812' in service for service in device['services']):
            is_candidate = True
            reasons.append("Has HID service")
        
        # Check for gamepad-like names
        if device['name']:
            name_lower = device['name'].lower()
            if any(pattern.lower() in name_lower for pattern in ['8bitdo', 'zero', 'gamepad', 'controller']):
                is_candidate = True
                reasons.append("Name suggests gamepad")
        
        # Check for battery service (common in gamepads)
        if any('180f' in service.lower() for service in device['services']):
            reasons.append("Has battery service")
        
        if is_candidate:
            candidates.append((i, device, reasons))
            print(f"CANDIDATE {i}: {device['name'] or 'No Name'} ({device['addr']})")
            print(f"  Reasons: {', '.join(reasons)}")
    
    # If we found likely candidates, try the first one
    if candidates:
        best_candidate = candidates[0]
        print(f"Trying best candidate: {best_candidate[1]['name'] or 'No Name'}")
        # We need to scan again to get the actual device object
        return await find_specific_device(best_candidate[1]['addr'])
    
    return None

async def find_specific_device(target_addr):
    """Find a specific device by address"""
    async with aioble.scan(10000, interval_us=30000, window_us=30000, active=True) as scanner:
        async for result in scanner:
            device_addr = result.device.addr_hex() if hasattr(result.device, 'addr_hex') else str(result.device)
            if device_addr == target_addr:
                return result.device
    return None

async def try_connect_and_check_hid(device_addr, device_obj):
    """Try to connect to a device and check if it has HID services"""
    try:
        print(f"Trying to connect to {device_addr}...")
        connection = await asyncio.wait_for(device_obj.connect(), timeout=10)
        print(f"Connected to {device_addr}")
        
        async with connection:
            try:
                # Try to discover HID service
                hid_service = await asyncio.wait_for(connection.service(_HID_SERVICE_UUID), timeout=5)
                print(f"Found HID service on {device_addr} - This might be our gamepad!")
                return device_obj
            except asyncio.TimeoutError:
                print(f"No HID service found on {device_addr}")
                return None
            except Exception as e:
                print(f"Error checking services on {device_addr}: {e}")
                return None
                
    except asyncio.TimeoutError:
        print(f"Connection timeout to {device_addr}")
        return None
    except Exception as e:
        print(f"Connection error to {device_addr}: {e}")
        return None

async def find_gamepad_by_trial():
    """Find gamepad by trying to connect to each device and checking for HID"""
    print("Scanning for devices to test...")
    potential_devices = []
    
    # First, collect all devices
    async with aioble.scan(10000, interval_us=30000, window_us=30000, active=True) as scanner:
        async for result in scanner:
            device_addr = result.device.addr_hex() if hasattr(result.device, 'addr_hex') else str(result.device)
            if device_addr not in [d[0] for d in potential_devices]:
                potential_devices.append((device_addr, result.device))
                print(f"Found device: {device_addr}")
    
    print(f"Found {len(potential_devices)} devices. Testing each for HID services...")
    
    # Try connecting to each device to check for HID services
    for device_addr, device_obj in potential_devices:
        gamepad = await try_connect_and_check_hid(device_addr, device_obj)
        if gamepad:
            return gamepad
        await asyncio.sleep_ms(1000)  # Small delay between attempts
    
    return None

async def main():
    gamepad_state = GamepadState()
    
    while True:
        print("Looking for 8BitDo Zero 2 gamepad...")
        device = await find_gamepad_by_trial()
        
        if not device:
            print("8BitDo Zero 2 gamepad not found. Make sure it's in pairing mode (Start + Right shoulder button).")
            print("Retrying in 10 seconds...")
            await asyncio.sleep_ms(10000)
            continue

        try:
            print("Connecting to gamepad...")
            connection = await device.connect()
            print("Connected successfully!")
        except Exception as e:
            print("Connection error:", e)
            await asyncio.sleep_ms(5000)
            continue

        async with connection:
            try:
                print("Discovering HID service...")
                hid_service = await connection.service(_HID_SERVICE_UUID)
                print("HID service found")
                
                # Get all characteristics in the HID service
                print("Discovering characteristics...")
                characteristics = await hid_service.characteristics()
                print(f"Found {len(characteristics)} characteristics")
                
                # Look for input report characteristic
                input_char = None
                for char in characteristics:
                    print(f"Characteristic: {char.uuid}")
                    # Try different possible UUIDs for input reports
                    if (char.uuid == _HID_REPORT_UUID or 
                        str(char.uuid) == "2a4d" or 
                        "2a4d" in str(char.uuid).lower()):
                        input_char = char
                        print("Found input report characteristic")
                        break
                
                if not input_char:
                    # If we can't find the standard report characteristic, try the first one
                    if characteristics:
                        input_char = characteristics[0]
                        print(f"Using first characteristic: {input_char.uuid}")
                    else:
                        print("No characteristics found")
                        continue
                
            except Exception as e:
                print("Service discovery error:", e)
                await asyncio.sleep_ms(5000)
                continue

            print("Starting gamepad input reading...")
            print("Press buttons and move sticks on your gamepad...")
            
            while True:
                try:
                    # Try to read from the characteristic
                    report_data = await input_char.read()
                    if report_data is not None and len(report_data) > 0:
                        print(f"Received data: {[hex(b) for b in report_data]} (length: {len(report_data)})")
                        
                        # Update gamepad state
                        gamepad_state.update_from_report(report_data)
                        gamepad_state.print_state()
                        print("---")
                    else:
                        print("No data received")
                        
                except Exception as e:
                    print("Error reading gamepad data:", e)
                    # Try to continue rather than breaking immediately
                    await asyncio.sleep_ms(1000)
                    continue

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