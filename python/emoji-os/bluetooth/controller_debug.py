"""
BLE Controller Debug Version for Raspberry Pi Zero 2 W
Enhanced with detailed scanning and debugging output
"""

import asyncio
import time
from bleak import BleakScanner, BleakClient
from bleak.backends.characteristic import BleakGATTCharacteristic

# Nordic UART Service UUIDs
UART_SERVICE_UUID = "6E400001-B5A3-F393-E0A9-E50E24DCCA9E"
UART_RX_CHAR_UUID = "6E400002-B5A3-F393-E0A9-E50E24DCCA9E"  # Write characteristic
UART_TX_CHAR_UUID = "6E400003-B5A3-F393-E0A9-E50E24DCCA9E"  # Notify characteristic

# Device name to look for
TARGET_DEVICE_NAME = "Pico-Client"

# Available commands
COMMANDS = ["ON", "OFF", "STATUS", "BLINK"]


class BLEControllerDebug:
    """BLE Central controller with enhanced debugging"""
    
    def __init__(self):
        self.client = None
        self.device_address = None
        
    async def scan_for_device(self, timeout=15):
        """Scan for the target Pico device with detailed output"""
        print(f"Scanning for '{TARGET_DEVICE_NAME}' for {timeout} seconds...")
        print("Make sure your Pico is running client.py and advertising...")
        
        devices = await BleakScanner.discover(timeout=timeout)
        
        print(f"\nFound {len(devices)} total BLE devices:")
        print("-" * 60)
        
        target_found = False
        for i, device in enumerate(devices, 1):
            name = device.name or "(No Name)"
            print(f"{i:2d}. Name: {name:<20} | Address: {device.address} | RSSI: {device.rssi}")
            
            if device.name == TARGET_DEVICE_NAME:
                print(f"    *** FOUND TARGET DEVICE! ***")
                self.device_address = device.address
                target_found = True
        
        print("-" * 60)
        
        if target_found:
            print(f"✓ Found {TARGET_DEVICE_NAME} at address: {self.device_address}")
            return True
        else:
            print(f"✗ Could not find '{TARGET_DEVICE_NAME}'")
            print("\nTroubleshooting tips:")
            print("1. Make sure Pico is running client.py")
            print("2. Check that Pico shows 'Starting advertising...'")
            print("3. Try moving devices closer together")
            print("4. Restart both devices")
            return False
    
    async def connect_to_device(self):
        """Connect to the discovered Pico device"""
        if not self.device_address:
            print("No device address available. Run scan_for_device() first.")
            return False
            
        try:
            print(f"Connecting to {self.device_address}...")
            self.client = BleakClient(self.device_address)
            await self.client.connect()
            
            if self.client.is_connected:
                print("✓ Successfully connected!")
                return True
            else:
                print("✗ Failed to connect")
                return False
                
        except Exception as e:
            print(f"✗ Connection error: {e}")
            return False
    
    async def send_command(self, command):
        """Send a command to the connected Pico"""
        if not self.client or not self.client.is_connected:
            print("Not connected to any device")
            return False
            
        try:
            # Convert command to bytes
            command_bytes = command.encode('utf-8')
            
            # Write to the RX characteristic
            await self.client.write_gatt_char(UART_RX_CHAR_UUID, command_bytes)
            print(f"✓ Sent command: '{command}'")
            return True
            
        except Exception as e:
            print(f"✗ Error sending command '{command}': {e}")
            return False
    
    async def disconnect(self):
        """Disconnect from the device"""
        if self.client and self.client.is_connected:
            await self.client.disconnect()
            print("Disconnected")


async def main():
    """Main function with enhanced debugging"""
    controller = BLEControllerDebug()
    
    try:
        print("BLE Controller Debug Version")
        print("=" * 50)
        
        # Scan for the Pico device
        if not await controller.scan_for_device():
            print("\nExiting - could not find target device")
            return
        
        # Connect to the device
        if not await controller.connect_to_device():
            print("\nExiting - could not connect to device")
            return
        
        # Send a simple test command
        print("\nSending test command...")
        await controller.send_command("STATUS")
        await asyncio.sleep(1)
        
        print("\nTest completed successfully!")
        
    except KeyboardInterrupt:
        print("\nShutting down...")
        
    finally:
        # Clean up
        await controller.disconnect()


def run_controller():
    """Entry point for running the controller"""
    try:
        asyncio.run(main())
    except KeyboardInterrupt:
        print("\nController stopped by user")
    except Exception as e:
        print(f"Unexpected error: {e}")


if __name__ == "__main__":
    run_controller()
