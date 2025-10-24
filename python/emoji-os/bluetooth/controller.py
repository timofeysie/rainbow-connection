"""
BLE Controller for Raspberry Pi Zero 2 W
Acts as a BLE central that connects to Pico 2 W and sends commands
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
        
        devices = await BleakScanner.discover(timeout=timeout)
        
        for device in devices:
            if device.name == TARGET_DEVICE_NAME:
                print(f"Found {TARGET_DEVICE_NAME} at address: {device.address}")
                self.device_address = device.address
                return True
                
        print(f"Could not find '{TARGET_DEVICE_NAME}'")
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
                print("Successfully connected!")
                return True
            else:
                print("Failed to connect")
                return False
                
        except Exception as e:
            print(f"Connection error: {e}")
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
            print(f"Sent command: '{command}'")
            return True
            
        except Exception as e:
            print(f"Error sending command '{command}': {e}")
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
        # Scan for the Pico device
        if not await controller.scan_for_device():
            print("Exiting - could not find target device")
            return
        
        # Connect to the device
        if not await controller.connect_to_device():
            print("Exiting - could not connect to device")
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
    print("BLE Controller for Raspberry Pi Zero 2 W")
    print("=" * 50)
    
    try:
        asyncio.run(main())
    except KeyboardInterrupt:
        print("\nController stopped by user")
    except Exception as e:
        print(f"Unexpected error: {e}")


if __name__ == "__main__":
    run_controller()
