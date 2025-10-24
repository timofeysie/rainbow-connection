"""
BLE Client Debug Version for Raspberry Pi Pico 2 W
Enhanced with detailed service registration debugging
"""

import bluetooth
import time
from machine import Pin
from ble_advertising import advertising_payload
from micropython import const

# BLE constants
_IRQ_CENTRAL_CONNECT = const(1)
_IRQ_CENTRAL_DISCONNECT = const(2)
_IRQ_GATTS_WRITE = const(3)

_FLAG_READ = const(0x0002)
_FLAG_WRITE_NO_RESPONSE = const(0x0004)
_FLAG_WRITE = const(0x0008)
_FLAG_NOTIFY = const(0x0010)

# Nordic UART Service UUIDs
_UART_UUID = bluetooth.UUID("6E400001-B5A3-F393-E0A9-E50E24DCCA9E")
_UART_TX = (
    bluetooth.UUID("6E400003-B5A3-F393-E0A9-E50E24DCCA9E"),
    _FLAG_READ | _FLAG_NOTIFY,
)
_UART_RX = (
    bluetooth.UUID("6E400002-B5A3-F393-E0A9-E50E24DCCA9E"),
    _FLAG_WRITE | _FLAG_WRITE_NO_RESPONSE,
)
_UART_SERVICE = (
    _UART_UUID,
    (_UART_TX, _UART_RX),
)


class BLESimplePeripheralDebug:
    """BLE Peripheral with enhanced debugging"""
    
    def __init__(self, ble, name="Pico-Client"):
        print("Initializing BLE Peripheral...")
        
        self._ble = ble
        print("Activating BLE...")
        self._ble.active(True)
        
        print("Setting up IRQ handler...")
        self._ble.irq(self._irq)
        
        print("Registering UART service...")
        print(f"Service UUID: {_UART_UUID}")
        print(f"TX Characteristic: {_UART_TX[0]}")
        print(f"RX Characteristic: {_UART_RX[0]}")
        
        try:
            ((self._handle_tx, self._handle_rx),) = self._ble.gatts_register_services((_UART_SERVICE,))
            print(f"✓ Service registered successfully!")
            print(f"TX handle: {self._handle_tx}")
            print(f"RX handle: {self._handle_rx}")
        except Exception as e:
            print(f"✗ Service registration failed: {e}")
            return
        
        self._connections = set()
        self._write_callback = None
        
        print("Creating advertising payload...")
        self._payload = advertising_payload(name=name, services=[_UART_UUID])
        print(f"Advertising payload length: {len(self._payload)}")
        
        print("Starting advertising...")
        self._advertise()

    def _irq(self, event, data):
        """Handle BLE events"""
        if event == _IRQ_CENTRAL_CONNECT:
            conn_handle, _, _ = data
            print(f"✓ New connection: {conn_handle}")
            self._connections.add(conn_handle)
        elif event == _IRQ_CENTRAL_DISCONNECT:
            conn_handle, _, _ = data
            print(f"✗ Disconnected: {conn_handle}")
            self._connections.remove(conn_handle)
            self._advertise()
        elif event == _IRQ_GATTS_WRITE:
            conn_handle, value_handle = data
            print(f"Write event - Handle: {value_handle}, Expected RX: {self._handle_rx}")
            value = self._ble.gatts_read(value_handle)
            if value_handle == self._handle_rx and self._write_callback:
                print(f"Calling write callback with data: {value}")
                self._write_callback(value)

    def send(self, data):
        """Send data to connected central devices"""
        for conn_handle in self._connections:
            self._ble.gatts_notify(conn_handle, self._handle_tx, data)

    def is_connected(self):
        """Check if any central device is connected"""
        return len(self._connections) > 0

    def _advertise(self, interval_us=500000):
        """Start advertising the BLE service"""
        print(f"Starting advertising with interval {interval_us}μs...")
        self._ble.gap_advertise(interval_us, adv_data=self._payload)

    def on_write(self, callback):
        """Set callback for when data is written to RX characteristic"""
        self._write_callback = callback


def handle_command(command_data):
    """Handle incoming commands from central device"""
    try:
        # Decode the command
        command = command_data.decode('utf-8').strip()
        print(f"✓ Received command: '{command}'")
        
        # Process different commands
        if command == "ON":
            print("Command: Turning ON")
            led.on()
        elif command == "OFF":
            print("Command: Turning OFF")
            led.off()
        elif command == "STATUS":
            print("Command: STATUS requested")
            print(f"LED is {'ON' if led.value() else 'OFF'}")
        elif command == "BLINK":
            print("Command: BLINK")
            for _ in range(3):
                led.on()
                time.sleep(0.2)
                led.off()
                time.sleep(0.2)
        else:
            print(f"Unknown command: '{command}'")
            
    except Exception as e:
        print(f"✗ Error processing command: {e}")


def main():
    """Main function to run the BLE client"""
    global led
    
    print("BLE Client Debug Version")
    print("=" * 40)
    
    # Initialize LED for visual feedback
    led = Pin("LED", Pin.OUT)
    led.off()
    
    # Initialize BLE
    print("Initializing BLE...")
    ble = bluetooth.BLE()
    
    print("Creating peripheral...")
    peripheral = BLESimplePeripheralDebug(ble, "Pico-Client")
    
    # Set up command handler
    print("Setting up command handler...")
    peripheral.on_write(handle_command)
    
    print("\nBLE Client started successfully!")
    print("Waiting for connections...")
    print("Available commands: ON, OFF, STATUS, BLINK")
    print("Press Ctrl+C to stop")
    
    # Main loop
    try:
        while True:
            if peripheral.is_connected():
                # LED indicates connection status
                led.on()
            else:
                # Blink LED slowly when not connected
                led.on()
                time.sleep(0.5)
                led.off()
                time.sleep(0.5)
                continue
                
            time.sleep(0.1)
            
    except KeyboardInterrupt:
        print("\nShutting down...")
        led.off()


if __name__ == "__main__":
    main()
