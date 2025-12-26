"""
BLE Controller v1.3 for Raspberry Pi Zero 2 W
Acts as a BLE central that connects to Pico 2 W and sends commands
Enhanced with better error handling and connection stability
Uses direct test write instead of service discovery for automatic device finding
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
        """Scan for the target Pico device by name or service UUID"""
        print(f"Scanning for Pico device (preferred name: '{TARGET_DEVICE_NAME}')...")
        print("Will also search for Nordic UART Service if name doesn't match")
        print("Make sure your Pico is running client.py or client_enhanced.py...")
        
        # First, try scanning by service UUID (most reliable)
        print("\nAttempting to scan by service UUID...")
        try:
            devices = await BleakScanner.discover(
                timeout=timeout,
                service_uuids=[UART_SERVICE_UUID]
            )
            if devices:
                print(f"✓ Found {len(devices)} device(s) advertising Nordic UART Service:")
                for device in devices:
                    name = device.name or "(No Name)"
                    print(f"  - {name:<20} | {device.address}")
                    self.device_address = device.address
                    print(f"✓ Selected device: {name} at {self.device_address}")
                    return True
        except Exception as e:
            print(f"Service UUID scan failed: {e}")
        
        # Fallback: General scan and check for name match or verify service
        print(f"\nPerforming general scan for {timeout} seconds...")
        devices = await BleakScanner.discover(timeout=timeout)
        
        print(f"Found {len(devices)} BLE devices:")
        print("-" * 50)
        
        # First, check for exact name match
        for i, device in enumerate(devices, 1):
            name = device.name or "(No Name)"
            print(f"{i:2d}. {name:<20} | {device.address}")
            
            if device.name == TARGET_DEVICE_NAME:
                print(f"    *** FOUND TARGET DEVICE BY NAME! ***")
                self.device_address = device.address
                print("-" * 50)
                print(f"✓ Found {TARGET_DEVICE_NAME} at address: {self.device_address}")
                return True
        
        print("-" * 50)
        
        # If no name match, try to find by service UUID by connecting to candidates
        print("\nNo exact name match found. Checking devices for Nordic UART Service...")
        candidate_devices = []
        
        # Look for devices that might be the Pico (check metadata if available)
        for device in devices:
            name = device.name or "(No Name)"
            # Check if device metadata indicates it has the service
            if hasattr(device, 'metadata') and device.metadata:
                services = device.metadata.get('uuids', [])
                if UART_SERVICE_UUID.lower() in [s.lower() for s in services]:
                    candidate_devices.append(device)
                    print(f"  Candidate: {name} ({device.address}) - has UART service in metadata")
        
        # If we found candidates via metadata, use the first one
        if candidate_devices:
            device = candidate_devices[0]
            name = device.name or "(No Name)"
            self.device_address = device.address
            print(f"✓ Selected candidate device: {name} at {self.device_address}")
            return True
        
        # Last resort: try connecting to devices and test write (avoids service discovery issues)
        print("\nTesting devices by attempting connection and test write...")
        print("(This may take a moment - checking up to 15 devices)...")
        print("Note: This method connects and tries to write a test command")
        
        # Known Pico MAC addresses from previous successful connections (for priority)
        known_pico_addresses = ["28:CD:C1:05:AB:A4", "28:CD:C1:07:2C:E8", "2C:CF:67:05:A4:F4"]
        
        # First, check known addresses (faster)
        for known_addr in known_pico_addresses:
            for device in devices:
                if device.address.upper() == known_addr.upper():
                    name = device.name or "(No Name)"
                    print(f"\n  Testing known address: {name} ({device.address})...", end=" ")
                    if await self._test_device_connection(device.address):
                        self.device_address = device.address
                        print(f"✓ FOUND!")
                        print(f"\n✓ Found Pico device (known address):")
                        print(f"  Name: {name}")
                        print(f"  Address: {self.device_address}")
                        return True
                    break
        
        # Then test all other devices
        for device in devices[:15]:  # Check up to 15 devices
            # Skip if we already checked this as a known address
            if device.address.upper() in [a.upper() for a in known_pico_addresses]:
                continue
                
            name = device.name or "(No Name)"
            print(f"  Testing {name} ({device.address})...", end=" ")
            if await self._test_device_connection(device.address):
                self.device_address = device.address
                print(f"✓ FOUND!")
                print(f"\n✓ Found Pico device with Nordic UART Service:")
                print(f"  Name: {name}")
                print(f"  Address: {self.device_address}")
                return True
        
        print(f"\n✗ Could not find Pico device")
        print("\nTroubleshooting tips:")
        print("1. Make sure Pico is running client.py or client_enhanced.py")
        print("2. Check that Pico shows 'Starting advertising...'")
        print("3. Try moving devices closer together")
        print("4. Restart both devices")
        print("5. Device may be advertising with a different name")
        return False
    
    async def _test_device_connection(self, address):
        """Test if a device has the Nordic UART Service by attempting a test write"""
        test_client = None
        try:
            test_client = BleakClient(address)
            await test_client.connect(timeout=3.0)
            
            # Try to write a test command directly to the RX characteristic
            # If this succeeds, we know the device has the UART service
            test_command = b"STATUS"  # Non-destructive test command
            try:
                await test_client.write_gatt_char(UART_RX_CHAR_UUID, test_command)
                # If write succeeded, this is likely our device
                await test_client.disconnect()
                return True
            except Exception as write_error:
                # Write failed - not the right device or characteristic doesn't exist
                await test_client.disconnect()
                return False
                
        except asyncio.TimeoutError:
            if test_client:
                try:
                    await test_client.disconnect()
                except:
                    pass
            return False
        except Exception as e:
            # Connection failed or other error
            if test_client:
                try:
                    await test_client.disconnect()
                except:
                    pass
            return False
    
    async def connect_to_device(self):
        """Connect to the discovered Pico device"""
        if not self.device_address:
            print("No device address available. Run scan_for_device() first.")
            return False
            
        try:
            print(f"Connecting to {self.device_address}...")
            self.client = BleakClient(self.device_address)
            await self.client.connect(timeout=10.0)  # Increased timeout
            
            if self.client.is_connected:
                print("✓ Successfully connected!")
                # Verify the service exists
                try:
                    services = await self.client.get_services()
                    uart_found = False
                    for service in services:
                        if service.uuid.lower() == UART_SERVICE_UUID.lower():
                            uart_found = True
                            print(f"✓ Verified Nordic UART Service is available")
                            break
                    if not uart_found:
                        print("⚠ Warning: Connected but Nordic UART Service not found!")
                        print("  This might not be the correct device.")
                except Exception as e:
                    print(f"⚠ Warning: Could not verify services: {e}")
                
                return True
            else:
                print("✗ Failed to connect (not connected after connect() call)")
                return False
                
        except asyncio.TimeoutError:
            print(f"✗ Connection timeout - device may not be in range or not advertising")
            return False
        except Exception as e:
            error_msg = str(e)
            print(f"✗ Connection error: {error_msg}")
            if "not found" in error_msg.lower() or "not available" in error_msg.lower():
                print("  → Device may not be advertising or is out of range")
            elif "timeout" in error_msg.lower():
                print("  → Connection timed out - device may be busy or not responding")
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
    import sys
    
    controller = BLEController()
    
    try:
        print("BLE Controller v1.3 for Raspberry Pi Zero 2 W")
        print("=" * 50)
        
        # Allow manual MAC address specification
        if len(sys.argv) > 1:
            manual_address = sys.argv[1].upper()
            print(f"Using manually specified MAC address: {manual_address}")
            print("Skipping scan and connecting directly...")
            controller.device_address = manual_address
        else:
            # Scan for the Pico device
            if not await controller.scan_for_device():
                print("\n" + "=" * 50)
                print("TROUBLESHOOTING:")
                print("1. Make sure client_enhanced.py is running on the Pico")
                print("2. Check Pico output shows 'Starting advertising...'")
                print("3. Try power cycling the Pico (unplug and replug USB)")
                print("4. Try running with a known MAC address:")
                print("   python controller-1.py 2C:CF:67:05:A4:F4")
                print("   (or try: python controller-1.py 28:CD:C1:05:AB:A4)")
                print("=" * 50)
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
