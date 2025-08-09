# Modified approach for 8BitDo Zero 2 - try different connection methods
from micropython import const
import uasyncio as asyncio
import aioble
import bluetooth
import struct

# Multiple possible service UUIDs for gamepads
_HID_SERVICE_UUID = bluetooth.UUID(0x1812)  # HID Service
_BATTERY_SERVICE_UUID = bluetooth.UUID(0x180F)  # Battery Service
_DEVICE_INFO_SERVICE_UUID = bluetooth.UUID(0x180A)  # Device Information

# HID Report Characteristic UUID
_HID_REPORT_UUID = bluetooth.UUID(0x2A4D)

# 8BitDo specific - they might use custom UUIDs
_CUSTOM_SERVICE_UUIDS = [
    bluetooth.UUID("6e400001-b5a3-f393-e0a9-e50e24dcca9e"),  # Nordic UART Service (sometimes used)
    bluetooth.UUID("0000180f-0000-1000-8000-00805f9b34fb"),  # Battery Service
    bluetooth.UUID("00001812-0000-1000-8000-00805f9b34fb"),  # HID Service
]

class GamepadState:
    def __init__(self):
        self.left_stick_x = 128
        self.left_stick_y = 128
        self.right_stick_x = 128
        self.right_stick_y = 128
        self.buttons = 0
        self.dpad = 0
    
    def update_from_report(self, data):
        """Update gamepad state from HID report data"""
        if len(data) >= 4:
            self.left_stick_x = data[0] if len(data) > 0 else 128
            self.left_stick_y = data[1] if len(data) > 1 else 128
            self.right_stick_x = data[2] if len(data) > 2 else 128
            self.right_stick_y = data[3] if len(data) > 3 else 128
            
            if len(data) > 4:
                self.buttons = struct.unpack("<H", data[4:6])[0] if len(data) >= 6 else data[4]
            if len(data) > 6:
                self.dpad = data[6]
    
    def get_button_state(self, button_bit):
        return bool(self.buttons & (1 << button_bit))
    
    def get_stick_position(self, stick):
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
        print(f"Left: ({self.get_stick_position('left_x'):.2f}, {self.get_stick_position('left_y'):.2f})")
        print(f"Right: ({self.get_stick_position('right_x'):.2f}, {self.get_stick_position('right_y'):.2f})")
        print(f"Buttons: 0x{self.buttons:04X}")

async def scan_for_gamepad_detailed():
    """Enhanced scanning with more details and filtering"""
    print("Detailed scan for 8BitDo Zero 2...")
    candidates = []
    
    # Longer scan to catch all advertisements
    async with aioble.scan(15000, interval_us=30000, window_us=30000, active=True) as scanner:
        async for result in scanner:
            device_name = result.name()
            device_addr = result.device.addr_hex() if hasattr(result.device, 'addr_hex') else str(result.device)
            services = list(result.services())
            
            # Check if this looks like a gamepad
            is_candidate = False
            reasons = []
            
            # Check name patterns
            if device_name:
                name_lower = device_name.lower()
                gamepad_keywords = ['8bitdo', 'zero', 'gamepad', 'controller', 'joystick']
                if any(keyword in name_lower for keyword in gamepad_keywords):
                    is_candidate = True
                    reasons.append(f"Name: {device_name}")
            
            # Check for gaming-related services
            service_strings = [str(s).lower() for s in services]
            if any('1812' in s for s in service_strings):  # HID
                is_candidate = True
                reasons.append("HID service")
            if any('180f' in s for s in service_strings):  # Battery
                reasons.append("Battery service")
            
            # Check signal strength (closer devices more likely to be our gamepad)
            rssi = getattr(result, 'rssi', None)
            if rssi and rssi > -60:  # Strong signal
                reasons.append(f"Strong signal: {rssi}dBm")
            
            if is_candidate or len(reasons) > 1:  # Multiple indicators
                candidates.append({
                    'device': result.device,
                    'name': device_name,
                    'addr': device_addr,
                    'services': services,
                    'reasons': reasons,
                    'rssi': rssi
                })
                print(f"CANDIDATE: {device_name or 'No Name'} ({device_addr})")
                print(f"  Reasons: {', '.join(reasons)}")
                print(f"  Services: {[str(s) for s in services]}")
                if rssi:
                    print(f"  RSSI: {rssi}dBm")
                print("---")
    
    # Sort candidates by signal strength if available
    candidates.sort(key=lambda x: x.get('rssi', -100), reverse=True)
    return candidates

async def try_connect_with_retry(device, max_retries=3):
    """Try to connect with multiple attempts and different approaches"""
    for attempt in range(max_retries):
        try:
            print(f"Connection attempt {attempt + 1}/{max_retries}...")
            
            # Try with different timeout values
            timeout = 5 + (attempt * 2)  # Increase timeout with each attempt
            connection = await asyncio.wait_for(device.connect(), timeout=timeout)
            print("Connection successful!")
            return connection
            
        except asyncio.TimeoutError:
            print(f"Attempt {attempt + 1} timed out")
            if attempt < max_retries - 1:
                await asyncio.sleep_ms(2000)
        except Exception as e:
            print(f"Attempt {attempt + 1} failed: {e}")
            if "EINVAL" in str(e):
                print("EINVAL error - device might not support BLE central connection")
                break
            if attempt < max_retries - 1:
                await asyncio.sleep_ms(2000)
    
    return None

async def main():
    gamepad_state = GamepadState()
    
    while True:
        print("=== 8BitDo Zero 2 Gamepad Scanner ===")
        print("Make sure your gamepad is in pairing mode:")
        print("- Hold Start + Y for 3 seconds, OR")
        print("- Hold Start + Right shoulder button")
        print("- LED should be flashing rapidly")
        print()
        
        # Scan for candidates
        candidates = await scan_for_gamepad_detailed()
        
        if not candidates:
            print("No gamepad candidates found. Retrying in 10 seconds...")
            await asyncio.sleep_ms(10000)
            continue
        
        print(f"Found {len(candidates)} candidate(s). Trying to connect...")
        
        connected_device = None
        connection = None
        
        # Try each candidate
        for i, candidate in enumerate(candidates):
            print(f"\nTrying candidate {i+1}: {candidate['name'] or 'No Name'} ({candidate['addr']})")
            
            connection = await try_connect_with_retry(candidate['device'])
            if connection:
                connected_device = candidate
                break
        
        if not connection:
            print("Could not connect to any candidates.")
            print("\nTroubleshooting tips:")
            print("1. Make sure the gamepad is in the correct pairing mode")
            print("2. Try turning the gamepad off and on again")
            print("3. The 8BitDo Zero 2 might use classic Bluetooth, not BLE")
            print("4. Try different button combinations for pairing mode")
            print("\nRetrying in 15 seconds...")
            await asyncio.sleep_ms(15000)
            continue
        
        print(f"Successfully connected to: {connected_device['name'] or 'Unknown'}")
        
        # Now try to work with the connection
        async with connection:
            print("Exploring device services...")
            
            try:
                # Get all available services
                all_services = await connection.services()
                print(f"Found {len(all_services)} services:")
                
                for service in all_services:
                    print(f"  Service: {service.uuid}")
                    try:
                        chars = await service.characteristics()
                        if chars:
                            for char in chars:
                                print(f"    Characteristic: {char.uuid}")
                    except:
                        print(f"    Could not enumerate characteristics")
                
                # Try to find a usable input characteristic
                input_char = None
                
                # Look through all services for readable characteristics
                for service in all_services:
                    try:
                        chars = await service.characteristics()
                        if chars:
                            for char in chars:
                                # Try to read from this characteristic
                                try:
                                    test_data = await char.read()
                                    if test_data:
                                        print(f"Found readable characteristic: {char.uuid} in service {service.uuid}")
                                        print(f"Sample data: {[hex(b) for b in test_data]}")
                                        input_char = char
                                        break
                                except:
                                    pass  # This characteristic isn't readable
                        if input_char:
                            break
                    except:
                        continue
                
                if not input_char:
                    print("No readable characteristics found")
                    continue
                
                print(f"Using characteristic: {input_char.uuid}")
                print("Reading gamepad data... Press buttons and move sticks!")
                
                # Read data
                while True:
                    try:
                        data = await input_char.read()
                        if data and len(data) > 0:
                            print(f"Data: {[hex(b) for b in data]} (len: {len(data)})")
                            gamepad_state.update_from_report(data)
                            gamepad_state.print_state()
                            print("---")
                        
                        await asyncio.sleep_ms(100)
                        
                    except Exception as e:
                        print(f"Read error: {e}")
                        break
            
            except Exception as e:
                print(f"Service exploration error: {e}")
                continue

# Create an Event Loop
loop = asyncio.get_event_loop()
loop.create_task(main())

try:
    loop.run_forever()
except Exception as e:
    print('Error occurred: ', e)
except KeyboardInterrupt:
    print('Program Interrupted by the user')