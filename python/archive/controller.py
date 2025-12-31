"""
BLE Controller for Raspberry Pi Zero 2 W
Acts as a BLE central that connects to Pico 2 W and sends commands
Enhanced with better error handling and connection stability
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


class BLEController:
    """BLE Central controller that connects to Pico and sends commands"""
    
    def __init__(self):
        self.client = None
        self.device_address = None
        
    async def scan_for_device(self, timeout=10):
        """Scan for the target Pico device"""
        print(f"Scanning for '{TARGET_DEVICE_NAME}' for {timeout} seconds...")
        print("Make sure your Pico is running client.py...")
        
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
    
    async def send_command_sequence(self):
        """Send a sequence of test commands"""
        print("\nSending command sequence...")
        
        for command in COMMANDS:
            success = await self.send_command(command)
            if success:
                await asyncio.sleep(1)  # Wait between commands
            else:
                print(f"Failed to send command: {command}")
                break
    
    async def interactive_mode(self):
        """Interactive mode for manual command sending"""
        print("\nInteractive mode - Enter commands manually:")
        print(f"Available commands: {', '.join(COMMANDS)}")
        print("Type 'quit' to exit")
        
        while True:
            try:
                command = input("\nEnter command: ").strip().upper()
                
                if command == "QUIT":
                    break
                elif command in COMMANDS:
                    await self.send_command(command)
                elif command == "":
                    continue
                else:
                    print(f"Unknown command: '{command}'")
                    print(f"Available commands: {', '.join(COMMANDS)}")
                    
            except KeyboardInterrupt:
                print("\nExiting interactive mode...")
                break


async def main():
    """Main function"""
    controller = BLEController()
    
    try:
        print("BLE Controller for Raspberry Pi Zero 2 W")
        print("=" * 50)
        
        # Scan for the Pico device
        if not await controller.scan_for_device():
            print("\nExiting - could not find target device")
            return
        
        # Connect to the device
        if not await controller.connect_to_device():
            print("\nExiting - could not connect to device")
            return
        
        # Send automatic command sequence
        await controller.send_command_sequence()
        
        # Wait a bit
        await asyncio.sleep(2)
        
        # Ask user if they want interactive mode
        print("\nWould you like to enter interactive mode? (y/n): ", end="")
        try:
            response = input().strip().lower()
            if response in ['y', 'yes']:
                await controller.interactive_mode()
        except KeyboardInterrupt:
            print("\nSkipping interactive mode...")
        
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
