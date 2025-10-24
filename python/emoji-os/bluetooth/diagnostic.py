"""
BLE Diagnostic Script for Raspberry Pi Zero 2 W
Helps troubleshoot BLE discovery issues
"""

import asyncio
import time
from bleak import BleakScanner, BleakClient

async def scan_all_devices(timeout=15):
    """Scan for all BLE devices and show detailed information"""
    print(f"Scanning for ALL BLE devices for {timeout} seconds...")
    print("=" * 60)
    
    devices = await BleakScanner.discover(timeout=timeout)
    
    print(f"\nFound {len(devices)} devices:")
    print("-" * 60)
    
    pico_devices = []
    
    for i, device in enumerate(devices, 1):
        name = device.name if device.name else "Unknown"
        address = device.address
        rssi = device.rssi
        
        print(f"{i:2d}. Name: '{name}'")
        print(f"    Address: {address}")
        print(f"    RSSI: {rssi} dBm")
        
        # Check if this might be our Pico
        if "pico" in name.lower() or "client" in name.lower() or name == "Pico-Client":
            pico_devices.append(device)
            print(f"    *** POTENTIAL PICO DEVICE ***")
        print()
    
    return devices, pico_devices

async def test_connection(address):
    """Test connection to a specific device"""
    print(f"\nTesting connection to {address}...")
    try:
        async with BleakClient(address, timeout=10.0) as client:
            print(f"✓ Successfully connected to {address}")
            
            print("\nServices and characteristics:")
            for service in client.services:
                print(f"  Service: {service.uuid}")
                for char in service.characteristics:
                    print(f"    Characteristic: {char.uuid} (properties: {char.properties})")
            
            return True
    except Exception as e:
        print(f"✗ Failed to connect to {address}: {e}")
        return False

async def scan_with_retries(max_retries=3):
    """Scan multiple times to catch intermittent advertising"""
    print("Performing multiple scans to catch intermittent advertising...")
    
    all_devices = []
    for attempt in range(max_retries):
        print(f"\nScan attempt {attempt + 1}/{max_retries}")
        devices = await BleakScanner.discover(timeout=10)
        all_devices.extend(devices)
        
        # Look for Pico devices in this scan
        pico_found = [d for d in devices if d.name == "Pico-Client"]
        if pico_found:
            print(f"✓ Found Pico-Client in attempt {attempt + 1}")
            return pico_found[0]
        
        if attempt < max_retries - 1:
            print("Waiting 2 seconds before next scan...")
            await asyncio.sleep(2)
    
    # Remove duplicates
    unique_devices = {}
    for device in all_devices:
        unique_devices[device.address] = device
    
    print(f"\nTotal unique devices found across {max_retries} scans: {len(unique_devices)}")
    return None

async def main():
    """Main diagnostic function"""
    print("BLE Diagnostic Tool for Raspberry Pi Zero 2 W")
    print("=" * 50)
    
    # First, do a comprehensive scan
    all_devices, potential_picos = await scan_all_devices()
    
    if potential_picos:
        print(f"\nFound {len(potential_picos)} potential Pico devices:")
        for device in potential_picos:
            print(f"  - {device.name} at {device.address}")
        
        # Test connection to the first potential Pico
        if await test_connection(potential_picos[0].address):
            print("\n✓ Connection test successful!")
            return
    
    # If no Pico found, try multiple scans
    print("\nNo Pico-Client found in initial scan. Trying multiple scans...")
    pico_device = await scan_with_retries()
    
    if pico_device:
        print(f"\n✓ Found Pico-Client: {pico_device.address}")
        await test_connection(pico_device.address)
    else:
        print("\n✗ Could not find Pico-Client device")
        print("\nTroubleshooting suggestions:")
        print("1. Ensure Pico is running client.py and shows 'Starting advertising...'")
        print("2. Check that Pico and Zero are within 5 meters of each other")
        print("3. Try restarting both devices")
        print("4. Check for Bluetooth interference from other devices")
        print("5. Verify MicroPython BLE support on Pico")

if __name__ == "__main__":
    try:
        asyncio.run(main())
    except KeyboardInterrupt:
        print("\nDiagnostic stopped by user")
    except Exception as e:
        print(f"Unexpected error: {e}")
