from PiicoDev_RFID import PiicoDev_RFID
from PiicoDev_Unified import sleep_ms
from PiicoDev_SSD1306 import *
import network   # handles connecting to WiFi
import urequests # handles making and servicing network requests
import time

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

while True:    
    if rfid.tagPresent():    # if an RFID tag is present
        id = rfid.readID()   # get the id
        # details = rfid.readID(detail=True) # gets more details eg. tag type
        # 'type', 'id_formatted', 'success', 'id_integers': [91, 111, 184, 8]
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
    sleep_ms(100)

