# Updated for 8BitDo Zero 2 with correct pairing modes
from micropython import const
import uasyncio as asyncio
import aioble
import bluetooth
import struct

# Service UUIDs
_HID_SERVICE_UUID = bluetooth.UUID(0x1812)
_BATTERY_SERVICE_UUID = bluetooth.UUID(0x180F)
_DEVICE_INFO_SERVICE_UUID = bluetooth.UUID(0x180A)
_HID_REPORT_UUID = bluetooth.UUID(0x2A4D)

# 8BitDo Zero 2 device names in different modes
GAMEPAD_NAMES = [
    "8BitDo Zero 2 gamepad",  # Windows/Android mode
    "Wireless Controller",     # macOS mode
    "8BitDo Zero 2",          # Possible alternative
    "Zero 2"                  # Possible short name
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

async def find_8bitdo_gamepad():
    """Look specifically for 8BitDo Zero 2 gamepad"""
    print("=== 8BitDo Zero 2 Setup Instructions ===")
    print("1. Put your gamepad in the correct mode:")
    print("   - For Windows/Android mode: Press X + Start")
    print("   - For Keyboard mode: Press R + Start")
    print("   - LED should blink in a pattern")
    print("2. Enter pairing mode: Press SELECT for 3 seconds")
    print("   - LED should start blinking rapidly")
    print("3. Keep the gamepad close to your Pico W")
    print()
    print("Scanning for 8BitDo Zero 2...")
    
    candidates = []
    
    # Scan for devices
    async with aioble.scan(15000, interval_us=30000, window_us=30000, active=True) as scanner:
        async for result in scanner:
            device_name = result.name()
            device_addr = result.device.addr_hex() if hasattr(result.device, 'addr_hex') else str(result.device)
            services = list(result.services())
            
            print(f"Found: {device_name or 'No Name'} ({device_addr})")
            
            # Check if this matches 8BitDo Zero 2 patterns
            is_8bitdo = False
            confidence = 0
            
            if device_name:
                name_lower = device_name.lower()
                
                # Exact matches
                for expected_name in GAMEPAD_NAMES:
                    if expected_name.lower() == name_lower:
                        is_8bitdo = True
                        confidence = 100
                        print(f"  ✓ EXACT MATCH: {expected_name}")
                        break
                
                # Partial matches
                if not is_8bitdo:
                    if "8bitdo" in name_lower:
                        is_8bitdo = True
                        confidence = 90
                        print(f"  ✓ Contains '8bitdo'")
                    elif "zero" in name_lower and "2" in name_lower:
                        is_8bitdo = True
                        confidence = 85
                        print(f"  ✓ Contains 'zero 2'")
                    elif "wireless controller" in name_lower:
                        is_8bitdo = True
                        confidence = 70
                        print(f"  ✓ Generic controller name (might be 8BitDo in macOS mode)")
            
            # Check services
            service_info = []
            has_hid = False
            has_battery = False
            
            for service in services:
                service_str = str(service).lower()
                if "1812" in service_str:
                    has_hid = True
                    service_info.append("HID")
                elif "180f" in service_str:
                    has_battery = True
                    service_info.append("Battery")
                else:
                    service_info.append(service_str)
            
            if has_hid:
                confidence += 20
                print(f"  ✓ Has HID service")
            if has_battery:
                confidence += 10
                print(f"  ✓ Has Battery service")
            
            print(f"  Services: {service_info}")
            print(f"  Confidence: {confidence}%")
            
            if is_8bitdo or confidence > 30:
                candidates.append({
                    'device': result.device,
                    'name': device_name,
                    'addr': device_addr,
                    'confidence': confidence,
                    'has_hid': has_hid,
                    'services': services
                })
                print(f"  → Added as candidate")
            
            print("---")
    
    # Sort by confidence
    candidates.sort(key=lambda x: x['confidence'], reverse=True)
    
    if candidates:
        print(f"\nFound {len(candidates)} candidate(s):")
        for i, candidate in enumerate(candidates):
            print(f"{i+1}. {candidate['name'] or 'No Name'} ({candidate['addr']}) - {candidate['confidence']}% confidence")
        
        return candidates[0]['device']  # Return the best candidate
    
    return None

async def connect_with_retries(device, max_retries=5):
    """Try to connect with multiple strategies"""
    for attempt in range(max_retries):
        try:
            print(f"Connection attempt {attempt + 1}/{max_retries}...")
            
            # Vary the connection timeout
            timeout = 8 + (attempt * 2)
            connection = await asyncio.wait_for(device.connect(), timeout=timeout)
            print("✓ Connected successfully!")
            return connection
            
        except asyncio.TimeoutError:
            print(f"  Timeout after {timeout}s")
        except Exception as e:
            error_msg = str(e)
            print(f"  Error: {error_msg}")
            
            if "EINVAL" in error_msg:
                print("  → EINVAL suggests the device might not be in BLE mode")
                print("  → Try different button combinations or check the manual")
            elif "EALREADY" in error_msg:
                print("  → Device might already be connected elsewhere")
            
        if attempt < max_retries - 1:
            print(f"  Waiting 3 seconds before retry...")
            await asyncio.sleep_ms(3000)
    
    return None

async def main():
    gamepad_state = GamepadState()
    
    while True:
        # Find the gamepad
        device = await find_8bitdo_gamepad()
        
        if not device:
            print("\n❌ No 8BitDo Zero 2 found!")
            print("\nTroubleshooting:")
            print("1. Make sure you pressed the correct button combination:")
            print("   - X + Start (for Windows mode)")
            print("   - R + Start (for Keyboard mode)")
            print("2. Then press SELECT for 3 seconds (LED should blink rapidly)")
            print("3. Make sure the gamepad is close to your Pico W")
            print("4. Try turning the gamepad off and on again")
            print("\nRetrying in 15 seconds...")
            await asyncio.sleep_ms(15000)
            continue
        
        # Try to connect
        print(f"\n🎮 Attempting to connect to gamepad...")
        connection = await connect_with_retries(device)
        
        if not connection:
            print("\n❌ Could not establish connection")
            print("The 8BitDo Zero 2 might be using Classic Bluetooth instead of BLE")
            print("Try putting it in different modes or check if it needs to be in a specific BLE mode")
            print("\nRetrying in 15 seconds...")
            await asyncio.sleep_ms(15000)
            continue
        
        print("\n✓ Successfully connected to 8BitDo Zero 2!")
        
        # Work with the connection
        async with connection:
            try:
                # Discover services
                print("Discovering services...")
                hid_service = await connection.service(_HID_SERVICE_UUID)
                print("✓ Found HID service")
                
                # Get input characteristic
                input_char = await hid_service.characteristic(_HID_REPORT_UUID)
                print("✓ Found HID report characteristic")
                
                print("\n🎮 Gamepad ready! Press buttons and move controls...")
                print("Press Ctrl+C to stop\n")
                
                # Try to enable notifications first
                try:
                    await input_char.subscribe(notify=True)
                    print("✓ Notifications enabled")
                    
                    while True:
                        try:
                            data = await asyncio.wait_for(input_char.notified(), timeout=1.0)
                            if data and len(data) > 0:
                                print(f"Input: {[hex(b) for b in data]}")
                                gamepad_state.update_from_report(data)
                                gamepad_state.print_state()
                                print("---")
                        except asyncio.TimeoutError:
                            pass  # No input, continue
                        except Exception as e:
                            print(f"Notification error: {e}")
                            break
                
                except Exception as e:
                    print(f"Notifications not supported: {e}")
                    print("Falling back to polling...")
                    
                    while True:
                        try:
                            data = await input_char.read()
                            if data and len(data) > 0:
                                print(f"Input: {[hex(b) for b in data]}")
                                gamepad_state.update_from_report(data)
                                gamepad_state.print_state()
                                print("---")
                            await asyncio.sleep_ms(50)  # 20Hz polling
                        except Exception as e:
                            print(f"Read error: {e}")
                            break``````
                
            except Exception as e:
                print(f"Service error: {e}")
                continue

# Create an Event Loop
loop = asyncio.get_event_loop()
loop.create_task(main())

try:
    loop.run_forever()
except Exception as e:
    print('Error occurred: ', e)
except KeyboardInterrupt:
    print('\n👋 Program stopped by user')