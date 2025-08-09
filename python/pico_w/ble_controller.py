# BLE Controller - much simpler than WiFi
import asyncio
import aioble
import bluetooth
import json
import struct
from machine import Pin

# Your pin definitions here...

_CONTROLLER_SERVICE_UUID = bluetooth.UUID("12345678-1234-1234-1234-123456789abc")
_CONTROLLER_CHAR_UUID = bluetooth.UUID("87654321-4321-4321-4321-cba987654321")

async def ble_controller():
    # Register the service
    service = aioble.Service(_CONTROLLER_SERVICE_UUID)
    characteristic = aioble.Characteristic(service, _CONTROLLER_CHAR_UUID, notify=True)
    aioble.register_services(service)
    
    # Start advertising
    await aioble.advertise(250_000, name="PicoController")
    print("BLE Controller advertising...")
    
    # Wait for connection and send data... 