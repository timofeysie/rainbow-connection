# 8BitDo Zero 2 Gamepad Reader for Pico 2 W
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

# 8BitDo Zero 2 specific
_8BITDO_NAME = "8BitDo Zero 2"
_8BITDO_PARTIAL_NAME = "Zero 2"

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
        
        # 8BitDo Zero 2 typically uses 8-byte reports
        # Format may vary - this is a common pattern
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
            print(f"Parse error: {e}")
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
        self._ble = bluetooth.BLE()
        self._ble.active(True)
        self._ble.irq(self._irq)
        self._reset()
        
        self.gamepad_state = GamepadState()
        self.connected_device = None
        self.hid_service = None
        self.hid_characteristic = None
        
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
        if event == _IRQ_SCAN_RESULT:
            addr_type, addr, adv_type, rssi, adv_data = data
            addr_str = ':'.join(['%02X' % i for i in addr])
            name = self._decode_name(adv_data)
            
            print(f"Found device: {name} ({addr_str}) RSSI: {rssi}")
            
            # Look for 8BitDo Zero 2
            if (name and (_8BITDO_NAME in name or _8BITDO_PARTIAL_NAME in name)) or \
               (name and "8BitDo" in name):
                print(f"🎮 Found 8BitDo device: {name}")
                self._addr_type = addr_type
                self._addr = bytes(addr)
                self._ble.gap_scan(None)  # Stop scanning
                self._ble.gap_connect(self._addr_type, self._addr)
        
        elif event == _IRQ_SCAN_DONE:
            print("Scan complete")
            
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
                
                # Enable notifications
                try:
                    self._ble.gattc_write(
                        self._conn_handle, 
                        self._value_handle + 1,  # Client Characteristic Configuration Descriptor
                        struct.pack("<H", 0x0001),  # Enable notifications
                        True
                    )
                except:
                    print("⚠️ Could not enable notifications, will poll instead")
                    
            else:
                print("❌ HID characteristic not found")
                self._ble.gap_disconnect(self._conn_handle)
                
        elif event == _IRQ_GATTC_NOTIFY:
            conn_handle, value_handle, notify_data = data
            if value_handle == self._value_handle:
                self._handle_gamepad_data(notify_data)
                
        elif event == _IRQ_GATTC_READ_RESULT:
            conn_handle, value_handle, char_data = data
            if value_handle == self._value_handle:
                self._handle_gamepad_data(char_data)
                
        elif event == _IRQ_GATTC_READ_DONE:
            conn_handle, value_handle, status = data
            if status != 0:
                print(f"❌ Read failed: {status}")
    
    def _decode_name(self, adv_data):
        """Decode device name from advertising data"""
        n = 0
        while n < len(adv_data):
            length = adv_data[n]
            if length == 0:
                break
            type = adv_data[n + 1]
            if type == 0x09:  # Complete Local Name
                return adv_data[n + 2:n + length + 1].decode()
            n += length + 1
        return None
    
    def _handle_gamepad_data(self, data):
        """Process incoming gamepad data"""
        if self.gamepad_state.parse_hid_report(data):
            active_inputs = self.gamepad_state.get_active_inputs()
            if active_inputs:
                print(f"�� Input: {', '.join(active_inputs)}")
    
    def scan_for_gamepad(self, duration_ms=10000):
        """Scan for 8BitDo Zero 2 gamepad"""
        print(f"🔍 Scanning for {_8BITDO_NAME}...")
        print("💡 Make sure gamepad is in BLE mode (Start + Y for 3 seconds)")
        print("   LED should flash slowly, not rapidly")
        
        self._ble.gap_scan(duration_ms, 30000, 30000, False)
        
        # Wait for scan to complete or device found
        start_time = time.ticks_ms()
        while time.ticks_diff(time.ticks_ms(), start_time) < duration_ms:
            if self._addr is not None:
                break
            time.sleep(0.1)
        
        if self._addr is None:
            print("❌ 8BitDo Zero 2 not found")
            print("💡 Check:")
            print("   - Gamepad is powered on")
            print("   - Gamepad is in BLE mode (Start + Y)")
            print("   - Gamepad is nearby")
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
    print("�� 8BitDo Zero 2 Gamepad Reader for Pico 2 W")
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
        print(f"❌ Error: {e}")
    finally:
        gamepad.disconnect()
        print("✅ Disconnected")

if __name__ == "__main__":
    main()