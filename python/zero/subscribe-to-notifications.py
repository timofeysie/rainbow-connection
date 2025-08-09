import asyncio
from bleak import BleakClient

ADDRESS = "XX:XX:XX:XX:XX:XX"  # Replace with your gamepad's address
CHAR_UUID = "XXXXXXXX-XXXX-XXXX-XXXX-XXXXXXXXXXXX"  # Replace with correct UUID

def handle_notification(sender, data):
    print(f"Notification from {sender}: {data.hex()}")

async def main():
    async with BleakClient(ADDRESS) as client:
        await client.start_notify(CHAR_UUID, handle_notification)
        print("Listening for notifications... Press Ctrl+C to stop.")
        while True:
            await asyncio.sleep(1)

asyncio.run(main())