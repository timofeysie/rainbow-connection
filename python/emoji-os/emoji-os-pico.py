# emoji os v0.1.5
import glowbit
from machine import Pin
import time
from emojis import *

from PiicoDev_RFID import PiicoDev_RFID
from PiicoDev_Unified import sleep_ms
from PiicoDev_SSD1306 import *
import network   # handles connecting to WiFi
import urequests # handles making and servicing network requests
import time
import secrets

# NFC & Bluetooth setup
import bluetooth
import random
import struct
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


# Connect to network
wlan = network.WLAN(network.STA_IF)
wlan.active(True)

# Attempt to connect to the network
wlan.connect(secrets.ssid, secrets.password)

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

## Emoji OS
matrix = glowbit.matrix8x8()
matrix.pixelsFill(matrix.black())
button1 = Pin(22, Pin.IN, Pin.PULL_DOWN)
button2 = Pin(21, Pin.IN, Pin.PULL_DOWN)
button3 = Pin(20, Pin.IN, Pin.PULL_DOWN)
buzzer = Pin(11, Pin.OUT)

menu = 0
pos = 0
neg = 0
state = "none" # start end or none
# preserve the previous state for pos/neg flipping
prev_menu = 0
prev_pos = 0
prev_neg = 0
prev_state = "none" # or done
pause = 0.2

def check_menu():
    global menu
    if menu > 3:
        menu = 0
    if menu < 0:
        menu = 3

def check_pos():
    global pos
    if pos > 4:
        pos = 1

def check_neg():
    global neg
    if neg > 4:
        neg = 1

# drawing the menu could be considered a training mode
def draw_menu():
    global menu
    global pause
    if menu == 0:
        matrix.drawRectangleFill(3,0, 4,1, matrix.white()) # 1 center square
        matrix.pixelsShow()
        time.sleep(pause)
    if menu == 1:
        matrix.drawRectangleFill(3,2, 4,3, matrix.white()) # 1 center square
        matrix.pixelsShow()
        time.sleep(pause)
    if menu == 2:
        matrix.drawRectangleFill(3,4, 4,5, matrix.white()) # 1 center square
        matrix.pixelsShow()
        time.sleep(pause)
    if menu == 3:
        matrix.drawRectangleFill(3,6, 4,7, matrix.white()) # 1 center square
        matrix.pixelsShow()
        time.sleep(pause)

# draw the positive state value.  possibly we will hide these
# pos & neg start at 1.  0 means either one has not been selected
def draw_pos():
    global pos
    if pos == 1:
        matrix.drawRectangleFill(0,0, 1,1, matrix.green()) # 1 center square
        matrix.pixelsShow()
        time.sleep(pause)
    if pos == 2:
        matrix.drawRectangleFill(0,2, 1,3, matrix.green()) # 1 center square
        matrix.pixelsShow()
        time.sleep(pause)
    if pos == 3:
        matrix.drawRectangleFill(0,4, 1,5, matrix.green()) # 1 center square
        matrix.pixelsShow()
        time.sleep(pause)
    if pos == 4:
        matrix.drawRectangleFill(0,6, 1,7, matrix.green()) # 1 center square
        matrix.pixelsShow()
        time.sleep(pause)

def draw_neg():
    global neg
    if neg == 1:
        matrix.drawRectangleFill(5,0, 6,1, matrix.red()) # 1 center square
        matrix.pixelsShow()
        # time.sleep(0.5)
    if neg == 2:
        matrix.drawRectangleFill(5,2, 6,3, matrix.red()) # 1 center square
        matrix.pixelsShow()
        # time.sleep(0.5)
    if neg == 3:
        matrix.drawRectangleFill(5,4, 6,5, matrix.red()) # 1 center square
        matrix.pixelsShow()
        # time.sleep(0.5)
    if neg == 4:
        matrix.drawRectangleFill(5,6, 6,7, matrix.red()) # 1 center square
        matrix.pixelsShow()
        # time.sleep(0.5)

def reset_state():
    global state
    global menu
    global pos
    global neg
    global prev_state
    global prev_menu
    global prev_pos
    global prev_neg
    prev_state = "done"
    prev_menu = menu
    prev_pos = pos
    prev_neg = neg
    state = "none"
    menu = 0
    pos = 0
    neg = 0

def reset_prev():
    global prev_state
    global prev_menu
    global prev_pos
    global prev_neg
    prev_state = "none"
    prev_menu = 0
    prev_pos = 0
    prev_neg = 0
    
def buzz():
    buzzer.value(1)
    time.sleep(0.1)
    buzzer.value(0)

# draw the chosen emoji and reset values
def draw_emoji():
    global state
    global menu
    global pos
    global neg
    print ("draw emoji menu at", menu, "pos at", pos, "neg at", neg, "state", state)
    matrix = glowbit.matrix8x8(rateLimitCharactersPerSecond = 0.7)
    #==========
    #POSITIVE 0
    # regular
    if (menu == 0 and pos == 1):
        print("menu 0 pos 1 normal")
        regular()
    # happy
    if (menu == 0 and pos == 2):
        print("menu 0 pos 2 happy")
        happy()
    # wry
    if (menu == 0 and pos == 3):
        print("menu 0 pos 3 wry")
        wry()
    # heart bounce
    if (menu == 0 and pos == 4):
        print("menu 0 pos 4 heart bounce")
        heartBounce()
    # NEGATIVE 0
    # thick lips
    if (menu == 0 and neg == 1):
        print("menu 0 neg 1 thick lips")
        thickLips()
    # sad
    if (menu == 0 and neg == 2):
        print("menu 0 neg 2 sad")
        sad()
    # angry
    if (menu == 0 and neg == 3):
        print("menu 0 neg 3 angry")
        angry()
    # monster
    if (menu == 0 and neg == 4):
        print("menu 0 neg 4 green monster")
        greenMonster()
    #==========
    #POSITIVE 1
    # fireworks
    if (menu == 1 and pos == 1):
        print("menu 1 pos 1 fireworks " + state)
        matrix = glowbit.matrix8x8(rateLimitCharactersPerSecond = 1)
        matrix.fireworks()
    # circularRainbow
    if (menu == 1 and pos == 2):
        print("menu 1 pos 2 circularRainbow")
        matrix = glowbit.matrix8x8(rateLimitCharactersPerSecond = 20)
        matrix.circularRainbow()
    # scroll_large_image
    if (menu == 1 and pos == 3):
        print("menu 1 pos 3 scroll_large_image")
        print("scrolling")
        scroll_large_image()
    # chakana
    if (menu == 1 and pos == 4):
        print("menu 1 pos 4 chacana")
        chakana()
    # NEGATIVE 1
    # rain
    if (menu == 1 and neg == 1):
        print("menu 1 neg 1 rain")
        matrix = glowbit.matrix8x8(rateLimitCharactersPerSecond = 5)
        matrix.rain()
    # ??
    if (menu == 1 and neg == 2):
        print("menu 1 neg 2 ")
        # sad()
    # ??
    if (menu == 1 and neg == 3):
        print("menu 1 neg 3")
        # angry()
    # ??
    if (menu == 1 and neg == 4):
        print("menu 1 neg 4 green monster")
        #greenMonster()
    #==========
    #POSITIVE 2
    # finn
    if (menu == 2 and pos == 1):
        print("menu 2 pos 1 finn")
        finn()
    # pikachu
    if (menu == 2 and pos == 2):
        print("menu 2 pos 2 pikachu")
        pikachu()
    # crab
    if (menu == 2 and pos == 3):
        print("menu 2 pos 2 crab")
        crab()
    # frog
    if (menu == 2 and pos == 4):
        print("menu 2 pos 2 frog")
        frog()
    # NEGATIVE 2
    # bald
    if (menu == 2 and neg == 1):
        print("menu 2 neg 1 bald")
        bald()
    # surprise
    if (menu == 2 and neg == 2):
        print("menu 2 neg 2 surprise")
        surprise()
    #==========
    #POSITIVE 3
    # circle
    if (menu == 3 and pos == 1):
        print("menu 3 pos 1 circle")
        matrix.drawCircle(3, 3, 3, matrix.blue())
        matrix.pixelsShow()
    # yes
    if (menu == 3 and pos == 2):
        print("menu 3 pos 2 pikachu")
        matrix.addTextScroll("YES")
        while matrix.scrollingText == True:
            matrix.updateTextScroll()
            matrix.pixelsShow()
    # Somi
    if (menu == 3 and pos == 3):
        print("menu 3 pos 2 pikachu")
        matrix.addTextScroll("Somi")
        while matrix.scrollingText == True:
            matrix.updateTextScroll()
            matrix.pixelsShow()
    # NEGATIVE 3
    # X
    if (menu == 3 and neg == 1):
        print("menu 3 neg 1")
        matrix.drawLine(0, 0, 7, 7, matrix.red())
        matrix.drawLine(0, 7, 7, 0, matrix.red())
        matrix.pixelsShow()
    # no
    if (menu == 3 and neg == 2):
        print("menu 3 neg 2")
        matrix.addTextScroll("NO")
        while matrix.scrollingText == True:
            matrix.updateTextScroll()
            matrix.pixelsShow()
    else:
        # do we need this in scrolling mode?
        reset_state()


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

led_onboard = Pin("LED", Pin.OUT)
ble = bluetooth.BLE()
p = BLESimplePeripheral(ble)

def on_rx(v):
    print("RX", v)

p.on_write(on_rx)

i = 0

while True:
    if rfid.tagPresent():  # if an RFID tag is present
        id = rfid.readID()   # get the id
        matrix.pixelsFill(matrix.black()) # clear the glowbit
        if (id == "5B:6F:B8:08"):
            display.fill(0)
            print("R12")
            display.text(display_str, 0,0, 1)
            display.text("R12 - Monkey", 0,15, 1)
            matrix.drawCircle(3, 3, 3, matrix.blue())
            matrix.pixelsShow()
        elif (id == "DB:93:B7:08"):
            display.fill(0)
            print("W3 - Clown")
            display.text(display_str, 0,0, 1)
            display.text("W3 - Clown", 0,15, 1)
            matrix.drawLine(0, 0, 7, 7, matrix.red())
            matrix.drawLine(0, 7, 7, 0, matrix.red())
            matrix.pixelsShow()
        else:
            print(id)
            display.fill(0)
            display.text(display_str, 0,0, 1)
            display.text(id, 0,15, 1)
        display.show()

        # bluetooth demo part from the first script
        if p.is_connected():
            led_onboard.on()
            for _ in range(3):
                data = str(i) + "_"
                print("TX", data)
                display.text(data, 0,30, 1)
                display.show()
                p.send(data)
                i += 1

    # blocks need to be in reverse order to stop the cascade throguh the conditions
    if button1.value():
        print('debug btn 1 menu ', menu, "pos", pos, "neg", neg, "state", state, "prev_pos", prev_pos, "prev_neg", prev_neg, "prev_state", prev_state)
        if state == "choosing":
            buzz()
            # increment positive choice
            pos = pos + 1
            neg = 0 # reset any negative value
            check_pos()
            print('button 1 pressed, menu ', menu, "pos", pos, "state", state)
            matrix.pixelsFill(matrix.black())
            draw_menu()
            draw_pos()
        if state == "start":
            buzz()
            # increment positive choice
            state = "choosing"
            pos = pos + 1
            check_pos()
            print('button 1 pressed, menu ', menu, "pos", pos, "state", state)
            matrix.pixelsFill(matrix.black())
            draw_menu()
            draw_pos()
        if prev_state == "done":
            if (prev_neg > 0):
                # reverse previous neg choice
                buzz()
                matrix.pixelsFill(matrix.black())
                pos = prev_neg
                neg = 0
                menu = prev_menu
                print('button 1 pressed again, menu ', menu, "pos", pos, "neg", neg, "state", state)
                draw_emoji()
            if (prev_pos > 0):
                # play last pos
                buzz()
                matrix.pixelsFill(matrix.black())
                pos = prev_pos
                neg = 0
                menu = prev_menu
                print('button 3 pressed again, menu ', menu, "pos", pos, "neg", neg, "state", state)
                draw_emoji()
    if button2.value():
        reset_prev()
        print('debug btn 2 menu ', menu, "pos", pos, "neg", neg, "state", state, "prev_pos", prev_pos, "prev_neg", prev_neg, "prev_state", prev_state)
        buzz()
        if state == "start":
            # start or increment main menu
            menu = menu + 1
            check_menu()
            matrix.pixelsFill(matrix.black())
            draw_menu()
            print('button 2 pressed, menu ', menu, "state", state)
        if state == "none":
            buzz()
            # start or increment main menu
            state = "start"
            check_menu()
            matrix.pixelsFill(matrix.black())
            draw_menu()
            print('button 2 pressed, menu ', menu, "state", state)
        if state == "choosing":
            buzz()
            # done choosing, draw emoji
            print("finshed, draw emoji")
            matrix.pixelsFill(matrix.black())
            draw_emoji()
    if button3.value():
        print('debug btn 3 menu ', menu, "pos", pos, "neg", neg, "state", state, "prev_pos", prev_pos, "prev_neg", prev_neg, "prev_state", prev_state)
        buzz()
        if state == "choosing":
            # increment negative choice
            neg = neg + 1
            pos = 0 # reset positive
            check_neg()
            print('button 3 pressed, menu ', menu, "neg", neg, "state", state)
            matrix.pixelsFill(matrix.black())
            draw_menu()
            draw_neg()
        if state == "start":
            buzz()
            # increment negative choice
            state = "choosing"
            neg = neg + 1
            check_neg()
            print('button 3 pressed, menu ', menu, "neg", neg, "state", state)
            matrix.pixelsFill(matrix.black())            
            draw_menu()
            draw_neg()
        if prev_state == "done":
            print("prev_pos", prev_pos)
            if (prev_pos > 0):
                # toggle pos to neg response
                buzz()
                matrix.pixelsFill(matrix.black())
                neg = prev_pos
                pos = 0
                menu = prev_menu
                print('button 3 pressed again, menu ', menu, "pos", pos, "neg", neg, "state", state)
                draw_emoji()
            if (prev_neg > 0):
                # play last neg
                buzz()
                matrix.pixelsFill(matrix.black())
                neg = prev_neg
                pos = 0
                menu = prev_menu
                print('button 3 pressed again, menu ', menu, "pos", pos, "neg", neg, "state", state)
                draw_emoji()
