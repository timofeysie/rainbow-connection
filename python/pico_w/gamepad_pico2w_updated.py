# 8BitDo Zero 2 Gamepad Reader for Pico 2 W - Updated for Actual Manual
import aioble
import bluetooth
import random
import struct
import time
from micropython import const

# BLE constants
_IRQ_CENTRAL_CONNECT = const(1)
_IRQ_CENTRAL_DISCONNECT = const(2)
_IRQ_GATTC_SERVICE_RESULT = const(7)
_IRQ_GATTC_SERVICE_DONE = const(8)
_IRQ_GATTC_CHARACTERISTIC_RESULT = const(11)
_IRQ_GATTC_CHARACTERISTIC_DONE = const(12)
_IRQ_GATTC_DESCRIPTOR_RESULT = const(13)
_IRQ_GATTC_DESCRIPTOR_DONE = const(14)
_IRQ_GATTC_READ_RESULT = const(15)
_IRQ_GATTC_READ_DONE = const(16)
_IRQ_GATTC_READ_STATUS = const(17)
_IRQ_GATTC_WRITE_STATUS = const(18)
_IRQ_GATTC_NOTIFY = const(19)
_IRQ_GATTC_INDICATE = const(20)
_IRQ_SCAN_RESULT = const(21)
_IRQ_SCAN_DONE = const(22)
_IRQ_PERIPHERAL_CONNECT = const(23)
_IRQ_PERIPHERAL_DISCONNECT = const(24)
_IRQ_GATTS_WRITE = const(25)
_IRQ_GATTS_READ_REQUEST = const(26)
_IRQ_CONNECTION_UPDATE = const(27)
_IRQ_ENCRYPTION_UPDATE = const(28)
_IRQ_GET_SECRET = const(29)
_IRQ_SET_SECRET = const(30)

# HID Service UUIDs
_HID_SERVICE_UUID = bluetooth.UUID(0x1812)
_HID_REPORT_UUID = bluetooth.UUID(0x2A4D)
_HID_REPORT_MAP_UUID = bluetooth.UUID(0x2A4B)

# 8BitDo Zero 2 - based on actual manual
_8BITDO_NAMES = [
    "8BitDo Zero 2",
    "8BitDo Zero 2 gamepad",
    "Zero 2",
    "8BitDo"
]

class GamepadState:
    def __init__(self):
        self.buttons = {
            'A': False, 'B': False, 'X': False, 'Y': False,
            'L': False, 'R': False, 'ZL': False, 'ZR': False,
            'SELECT': False, 'START': False, 'HOME': False,
            'L_STICK': False, 'R_STICK': False
        }
        self.dpad = {'UP': False, 'DOWN': False, 'LEFT': False, 'RIGHT': False}
        self.left_stick = {'x': 128, 'y': 128}  # 0-255 range
        self.right_stick = {'x': 128, 'y': 128}
        self.timestamp = 0
    
    def parse_hid_report(self, data):
        """Parse HID report data from 8BitDo Zero 2"""
        if len(data) < 8:
            return False
        
        try:
            # Button states (first byte)
            button_byte = data[0]
            self.buttons['A'] = bool(button_byte & 0x01)
            self.buttons['B'] = bool(button_byte & 0x02)
            self.buttons['X'] = bool(button_byte & 0x04)
            self.buttons['Y'] = bool(button_byte & 0x08)
            self.buttons['L'] = bool(button_byte & 0x10)
            self.buttons['R'] = bool(button_byte & 0x20)
            self.buttons['SELECT'] = bool(button_byte & 0x40)
            self.buttons['START'] = bool(button_byte & 0x80)
            
            # D-pad (second byte)
            dpad_byte = data[1]
            self.dpad['UP'] = bool(dpad_byte & 0x01)
            self.dpad['DOWN'] = bool(dpad_byte & 0x02)
            self.dpad['LEFT'] = bool(dpad_byte & 0x04)
            self.dpad['RIGHT'] = bool(dpad_byte & 0x08)
            
            # Left stick (bytes 2-3)
            if len(data) >= 4:
                self.left_stick['x'] = data[2]
                self.left_stick['y'] = data[3]
            
            # Right stick (bytes 4-5) if available
            if len(data) >= 6:
                self.right_stick['x'] = data[4]
                self.right_stick['y'] = data[5]
            
            self.timestamp = time.ticks_ms()
            return True
            
        except Exception as e:
            print("Parse error: " + str(e))
            return False
    
    def get_active_inputs(self):
        """Get list of currently active inputs"""
        active = []
        
        # Check buttons
        for name, state in self.buttons.items():
            if state:
                active.append(name)
        
        # Check d-pad
        for direction, state in self.dpad.items():
            if state:
                active.append(f"DPAD_{direction}")
        
        # Check sticks (if moved significantly from center)
        if abs(self.left_stick['x'] - 128) > 20 or abs(self.left_stick['y'] - 128) > 20:
            active.append(f"L_STICK({self.left_stick['x']},{self.left_stick['y']})")
        
        if abs(self.right_stick['x'] - 128) > 20 or abs(self.right_stick['y'] - 128) > 20:
            active.append(f"R_STICK({self.right_stick['x']},{self.right_stick['y']})")
        
        return active

class GamepadCentral:
    def __init__(self):
        print("🔧 Initializing BLE system...")
        self._ble = bluetooth.BLE()
        
        print(f"📱 BLE active state: {self._ble.active()}")
        print("🔧 Activating BLE...")
        self._ble.active(True)
        print(f"📱 BLE active state after activation: {self._ble.active()}")
        
        print("🔧 Setting up BLE IRQ handler...")
        self._ble.irq(self._irq)
        
        print("🔧 Resetting BLE state...")
        self._reset()
        
        self.gamepad_state = GamepadState()
        self.connected_device = None
        self.hid_service = None
        self.hid_characteristic = None
        self.scan_results = []
        
        print("✅ BLE system initialized successfully")
        
    def _reset(self):
        """Reset BLE state"""
        self._addr = None
        self._addr_type = None
        self._conn_handle = None
        self._start_handle = None
        self._end_handle = None
        self._value_handle = None
        
    def _irq(self, event, data):
        """BLE event handler"""
        print(f"🔔 BLE IRQ Event: {event}")
        
        if event == _IRQ_SCAN_RESULT:
            try:
                addr_type, addr, adv_type, rssi, adv_data = data
                addr_str = ':'.join(['%02X' % i for i in addr])
                
                # Decode name and services with error handling
                try:
                    name = self._decode_name(adv_data)
                except Exception as e:
                    print("❌ Error decoding name: " + str(e))
                    name = None
                
                try:
                    services = self._decode_services(adv_data)
                except Exception as e:
                    print("❌ Error decoding services: " + str(e))
                    services = []
                
                # Store all scan results for debugging
                device_info = {
                    'addr': addr_str,
                    'name': name,
                    'rssi': rssi,
                    'services': services,
                    'adv_type': adv_type,
                    'adv_data': adv_data
                }
                self.scan_results.append(device_info)
                
                device_name = name or 'No Name'
                print("📱 Found: " + device_name + " (" + addr_str + ") RSSI: " + str(rssi))
                if services:
                    print(f"   Services: {services}")
                
                # Look for 8BitDo Zero 2 - but don't stop scanning immediately
                if name and any(bitdo_name in name for bitdo_name in _8BITDO_NAMES):
                    print(f"🎮 Found 8BitDo device: {name}")
                    # Store the target device but continue scanning to see all devices
                    if self._addr is None:  # Only store if we haven't found one yet
                        self._addr_type = addr_type
                        self._addr = bytes(addr)
                        print(f"🎯 Target device stored: {addr_str}")
                
            except Exception as e:
                print("❌ Error processing scan result: " + str(e))
                import sys
                sys.print_exception(e)
        
        elif event == _IRQ_SCAN_DONE:
            print("🔔 Scan complete. Found " + str(len(self.scan_results)) + " devices")
            print(f"🔔 Scan status: {data}")
            
            # Show all devices found for debugging
            if self.scan_results:
                print("\n📱 All devices found:")
                for i, device in enumerate(self.scan_results):
                    device_name = device['name'] or 'No Name'
                    print("  " + str(i+1) + ". " + device_name + " (" + device['addr'] + ") RSSI: " + str(device['rssi']))
                    if device['services']:
                        print("     Services: " + str(device['services']))
            
            # Now try to connect if we found a target device
            if self._addr is not None:
                addr_str = ':'.join(['%02X' % i for i in self._addr])
                print("🎯 Connecting to target device: " + addr_str)
                self._ble.gap_connect(self._addr_type, self._addr)
            else:
                print("❌ No 8BitDo Zero 2 found")
                print("\n💡 Troubleshooting:")
                print("1. Make sure you pressed the correct button combination:")
                print("   - B + Start (for Android mode) - LED blinks once per cycle")
                print("   - X + Start (for Windows mode) - LED blinks twice per cycle")
                print("   - A + Start (for macOS mode) - LED blinks 3 times per cycle")
                print("   - R + Start (for Keyboard mode) - LED blinks 5 times per cycle")
                print("2. Then press SELECT for 3 seconds (LED should blink rapidly)")
                print("3. Make sure the gamepad is close to your Pico 2 W")
                print("4. Try turning the gamepad off and on again")
                print("5. Check if the gamepad appears in the list above")
            
        elif event == _IRQ_PERIPHERAL_CONNECT:
            conn_handle, addr_type, addr = data
            addr_str = ':'.join(['%02X' % i for i in addr])
            print(f"✅ Connected to {addr_str}")
            self._conn_handle = conn_handle
            self._ble.gattc_discover_services(self._conn_handle)
            
        elif event == _IRQ_PERIPHERAL_DISCONNECT:
            conn_handle, addr_type, addr = data
            print("❌ Disconnected")
            self._reset()
            
        elif event == _IRQ_GATTC_SERVICE_RESULT:
            conn_handle, start_handle, end_handle, uuid = data
            print(f"Service: {uuid}")
            if uuid == _HID_SERVICE_UUID:
                print("🎯 Found HID Service!")
                self._start_handle = start_handle
                self._end_handle = end_handle
                
        elif event == _IRQ_GATTC_SERVICE_DONE:
            conn_handle, status = data
            if status == 0 and self._start_handle is not None:
                print("🔍 Discovering HID characteristics...")
                self._ble.gattc_discover_characteristics(
                    self._conn_handle, self._start_handle, self._end_handle
                )
            else:
                print("❌ HID service not found")
                self._ble.gap_disconnect(self._conn_handle)
                
        elif event == _IRQ_GATTC_CHARACTERISTIC_RESULT:
            conn_handle, def_handle, value_handle, properties, uuid = data
            print(f"Characteristic: {uuid} (handle: {value_handle})")
            
            if uuid == _HID_REPORT_UUID:
                print("🎯 Found HID Report Characteristic!")
                self._value_handle = value_handle
                
        elif event == _IRQ_GATTC_CHARACTERISTIC_DONE:
            conn_handle, status = data
            if status == 0 and self._value_handle is not None:
                print("✅ HID characteristic found!")
                print("🎮 Gamepad ready! Press buttons and move sticks...")
                
                # Try to enable notifications
                try:
                    self._ble.gattc_write(self._conn_handle, self._value_handle + 1, b'\x01\x00', 1)
                    print("🔔 Notifications enabled")
                except:
                    print("⚠️ Could not enable notifications, will use polling")
            else:
                print("❌ HID characteristic not found")
                self._ble.gap_disconnect(self._conn_handle)
                
        elif event == _IRQ_GATTC_NOTIFY:
            conn_handle, value_handle, notify_data = data
            if conn_handle == self._conn_handle and value_handle == self._value_handle:
                self._handle_gamepad_data(notify_data)
                
        elif event == _IRQ_GATTC_READ_DONE:
            conn_handle, value_handle, notify_data = data
            if conn_handle == self._conn_handle and value_handle == self._value_handle:
                self._handle_gamepad_data(notify_data)
    
    def _decode_name(self, adv_data):
        """Decode device name from advertising data"""
        try:
            print(f"🔍 Decoding name from adv_data: {adv_data}")
            n = 0
            while n < len(adv_data):
                length = adv_data[n]
                if length == 0:
                    break
                type = adv_data[n + 1]
                print(f"   Type: 0x{type:02x}, Length: {length}")
                
                if type == 0x09:  # Complete Local Name
                    name_data = adv_data[n + 2:n + length + 1]
                    print(f"   Found name data: {name_data}")
                    try:
                        name = name_data.decode()
                        print(f"   Decoded name: '{name}'")
                        return name
                    except Exception as e:
                        print("   Error decoding name: " + str(e))
                        return None
                elif type == 0x08:  # Shortened Local Name
                    name_data = adv_data[n + 2:n + length + 1]
                    print(f"   Found shortened name data: {name_data}")
                    try:
                        name = name_data.decode()
                        print(f"   Decoded shortened name: '{name}'")
                        return name
                    except Exception as e:
                        print("   Error decoding shortened name: " + str(e))
                        return None
                
                n += length + 1
            print("   No name found in advertising data")
            return None
        except Exception as e:
            print("❌ Error in _decode_name: " + str(e))
            return None
    
    def _decode_services(self, adv_data):
        """Decode services from advertising data"""
        try:
            print("🔍 Decoding services from adv_data: " + str(adv_data))
            services = []
            n = 0
            while n < len(adv_data):
                length = adv_data[n]
                if length == 0:
                    break
                type = adv_data[n + 1]
                print("   Service type: 0x" + str(type) + ", Length: " + str(length))
                
                if type == 0x16:  # Service Data
                    service_uuid = adv_data[n + 2:n + 4]
                    uuid_str = ':'.join(['%02x' % i for i in service_uuid])
                    services.append("uuid('" + uuid_str + "')")
                    print("   Found service data: " + str(uuid_str))
                elif type == 0x06:  # Incomplete List of 16-bit Service UUIDs
                    for i in range(2, length + 1, 2):
                        if i + 1 < length + 1:
                            uuid = struct.unpack("<H", adv_data[n + i:n + i + 2])[0]
                            services.append("0x" + str(uuid))
                            print("   Found 16-bit UUID: 0x" + str(uuid))
                elif type == 0x02:  # Incomplete List of 16-bit Service UUIDs (alternative)
                    for i in range(2, length + 1, 2):
                        if i + 1 < length + 1:
                            uuid = struct.unpack("<H", adv_data[n + i:n + i + 2])[0]
                            services.append("0x" + str(uuid))
                            print("   Found 16-bit UUID (alt): 0x" + str(uuid))
                elif type == 0x03:  # Complete List of 16-bit Service UUIDs
                    for i in range(2, length + 1, 2):
                        if i + 1 < length + 1:
                            uuid = struct.unpack("<H", adv_data[n + i:n + i + 2])[0]
                            services.append("0x" + str(uuid))
                            print("   Found complete 16-bit UUID: 0x" + str(uuid))
                
                n += length + 1
            print("   Total services found: " + str(len(services)))
            return services
        except Exception as e:
            print("❌ Error in _decode_services: " + str(e))
            return []
    
    def _handle_gamepad_data(self, data):
        """Process incoming gamepad data"""
        if self.gamepad_state.parse_hid_report(data):
            active_inputs = self.gamepad_state.get_active_inputs()
            if active_inputs:
                input_str = ', '.join(active_inputs)
                print("🎮 Input: " + input_str)
    
    def scan_for_gamepad(self, duration_ms=10000):
        """Scan for 8BitDo Zero 2 gamepad"""
        print(f"🔍 Scanning for 8BitDo Zero 2...")
        print("\n💡 Pairing Instructions (from manual):")
        print("1. Power on with one of these combinations:")
        print("   - B + Start (Android mode) - LED blinks once per cycle")
        print("   - X + Start (Windows mode) - LED blinks twice per cycle")
        print("   - A + Start (macOS mode) - LED blinks 3 times per cycle")
        print("   - R + Start (Keyboard mode) - LED blinks 5 times per cycle")
        print("2. Press SELECT for 3 seconds to enter pairing mode")
        print("   LED should start rapidly blinking")
        print("3. Keep gamepad close to Pico 2 W")
        print("\n🔍 Starting scan...")
        
        # Clear previous scan results
        self.scan_results = []
        
        print("🔧 Starting BLE scan for " + str(duration_ms) + "ms...")
        print("🔧 Scan parameters: interval=30000, window=30000, active=False")
        
        try:
            self._ble.gap_scan(duration_ms, 30000, 30000, False)
            print("✅ BLE scan started successfully")
        except Exception as e:
            print("❌ Failed to start BLE scan: " + str(e))
            return False
        
        # Wait for scan to complete or device found
        print("⏳ Waiting for scan results...")
        start_time = time.ticks_ms()
        scan_timeout = duration_ms + 2000  # Add 2 seconds buffer
        
        while time.ticks_diff(time.ticks_ms(), start_time) < scan_timeout:
            if self._addr is not None:
                print("🎯 Target device found during scan!")
                break
            time.sleep(0.1)
        
        elapsed_time = time.ticks_diff(time.ticks_ms(), start_time)
        print("⏱️ Scan wait completed. Time elapsed: " + str(elapsed_time) + "ms")
        
        if self._addr is None:
            print("❌ 8BitDo Zero 2 not found")
            print("📊 Scan results: " + str(len(self.scan_results)) + " devices found")
            return False
        
        return True
    
    def poll_gamepad(self):
        """Poll gamepad data (fallback if notifications don't work)"""
        if self._conn_handle is None or self._value_handle is None:
            return False
        
        try:
            self._ble.gattc_read(self._conn_handle, self._value_handle)
            return True
        except:
            return False
    
    def is_connected(self):
        """Check if gamepad is connected"""
        return self._conn_handle is not None
    
    def disconnect(self):
        """Disconnect from gamepad"""
        if self._conn_handle is not None:
            self._ble.gap_disconnect(self._conn_handle)

def main():
    """Main function"""
    print("🎮 8BitDo Zero 2 Gamepad Reader for Pico 2 W")
    print("=" * 50)
    print("Updated for actual manual pairing modes")
    print("=" * 50)
    
    gamepad = GamepadCentral()
    
    try:
        # Scan for gamepad
        if not gamepad.scan_for_gamepad():
            return
        
        # Wait for connection and setup
        print("⏳ Waiting for connection...")
        while not gamepad.is_connected():
            time.sleep(0.1)
        
        print("🎉 Gamepad connected and ready!")
        print("🎮 Press buttons and move sticks to test")
        print("💡 Press Ctrl+C to disconnect")
        
        # Main loop - poll for data
        last_poll = 0
        while gamepad.is_connected():
            current_time = time.ticks_ms()
            
            # Poll every 50ms if notifications aren't working
            if time.ticks_diff(current_time, last_poll) > 50:
                gamepad.poll_gamepad()
                last_poll = current_time
            
            time.sleep(0.01)
            
    except KeyboardInterrupt:
        print("\n👋 Disconnecting...")
    except Exception as e:
        print("❌ Error: " + str(e))
    finally:
        gamepad.disconnect()
        print("✅ Disconnected")

if __name__ == "__main__":
    main() 