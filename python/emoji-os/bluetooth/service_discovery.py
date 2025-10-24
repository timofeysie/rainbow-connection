"""
BLE Service Discovery Debug Script
Connects to Pico and lists all available services and characteristics
"""

import asyncio
from bleak import BleakClient

# Device address from your successful connection
PICO_ADDRESS = "28:CD:C1:05:AB:A4"

async def discover_services():
    """Connect to Pico and discover all services and characteristics"""
    print("BLE Service Discovery Debug")
    print("=" * 40)
    print(f"Connecting to Pico at {PICO_ADDRESS}...")
    
    try:
        async with BleakClient(PICO_ADDRESS) as client:
            if not client.is_connected:
                print("Failed to connect!")
                return
                
            print("✓ Connected successfully!")
            print("\nDiscovering services and characteristics...")
            
            # Get all services
            services = client.services
            print(f"\nFound {len(services)} services:")
            print("-" * 60)
            
            for service in services:
                print(f"Service: {service.uuid}")
                print(f"  Description: {service.description}")
                
                # Get characteristics for this service
                characteristics = service.characteristics
                print(f"  Characteristics ({len(characteristics)}):")
                
                for char in characteristics:
                    print(f"    UUID: {char.uuid}")
                    print(f"    Properties: {char.properties}")
                    print(f"    Description: {char.description}")
                    print()
                
                print("-" * 60)
            
            print("\nLooking for Nordic UART Service...")
            nus_service_uuid = "6E400001-B5A3-F393-E0A9-E50E24DCCA9E"
            nus_rx_uuid = "6E400002-B5A3-F393-E0A9-E50E24DCCA9E"
            nus_tx_uuid = "6E400003-B5A3-F393-E0A9-E50E24DCCA9E"
            
            nus_service = None
            for service in services:
                if str(service.uuid).upper() == nus_service_uuid.upper():
                    nus_service = service
                    break
            
            if nus_service:
                print(f"✓ Found Nordic UART Service: {nus_service.uuid}")
                
                # Check for RX characteristic
                rx_char = None
                tx_char = None
                
                for char in nus_service.characteristics:
                    char_uuid = str(char.uuid).upper()
                    if char_uuid == nus_rx_uuid.upper():
                        rx_char = char
                        print(f"✓ Found RX characteristic: {char.uuid}")
                    elif char_uuid == nus_tx_uuid.upper():
                        tx_char = char
                        print(f"✓ Found TX characteristic: {char.uuid}")
                
                if not rx_char:
                    print(f"✗ RX characteristic not found! Expected: {nus_rx_uuid}")
                if not tx_char:
                    print(f"✗ TX characteristic not found! Expected: {nus_tx_uuid}")
                    
            else:
                print(f"✗ Nordic UART Service not found! Expected: {nus_service_uuid}")
                print("This means the Pico client.py is not properly setting up the UART service.")
            
    except Exception as e:
        print(f"Error: {e}")


if __name__ == "__main__":
    asyncio.run(discover_services())
