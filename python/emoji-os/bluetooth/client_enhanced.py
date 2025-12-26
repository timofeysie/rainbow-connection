"""
BLE Client enhanced for Raspberry Pi Pico 2 W v1.1.0
Acts as a BLE peripheral that receives emoji commands from a central device (Pi Zero 2 W)
Enhanced to handle emoji selection commands in format "MENU:POS:NEG"
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


class BLESimplePeripheral:
    """BLE Peripheral that advertises UART service and receives commands"""
    
    def __init__(self, ble, name="Pico-Client"):
        self._ble = ble
        # Force BLE stack reset to clear cached name
        self._ble.active(False)
        time.sleep(0.1)
        self._ble.active(True)
        time.sleep(0.1)
        self._ble.irq(self._irq)
        
        # Register the UART service
        ((self._handle_tx, self._handle_rx),) = self._ble.gatts_register_services((_UART_SERVICE,))
        
        self._connections = set()
        self._write_callback = None
        self._payload = advertising_payload(name=name, services=[_UART_UUID])
        self._advertise()

    def _irq(self, event, data):
        """Handle BLE events"""
        if event == _IRQ_CENTRAL_CONNECT:
            conn_handle, _, _ = data
            print(f"✓ Connected: {conn_handle}")
            self._connections.add(conn_handle)
        elif event == _IRQ_CENTRAL_DISCONNECT:
            conn_handle, _, _ = data
            print(f"✗ Disconnected: {conn_handle}")
            self._connections.remove(conn_handle)
            # Restart advertising after disconnect
            self._advertise()
        elif event == _IRQ_GATTS_WRITE:
            conn_handle, value_handle = data
            value = self._ble.gatts_read(value_handle)
            if value_handle == self._handle_rx and self._write_callback:
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
        print("Starting advertising...")
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
        
        # Check if this is an emoji command (format: "MENU:POS:NEG")
        if ':' in command:
            try:
                parts = command.split(':')
                if len(parts) == 3:
                    menu = int(parts[0])
                    pos = int(parts[1])
                    neg = int(parts[2])
                    
                    print(f"Emoji Command - Menu: {menu}, Pos: {pos}, Neg: {neg}")
                    
                    # Handle emoji selection
                    handle_emoji_selection(menu, pos, neg)
                    return
            except ValueError:
                print(f"Invalid emoji command format: '{command}'")
        
        # Process legacy commands
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


def handle_emoji_selection(menu, pos, neg):
    """Handle emoji selection from the Pi Zero"""
    print(f"Processing emoji selection:")
    print(f"  Menu: {menu} ({get_menu_name(menu)})")
    print(f"  Position: {pos}")
    print(f"  Negative: {neg}")
    
    # Visual feedback with LED
    # Blink LED to indicate emoji received
    for _ in range(2):
        led.on()
        time.sleep(0.1)
        led.off()
        time.sleep(0.1)
    
    # Here you would typically:
    # 1. Display the selected emoji on an LCD screen
    # 2. Play animations
    # 3. Control other hardware based on the selection
    
    # For now, we'll just provide feedback
    if menu == 0:  # Emojis menu
        if pos > 0:
            emoji_name = get_positive_emoji_name(pos)
            print(f"  Selected positive emoji: {emoji_name}")
        elif neg > 0:
            emoji_name = get_negative_emoji_name(neg)
            print(f"  Selected negative emoji: {emoji_name}")
    elif menu == 1:  # Animations menu
        if pos > 0:
            print(f"  Selected positive animation: {get_positive_animation_name(pos)}")
        elif neg > 0:
            print(f"  Selected negative animation: {get_negative_animation_name(neg)}")


def get_menu_name(menu):
    """Get the name of the menu"""
    menu_names = ["Emojis", "Animations", "Characters", "Other"]
    if 0 <= menu < len(menu_names):
        return menu_names[menu]
    return "Unknown"


def get_positive_emoji_name(pos):
    """Get the name of the positive emoji"""
    emoji_names = ["", "Regular", "Happy", "Wry", "Heart"]
    if 1 <= pos < len(emoji_names):
        return emoji_names[pos]
    return "Unknown"


def get_negative_emoji_name(neg):
    """Get the name of the negative emoji"""
    emoji_names = ["", "Thick Lips", "Sad", "Angry", "Green Monster"]
    if 1 <= neg < len(emoji_names):
        return emoji_names[neg]
    return "Unknown"


def get_positive_animation_name(pos):
    """Get the name of the positive animation"""
    animation_names = ["", "Fireworks"]
    if 1 <= pos < len(animation_names):
        return animation_names[pos]
    return "Unknown"


def get_negative_animation_name(neg):
    """Get the name of the negative animation"""
    animation_names = ["", "Rain"]
    if 1 <= neg < len(animation_names):
        return animation_names[neg]
    return "Unknown"


def main():
    """Main function to run the BLE client"""
    global led
    
    print("BLE Client for Raspberry Pi Pico 2 W v1.1.0 - Enhanced for Emoji Commands")
    print("Device Name: Pico-Client")
    print("=" * 70)
    
    # Initialize LED for visual feedback
    led = Pin("LED", Pin.OUT)
    led.off()
    
    # Initialize BLE
    ble = bluetooth.BLE()
    peripheral = BLESimplePeripheral(ble, "Pico-Client")
    
    # Set up command handler
    peripheral.on_write(handle_command)
    
    print("BLE Client started")
    print("Waiting for connections...")
    print("Supports emoji commands in format: 'MENU:POS:NEG'")
    print("Legacy commands: ON, OFF, STATUS, BLINK")
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
