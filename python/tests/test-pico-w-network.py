# A simple example that:
# - Connects to a WiFi Network defined by "ssid" and "password"
# - Queries the current time from a server

import network   # handles connecting to WiFi
import urequests # handles making and servicing network requests
import time

# Fill in your network name (ssid) and password here:
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

# Example 2. urequests can also handle basic json support! Let's get the current time from a server
print("\n\n2. Querying the current GMT+0 time:")
r = urequests.get("http://date.jsontest.com") # Server that returns the current GMT+0 time.
print(r.json())
