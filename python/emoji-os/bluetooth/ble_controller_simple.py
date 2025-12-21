"""
Simple BLE Controller - exactly matches the working controller.py approach
Use this BLEController class in emoji-os-zero scripts
"""

import asyncio
from bleak import BleakScanner, BleakClient

# Nordic UART Service UUIDs
UART_SERVICE_UUID = "6E400001-B5A3-F393-E0A9-E50E24DCCA9E"
UART_RX_CHAR_UUID = "6E400002-B5A3-F393-E0A9-E50E24DCCA9E"  # Write characteristic
UART_TX_CHAR_UUID = "6E400003-B5A3-F393-E0A9-E50E24DCCA9E"  # Notify characteristic

# Device name to look for
TARGET_DEVICE_NAME = "Pico-Client"


class BLEController:
    """BLE Central controller that connects to Pico and sends commands
    This matches the working controller.py approach exactly
    """
    
    def __init__(self):
        self.client = None
        self.device_address = None
        self.connected = False
        
    async def scan_for_device(self, timeout=10):
        """Scan for the target Pico device - exactly like controller.py"""
        print(f"Scanning for '{TARGET_DEVICE_NAME}' for {timeout} seconds...")
        print("Make sure your Pico is running emoji-os-pico-0.2.0.py...")
        
        devices = await BleakScanner.discover(timeout=timeout)
        
        print(f"Found {len(devices)} BLE devices:")
        print("-" * 50)
        
        target_found = False
        for i, device in enumerate(devices, 1):
            name = device.name or "(No Name)"
            print(f"{i:2d}. {name:<20} | {device.address}")
            
            if device.name == TARGET_DEVICE_NAME:
                print(f"    *** FOUND TARGET DEVICE! ***")
                self.device_address = device.address
                target_found = True
        
        print("-" * 50)
        
        if target_found:
            print(f"✓ Found {TARGET_DEVICE_NAME} at address: {self.device_address}")
            return True
        else:
            print(f"✗ Could not find '{TARGET_DEVICE_NAME}'")
            print("\nTroubleshooting tips:")
            print("1. Make sure Pico is running emoji-os-pico-0.2.0.py")
            print("2. Check that Pico shows 'Starting advertising as 'Pico-Client'...'")
            print("3. Try moving devices closer together")
            print("4. Restart both devices")
            return False
    
    async def connect_to_device(self):
        """Connect to the discovered Pico device - exactly like controller.py"""
        if not self.device_address:
            print("No device address available. Run scan_for_device() first.")
            return False
            
        try:
            print(f"Connecting to {self.device_address}...")
            self.client = BleakClient(self.device_address)
            await self.client.connect()
            
            if self.client.is_connected:
                print("✓ Successfully connected!")
                self.connected = True
                return True
            else:
                print("✗ Failed to connect")
                return False
                
        except Exception as e:
            print(f"✗ Connection error: {e}")
            return False
    
    async def send_emoji_command(self, menu, pos, neg):
        """Send emoji selection command to the connected Pico"""
        if not self.client or not self.client.is_connected:
            print("Not connected to any device")
            return False
            
        try:
            # Create command string: "MENU:POS:NEG"
            command = f"{menu}:{pos}:{neg}"
            command_bytes = command.encode('utf-8')
            
            # Write to the RX characteristic - exactly like controller.py
            await self.client.write_gatt_char(UART_RX_CHAR_UUID, command_bytes)
            print(f"✓ Sent emoji command: '{command}'")
            return True
            
        except Exception as e:
            print(f"✗ Error sending emoji command '{command}': {e}")
            return False
    
    async def disconnect(self):
        """Disconnect from the device"""
        if self.client and self.client.is_connected:
            await self.client.disconnect()
            print("Disconnected from Pico")
            self.connected = False

