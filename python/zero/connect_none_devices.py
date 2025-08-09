import asyncio
from bleak import BleakScanner, BleakClient

async def try_connect(address):
    print(f"\nTrying to connect to device at address: {address}")
    try:
        async with BleakClient(address, timeout=10.0) as client:
            print(f"Connected to {address}")
            print("Services and characteristics:")
            for service in client.services:
                print(f"  Service: {service}")
                for char in service.characteristics:
                    print(f"    Characteristic: {char} (properties: {char.properties})")
            return True
    except Exception as e:
        print(f"Failed to connect to {address}: {e}")
        return False

async def main():
    print("Scanning for 20 seconds...")
    devices = await BleakScanner.discover(timeout=20)
    none_name_devices = [d for d in devices if d.name is None]
    print(f"Found {len(none_name_devices)} devices with name None.")
    for d in none_name_devices:
        print(f"  Address: {d.address} (RSSI: {d.rssi})")
    for d in none_name_devices:
        await try_connect(d.address)

if __name__ == "__main__":
    asyncio.run(main())