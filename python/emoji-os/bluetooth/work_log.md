# Work log

## Next Debugging Steps

Step 1: Run Service Discovery
On the zero:
python3 service_discovery.py
This will show us exactly what services and characteristics the Pico is advertising.

Step 2: Run Debug Client
On the Pico, run:
client_debug.py

This will show us detailed information about the service registration process.

Step 3: Test Connection Again
On your Zero, run:

client_debug.py

### Debugging outcome


Output on the pcio:
```
>>> %Run -c $EDITOR_CONTENT
BLE Client Debug Version
========================================
Initializing BLE...
Creating peripheral...
Initializing BLE Peripheral...
Activating BLE...
Setting up IRQ handler...
Registering UART service...
Service UUID: UUID('6e400001-b5a3-f393-e0a9-e50e24dcca9e')
TX Characteristic: UUID('6e400003-b5a3-f393-e0a9-e50e24dcca9e')
RX Characteristic: UUID('6e400002-b5a3-f393-e0a9-e50e24dcca9e')
✓ Service registered successfully!
TX handle: 9
RX handle: 12
Creating advertising payload...
Advertising payload length: 34
Starting advertising...
Starting advertising with interval 500000μs...
Setting up command handler...

BLE Client started successfully!
Waiting for connections...
Available commands: ON, OFF, STATUS, BLINK
Press Ctrl+C to stop
✓ New connection: 64
✗ Disconnected: 64
Starting advertising with interval 500000μs...
✓ New connection: 64
✗ Disconnected: 64
Starting advertising with interval 500000μs...
✓ New connection: 64
✗ Disconnected: 64
Starting advertising with interval 500000μs...
✓ New connection: 64
✗ Disconnected: 64
Starting advertising with interval 500000μs...
```

On the zero, when I run service_discovery.py
This is the output:

```
BLE Service Discovery Debug
========================================
Connecting to Pico at 28:CD:C1:05:AB:A4...
✓ Connected successfully!

Discovering services and characteristics...
Error: object of type 'BleakGATTServiceCollection' has no len()
```

I edit the len() fn out like this:

print(f"\nFound {len(services)} services:")
To 
print(f"\nFound x services:")

And this is the output:
```
BLE Service Discovery Debug
========================================
Connecting to Pico at 28:CD:C1:05:AB:A4...
✓ Connected successfully!

Discovering services and characteristics...

Found xxx services:
------------------------------------------------------------
Service: 6e400001-b5a3-f393-e0a9-e50e24dcca9e
  Description: Nordic UART Service
  Characteristics (2):
    UUID: 6e400002-b5a3-f393-e0a9-e50e24dcca9e
    Properties: ['write-without-response', 'write']
    Description: Nordic UART RX

    UUID: 6e400003-b5a3-f393-e0a9-e50e24dcca9e
    Properties: ['read', 'notify']
    Description: Nordic UART TX

------------------------------------------------------------
Service: 00001801-0000-1000-8000-00805f9b34fb
  Description: Generic Attribute Profile
  Characteristics (1):
    UUID: 00002a05-0000-1000-8000-00805f9b34fb
    Properties: ['read']
    Description: Service Changed

------------------------------------------------------------

Looking for Nordic UART Service...
✓ Found Nordic UART Service: 6e400001-b5a3-f393-e0a9-e50e24dcca9e
✓ Found RX characteristic: 6e400002-b5a3-f393-e0a9-e50e24dcca9e
✓ Found TX characteristic: 6e400003-b5a3-f393-e0a9-e50e24dcca9e
>>>
```

## Prompts

### Initial prompt for planning

I have a Raspberry Pi Pico 2 w which I want to listen to commands that are sent from a Raspberry Pi Zero 2 W using either BLE or Bluetooth Classic mode.
Lets create two simple test scripts, one for the zero in python to send signals to the pico, and one for the pico in micropython which will be connected to a laptop Thonny running the app and showing the output.  The raspberry pi zero script will be called: python/bluetooth/copntroller.py and the pico script: python/bluetooth/client.py.
Add some documentation to the python/bluetooth/product-requirements-document.md later.

### Question and answers

Bluetooth protocol choice: Which protocol would you prefer?
c) Either one (choose the most straightforward option)

Communication pattern: What type of commands will the Zero send to the Pico?
a) Simple text commands (e.g., "ON", "OFF", "STATUS")

Pico response behavior: Should the Pico respond back to the Zero?
b) No, just receive and display commands

First I tried the script and saw this:

```
>>> %Run controller.py
BLE Controller Debug Version
==================================================
Scanning for 'Pico-Client' for 15 seconds...
Make sure your Pico is running client.py and advertising...

Found 23 total BLE devices:
------------------------------------------------------------
Unexpected error: 'BLEDevice' object has no attribute 'rssi'
>>>
```

I removed the ```{device.rssi}``` occurance, then saw this:

```
BLE Controller Debug Version
==================================================
Scanning for 'Pico-Client' for 15 seconds...
Make sure your Pico is running client.py and advertising...

Found 21 total BLE devices:
------------------------------------------------------------
 1. Name: (No Name)            | Address: 45:C3:FC:8C:83:0C | RSSI: x
 2. Name: (No Name)            | Address: 52:B3:A2:98:D9:97 | RSSI: x
 3. Name: (No Name)            | Address: 6F:C2:16:4C:96:05 | RSSI: x
 4. Name: (No Name)            | Address: 54:0C:7A:46:04:66 | RSSI: x
 5. Name: (No Name)            | Address: 88:C6:26:AC:57:74 | RSSI: x
 6. Name: (No Name)            | Address: 75:9A:62:74:78:8D | RSSI: x
 7. Name: S24 9B0A LE          | Address: CD:4D:7C:66:43:1A | RSSI: x
 8. Name: (No Name)            | Address: 4B:70:CE:9B:8E:EA | RSSI: x
 9. Name: (No Name)            | Address: 42:ED:CD:74:FF:E2 | RSSI: x
10. Name: (No Name)            | Address: 19:0D:A1:75:3F:0C | RSSI: x
11. Name: Pico-Client          | Address: 28:CD:C1:05:AB:A4 | RSSI: x
    *** FOUND TARGET DEVICE! ***
12. Name: PR BT 7CF6           | Address: 00:1F:FF:A9:0F:06 | RSSI: x
13. Name: (No Name)            | Address: D0:77:9F:36:9F:70 | RSSI: x
14. Name: (No Name)            | Address: 50:E5:B6:61:E1:56 | RSSI: x
15. Name: (No Name)            | Address: 59:A9:C6:74:99:63 | RSSI: x
16. Name: (No Name)            | Address: E9:6A:F6:E3:4C:8E | RSSI: x
17. Name: (No Name)            | Address: C5:83:99:83:07:0D | RSSI: x
18. Name: (No Name)            | Address: CE:A4:02:35:F5:CB | RSSI: x
19. Name: (No Name)            | Address: CC:03:7B:7B:8C:93 | RSSI: x
20. Name: (No Name)            | Address: F4:8E:9A:E0:42:A9 | RSSI: x
21. Name: (No Name)            | Address: F8:5C:0E:79:80:46 | RSSI: x
------------------------------------------------------------
✓ Found Pico-Client at address: 28:CD:C1:05:AB:A4
Connecting to 28:CD:C1:05:AB:A4...
✓ Successfully connected!

Sending test command...
✗ Error sending command 'STATUS': Characteristic 6E400002-B5A3-F393-E0A9-E50E24DCCA9E was not found!

Test completed successfully!
Disconnected
```

What is the error from the test send?

### Next Debugging Steps

Now let's test this systematically:
Step 1: Run Service Discovery
On your Raspberry Pi Zero, run:
This will show us exactly what services and characteristics the Pico is advertising.
Step 2: Run Debug Client
On your Pico, stop the current client and run:
This will show us detailed information about the service registration process.
Step 3: Test Connection Again
On your Zero, run:

