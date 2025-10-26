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

Output on the pico:

```sh
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

On the zero, when I run service_discovery.py, this is the output:

```sh
BLE Service Discovery Debug
========================================
Connecting to Pico at 28:CD:C1:05:AB:A4...
✓ Connected successfully!

Discovering services and characteristics...
Error: object of type 'BleakGATTServiceCollection' has no len()
```

I edit the len() fn out like this:

```print(f"\nFound {len(services)} services:")```
To:
```print(f"\nFound x services:")```

And this is the output:

```sh
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

```sh
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

```sh
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

### Implementing the solution

After the above debugging, the communication between the zero and the pico is working.

This has been a long time coming.  Since my initial failures with trying to get a Pico 2 W to work in central mode, and then the same thing with the FireBeetle 2 ESP32 board, I was beginning to think it was not possible.

I was told in theory that a Raspberry pi zero could send signals to a Pico, but again, until it works, and can be used in emoji OS, it was still just an experiment.

Now I can move on to using the same method to send signals from the zero controller to the pico and have the emojis chosen that way.  Time to write the prompt for that.

I think I will have to start with the python\emoji-os\emoji-os-zero-0.2.3.py file.

Emoji OS Zero v0.2.7 with the PC simulation mode will not accept key or joystick input.  It did prove that the animation code currently could work, as it does on a PC, but that's another story.

We have a working controller.py running on a Raspberry Pi Zero 2 W that sends signals to a Raspberry Pi Pico 2 running the client.py file.

We want the controller to send the chosen emoji to the pico which can then display the emoji on the LCD display.

Look at the code in the python\emoji-os\emoji-os-zero-0.2.3.py and add the functionality from the python\emoji-os\bluetooth\controller.py file to send the main and sub-menu values to the pico.

We can make things simple and send a single string with the main menu value, a separator token and the sub-menu value.

### Running v0.3.0

I had some strange issues when running these scripts.  When I ran the script on startup via rc.local method, I saw this logging:

```sh
=== rc.local starting ===
Running emoji_os_zero_1.py...
Traceback (most recent call last):
  File "/home/tim/emoji-os/emoji_os_zero_1.py", line 7, in <module>
    from bleak import BleakScanner, BleakClient
ModuleNotFoundError: No module named 'bleak'
```

Note that emoji_os_zero_1.py is the name of the script that I pasted the contents of Emoji OS Zero v0.3.0 into and rebooted.

If I disable the rc.local method and run the script via Thonny on the zero, the script runs, and I see this output:

```sh
Emoji OS Zero v0.3.0 started with BLE Controller functionality
Joystick: Navigate menus
KEY1: Select positive
KEY2: Navigate/confirm
KEY3: Select negative
==================================================
Scanning for 'Pico-Client' for 5 seconds...
Make sure your Pico is running client.py...
Found 20 BLE devices:
--------------------------------------------------
 1. (No Name)            | 34:FC:C5:09:84:A3
 2. S24 9B06 LE          | CD:4D:CA:E8:49:22
 3. (No Name)            | FA:FA:C2:46:80:58
 4. (No Name)            | 6A:41:26:41:6A:9D
 5. S24 9B0A LE          | CD:4D:7C:66:43:1A
 6. Pico-Client          | 28:CD:C1:05:AB:A4
    *** FOUND TARGET DEVICE! ***
 7. (No Name)            | 70:D3:A4:89:21:81
 8. (No Name)            | 88:C6:26:AC:57:74
 9. (No Name)            | 78:32:93:43:15:D0
10. (No Name)            | 7D:3B:43:E3:7F:DF
11. (No Name)            | 7D:8F:B2:F6:49:EC
12. (No Name)            | F1:E4:7A:76:BB:5D
13. (No Name)            | F0:A4:4A:43:1F:4B
14. PR BT 7CF6           | 00:1F:FF:A9:0F:06
15. (No Name)            | EC:DF:20:E4:A9:78
16. (No Name)            | EB:52:DE:85:FB:07
17. (No Name)            | 1F:B1:8F:DF:45:D0
18. (No Name)            | E1:A3:C2:8C:47:DE
19. (No Name)            | 55:68:20:D2:B2:15
20. (No Name)            | 7B:3E:58:CD:9C:A6
--------------------------------------------------
✓ Found Pico-Client at address: 28:CD:C1:05:AB:A4
Connecting to 28:CD:C1:05:AB:A4...
✓ Successfully connected!
KEY2 - Menu: 0 State: start
debug KEY1 - menu: 0 pos 0 neg 0 state start prev_pos 0 prev_neg 0 prev_state none
KEY1 - Positive: 1 State: choosing
debug KEY1 - menu: 0 pos 1 neg 0 state choosing prev_pos 0 prev_neg 0 prev_state none
KEY1 - Positive: 2 State: choosing
debug KEY1 - menu: 0 pos 2 neg 0 state choosing prev_pos 0 prev_neg 0 prev_state none
KEY1 - Positive: 3 State: choosing
debug KEY1 - menu: 0 pos 3 neg 0 state choosing prev_pos 0 prev_neg 0 prev_state none
KEY1 - Positive: 4 State: choosing
Selected: Menu 0, Pos 4, Neg 0
✗ Error sending emoji command '0:4:0': Task <Task pending name='Task-9' coro=<BLEController.send_emoji_command() running at /home/tim/emoji-os/emoji_os_zero_1.py:102> cb=[_run_until_complete_cb() at /usr/lib/python3.11/asyncio/base_events.py:180]> got Future <Future pending> attached to a different loop
KEY2 - Menu: 0 State: choosing
KEY2 - Menu: 0 State: start
debug KEY3 - menu: 0 pos 0 neg 0 state start prev_pos 0 prev_neg 0 prev_state none
KEY3 - Negative: 1 State: choosing
debug KEY3 - menu: 0 pos 0 neg 1 state choosing prev_pos 0 prev_neg 0 prev_state none
KEY3 - Negative: 2 State: choosing
debug KEY3 - menu: 0 pos 0 neg 2 state choosing prev_pos 0 prev_neg 0 prev_state none
KEY3 - Negative: 3 State: choosing
Selected: Menu 0, Pos 0, Neg 3
✗ Error sending emoji command '0:0:3': Task <Task pending name='Task-10' coro=<BLEController.send_emoji_command() running at /home/tim/emoji-os/emoji_os_zero_1.py:102> cb=[_run_until_complete_cb() at /usr/lib/python3.11/asyncio/base_events.py:180]> got Future <Future pending> attached to a different loop
KEY2 - Menu: 0 State: choosing
```  

#### Question 1: why is bleak not installed when run via rc.local method?

*The issue is that rc.local runs with a different environment than when you run scripts manually through Thonny. When you run via rc.local, it uses the system's default Python environment and PATH, which may not have the same packages installed as your user environment.*

Solution: *Startup Script (start_emoji_os.sh): A bash script that properly sets up the Python environment for rc.local*

I don't think we need a *fallback Version (emoji-os-zero-0.3.0-fallback.py) to gracefully handles missing bleak module*, as the idea is to setup the env correctly so it works every time.  But if we have to use this method, then it would be good to get the current details straight.

This is the output which shows where pip and python are:

```sh
tim@raspberrypi:~ $ pip --version
pip 23.0.1 from /usr/lib/python3/dist-packages/pip (python 3.11)
tim@raspberrypi:~ $ pip3 --version
pip 23.0.1 from /usr/lib/python3/dist-packages/pip (python 3.1
```

Here is the current contents of the /etc/rc.local file:

```sh
#!/bin/sh -e

sleep 10

echo "=== rc.local starting ===" >> /home/tim/rc.local.log
echo "Running emoji_os_zero_1.py..." >> /home/tim/rc.local.log

# /usr/bin/python /home/tim/emoji-os/emoji_os_zero_1.py >> /home/tim/rc.local.l>

# echo "=== rc.local done ===" >> /home/tim/rc.local.log

exit 0
```

Using these details, lets make a more appropriate python\emoji-os\start_emoji_os.sh file.

The new start_emoji_os.sh file:

```sh
#!/bin/bash
# Startup script for Emoji OS Zero v0.3.1
# This script handles the Python environment setup for rc.local

echo "=== Emoji OS Zero v0.3.1 Startup ===" >> /home/tim/rc.local.log

# Run as user 'tim' to get the correct environment
sudo -u tim bash << 'EOF'
cd /home/tim/emoji-os

# Use the user's Python environment
export PATH="/home/tim/.local/bin:$PATH"
export PYTHONPATH="/home/tim/.local/lib/python3.11/site-packages:$PYTHONPATH"

# Check if bleak is available in user environment
if python3 -c "import bleak" 2>/dev/null; then
    echo "✓ Bleak module found in user environment" >> /home/tim/rc.local.log
else
    echo "✗ Bleak module not found, installing..." >> /home/tim/rc.local.log
    pip3 install --user bleak
fi

# Run the emoji OS
echo "Starting Emoji OS Zero v0.3.1..." >> /home/tim/rc.local.log
python3 emoji_os_zero_1.py >> /home/tim/rc.local.log 2>&1

echo "Emoji OS Zero v0.3.1 stopped" >> /home/tim/rc.local.log
EOF
```

The rc.local file then would use the new script like this:

```sh
#!/bin/sh -e

sleep 10

echo "=== rc.local starting ===" >> /home/tim/rc.local.log

# Use the startup script that handles environment properly
/home/tim/emoji-os/start_emoji_os.sh &

echo "=== rc.local done ===" >> /home/tim/rc.local.log

exit 0
```

#### Question 2: what is the issue with the ```got Future <Future pending> attached to a different loop``` error?  we were able to send messages in the controller.py script without error before

*The error got Future <Future pending> attached to a different loop occurs because we're trying to use asyncio across different threads without proper event loop management. The BLE controller creates its own event loop in a separate thread, but when we try to send commands from the main thread, there's a conflict.*

Solution: *implement proper event loop management using asyncio.run_coroutine_threadsafe() which allows safe communication between threads.*
