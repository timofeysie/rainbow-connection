from PiicoDev_RFID import PiicoDev_RFID
from PiicoDev_Unified import sleep_ms
from PiicoDev_SSD1306 import *
import network   # handles connecting to WiFi
import urequests # handles making and servicing network requests
import time

# PiCockpit.com

import bluetooth
import random
import struct
import time
from machine import Pin
from ble_advertising import advertising_payload

from micropython import const

_IRQ_CENTRAL_CONNECT = const(1)
_IRQ_CENTRAL_DISCONNECT = const(2)
_IRQ_GATTS_WRITE = const(3)

_FLAG_READ = const(0x0002)
_FLAG_WRITE_NO_RESPONSE = const(0x0004)
_FLAG_WRITE = const(0x0008)
_FLAG_NOTIFY = const(0x0010)

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

## Network test
ssid = '***'
password = '***'

# Connect to network
wlan = network.WLAN(network.STA_IF)
wlan.active(True)

# Attempt to connect to the network
wlan.connect(ssid, password)

# Wait for the connection to establish
time.sleep(10)

# Check if the connection was successful
if wlan.isconnected():
    print("Connected to the network")
else:
    print("Failed to connect to the network")

# Example urequests can also handle basic json support! Let's get the current time from a server
print("\n\n2. Querying the current GMT+0 time:")
r = urequests.get("http://date.jsontest.com") # Server that returns the current GMT+0 time.
print(r.json())

## RFID & Display
display = create_PiicoDev_SSD1306()

data = r.json()
date_str = str(data['date'])
time_str = str(data['time'])
display_str = date_str + " " + time_str
display.text(display_str, 0,0, 1)

rfid = PiicoDev_RFID()   # Initialise the RFID module

print('Place tag near the PiicoDev RFID Module')
print(rfid)
display.show()

class BLESimplePeripheral:
    def __init__(self, ble, name="mpy-uart"):
        self._ble = ble
        self._ble.active(True)
        self._ble.irq(self._irq)
        ((self._handle_tx, self._handle_rx),) = self._ble.gatts_register_services((_UART_SERVICE,))
        self._connections = set()
        self._write_callback = None
        self._payload = advertising_payload(name=name, services=[_UART_UUID])
        self._advertise()

    def _irq(self, event, data):
        if event == _IRQ_CENTRAL_CONNECT:
            conn_handle, _, _ = data
            print("New connection", conn_handle)
            self._connections.add(conn_handle)
        elif event == _IRQ_CENTRAL_DISCONNECT:
            conn_handle, _, _ = data
            print("Disconnected", conn_handle)
            self._connections.remove(conn_handle)
            self._advertise()
        elif event == _IRQ_GATTS_WRITE:
            conn_handle, value_handle = data
            value = self._ble.gatts_read(value_handle)
            if value_handle == self._handle_rx and self._write_callback:
                self._write_callback(value)

    def send(self, data):
        for conn_handle in self._connections:
            self._ble.gatts_notify(conn_handle, self._handle_tx, data)

    def is_connected(self):
        return len(self._connections) > 0

    def _advertise(self, interval_us=500000):
        print("Starting advertising")
        self._ble.gap_advertise(interval_us, adv_data=self._payload)

    def on_write(self, callback):
        self._write_callback = callback


def demo():
    led_onboard = Pin("LED", Pin.OUT)
    ble = bluetooth.BLE()
    p = BLESimplePeripheral(ble)

    def on_rx(v):
        print("RX", v)

    p.on_write(on_rx)

    i = 0
    while True:
        if rfid.tagPresent():    # if an RFID tag is present
            id = rfid.readID()   # get the id
            if (id == "5B:6F:B8:08"):
                display.fill(0)
                print("R12")
                display.text(display_str, 0,0, 1)
                display.text("R12 - Monkey", 0,15, 1)
            elif (id == "DB:93:B7:08"):
                display.fill(0)
                print("W3 - Clown")
                display.text(display_str, 0,0, 1)
                display.text("W3 - Clown", 0,15, 1)
            else:
                print(id)
                display.fill(0)
                display.text(display_str, 0,0, 1)
                display.text(id, 0,15, 1)
            display.show()

        # bluetooth demo
        if p.is_connected():
            led_onboard.on()
            for _ in range(3):
                data = str(i) + "_"
                print("TX", data)
                display.text(data, 0,30, 1)
                display.show()
                p.send(data)
                i += 1
        time.sleep_ms(100)


if __name__ == "__main__":
    demo()
