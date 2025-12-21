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

### v0.3.1 issues

I run the client.py file on the pico and see this output:

```sh
>>> %Run -c $EDITOR_CONTENT
BLE Client for Raspberry Pi Pico 2 W - Enhanced for Emoji Commands
======================================================================
Starting advertising...
BLE Client started
Waiting for connections...
Supports emoji commands in format: 'MENU:POS:NEG'
Legacy commands: ON, OFF, STATUS, BLINK
Press Ctrl+C to stop
```

I run the Emoji OS Zero v0.3.1 script on the zero and see this output:

```sh
>>> %Run emoji_os_zero_1.py
Emoji OS Zero v0.3.0 started with BLE Controller functionality
Joystick: Navigate menus
KEY1: Select positive
KEY2: Navigate/confirm
KEY3: Select negative
==================================================
Scanning for 'Pico-Client' for 5 seconds...
Make sure your Pico is running client.py...
Found 24 BLE devices:
--------------------------------------------------
 1. (No Name)            | 0E:C1:D3:85:D2:91
 2. MPY BTSTACK          | 28:CD:C1:05:AB:A4
 3. (No Name)            | 7A:03:C9:18:F1:16
 4. (No Name)            | 4A:A9:3A:3F:53:E9
 5. (No Name)            | 64:72:E7:41:B1:BB
 6. (No Name)            | 49:06:0F:87:8B:84
 7. (No Name)            | 66:57:EF:18:01:B7
 8. (No Name)            | 4D:FE:44:8C:0E:9D
 9. (No Name)            | 77:01:58:02:50:D3
10. (No Name)            | 00:16:BA:FE:B9:02
11. S24 9B0A LE          | CD:4D:7C:66:43:1A
12. (No Name)            | 40:AB:E2:FF:2C:13
13. (No Name)            | E9:72:B8:35:0F:4C
14. (No Name)            | E4:E3:70:3E:8B:02
15. (No Name)            | C4:9D:A0:AD:C1:EF
16. (No Name)            | D7:E1:B8:C8:2B:AE
17. (No Name)            | C5:65:B8:EE:51:33
18. (No Name)            | EC:CE:37:A2:AC:D4
19. (No Name)            | F3:10:58:33:0D:EC
20. PR BT 7CF6           | 00:1F:FF:A9:0F:06
21. (No Name)            | 6B:AB:94:FD:66:C7
22. (No Name)            | CC:A9:42:85:98:E8
23. (No Name)            | 40:A1:13:F3:7E:AA
24. (No Name)            | E0:A1:28:41:3D:91
--------------------------------------------------
✗ Could not find 'Pico-Client'

Troubleshooting tips:
1. Make sure Pico is running client.py
2. Check that Pico shows 'Starting advertising...'
3. Try moving devices closer together
4. Restart both devices
```

### v0.3.1 again

I run the correct client file on the pico and see this output:

```sh
>>> %Run -c $EDITOR_CONTENT

MPY: soft reboot
BLE Client for Raspberry Pi Pico 2 W v1.1.0 - Enhanced for Emoji Commands
Device Name: Pico-Client
======================================================================
Starting advertising...
BLE Client started
Waiting for connections...
Supports emoji commands in format: 'MENU:POS:NEG'
Legacy commands: ON, OFF, STATUS, BLINK
Press Ctrl+C to stop
```

I run Emoji OS Zero v0.3.1 started with BLE Controller functionality on the zero and see this output:

```sh
>>> %Run emoji_os_zero_1.py
Emoji OS Zero v0.3.1 started with BLE Controller functionality
Joystick: Navigate menus
KEY1: Select positive
KEY2: Navigate/confirm
KEY3: Select negative
==================================================
Scanning for 'Pico-Client' for 5 seconds...
Make sure your Pico is running client.py...
Found 18 BLE devices:
--------------------------------------------------
 1. (No Name)            | 71:46:9E:FA:CF:78
 2. (No Name)            | 4B:CF:B3:FC:E6:68
 3. S24 9B0A LE          | CD:4D:7C:66:43:1A
 4. (No Name)            | 16:AC:7C:8F:7E:E5
 5. (No Name)            | C7:E6:45:9C:01:10
 6. (No Name)            | 73:67:51:08:2C:17
 7. (No Name)            | 5C:FF:01:E0:31:45
 8. (No Name)            | 56:CC:F7:82:2B:A7
 9. (No Name)            | 58:93:F8:9A:74:FF
10. (No Name)            | 5E:ED:A2:4B:EC:73
11. MPY BTSTACK          | 28:CD:C1:05:AB:A4
12. (No Name)            | CF:4E:77:CA:91:2B
13. (No Name)            | 40:CE:2A:44:0C:B2
14. (No Name)            | FD:8C:FD:30:1C:D0
15. (No Name)            | E2:F9:F4:A4:3A:93
16. (No Name)            | D7:7F:86:E8:ED:0F
17. (No Name)            | C3:98:54:F7:02:27
18. (No Name)            | FF:00:A3:F7:C7:68
--------------------------------------------------
✗ Could not find 'Pico-Client'

Troubleshooting tips:
1. Make sure Pico is running client.py
2. Check that Pico shows 'Starting advertising...'
3. Try moving devices closer together
4. Restart both devices
```

Why isn't the 'Pico-Client' in the device list?

Did we use the device name "MPY BTSTACK" at any point?  I don't see that in the old commits...

## emoji os v0.2.0 and zero v0.3.1 testing

On the Pico running the emoji os v0.2.0 - Enhanced with BLE Controller functionality, I see this output:`

```sh
>>> %Run -c $EDITOR_CONTENT
Starting advertising...
Emoji OS Pico v0.2.0 - Enhanced with BLE Controller functionality
Device Name: Pico-Client
Supports emoji commands in format: 'MENU:POS:NEG'
Legacy commands: ON, OFF, STATUS, BLINK
```

On the Zero running the Emoji OS Zero v0.3.1 started with BLE Controller functionality, I see this output:

```sh
tim@raspberrypi:~/emoji-os $ python emoji_os_zero_1.py
Emoji OS Zero v0.3.0 started with BLE Controller functionality
Joystick: Navigate menus
KEY1: Select positive
KEY2: Navigate/confirm
KEY3: Select negative
==================================================
Scanning for 'PR BT 7CF6' for 5 seconds...
Make sure your Pico is running client.py...
Found 10 BLE devices:
--------------------------------------------------
 1. (No Name)            | 88:C6:26:AC:57:74
 2. (No Name)            | 10:4D:01:B1:9E:7E
 3. (No Name)            | 28:CD:C1:07:2C:E8
 4. (No Name)            | 54:42:34:E4:B3:58
 5. (No Name)            | 05:9A:0B:9C:23:C4
 6. PR BT 7CF6           | 00:1F:FF:A9:0F:06
    *** FOUND TARGET DEVICE! ***
 7. (No Name)            | D0:BE:2C:A3:F8:0C
 8. (No Name)            | D4:16:4C:98:EA:8E
 9. (No Name)            | F2:F5:4C:F0:50:66
10. (No Name)            | FE:46:DF:20:AC:D9
--------------------------------------------------
✓ Found PR BT 7CF6 at address: 00:1F:FF:A9:0F:06
Connecting to 00:1F:FF:A9:0F:06...
✗ Connection error: failed to discover services, device disconnected
KEY2 - Menu: 0 State: start
debug KEY1 - menu: 0 pos 0 neg 0 state start prev_pos 0 prev_neg 0 prev_state none
KEY1 - Positive: 1 State: choosing
Selected: Menu 0, Pos 1, Neg 0
Not connected to any device
KEY2 - Menu: 0 State: choosing
KEY2 - Menu: 0 State: start
debug KEY1 - menu: 0 pos 0 neg 0 state start prev_pos 0 prev_neg 0 prev_state none
KEY1 - Positive: 1 State: choosing
debug KEY1 - menu: 0 pos 1 neg 0 state choosing prev_pos 0 prev_neg 0 prev_state none
KEY1 - Positive: 2 State: choosing
Selected: Menu 0, Pos 2, Neg 0
Not connected to any device
KEY2 - Menu: 0 State: choosing
debug KEY3 - menu: 0 pos 0 neg 0 state none prev_pos 2 prev_neg 0 prev_state done
KEY3 - Toggle from pos to neg, menu: 0 pos 0 neg 2
Not connected to any device
```

### Issue 1: Zero script scanning for wrong device name

The Zero output shows it's scanning for "PR BT 7CF6" instead of "Pico-Client". This suggests the running script (emoji_os_zero_1.py) has a different TARGET_DEVICE_NAME.
Fix: Ensure your Zero script has:
### Issue 2: Pico BLE name not advertising correctly

The Pico may not be advertising as "Pico-Client" (it may appear as "MPY BTSTACK" or another name).

#### Fixes applied:

Improved BLE stack reset with longer delays to clear cached names
Added logging to show the configured device name
Enhanced advertising messages to confirm the name being advertised

### Changes made:

#### emoji-os-pico-0.2.0.py:

Longer BLE reset delays (0.3s instead of 0.1s)
Added logging: "BLE Device Name configured: Pico-Client"
Enhanced advertising message to show the name being advertised

#### emoji-os-zero-0.3.0.py:

- Added comment warning not to change TARGET_DEVICE_NAME
- Enhanced scanning to show partial matches (devices with "pico" or "client" in name)
- Better error messages with troubleshooting steps
- Service discovery verification after connection

When I run the new version, I see this ouput on the zero: ``````
>>> %Run emoji_os_zero_1.py
Emoji OS Zero v0.3.3 started with BLE Controller functionality
Joystick: Navigate menus
KEY1: Select positive
KEY2: Navigate/confirm
KEY3: Select negative
==================================================
Scanning for 'PR BT 7CF6' for 5 seconds...
Make sure your Pico is running client.py...
Expected device name: 'PR BT 7CF6'
Found 12 BLE devices:
--------------------------------------------------
 1. (No Name)            | 88:C6:26:AC:57:74
 2. (No Name)            | 28:CD:C1:07:2C:E8
 3. (No Name)            | 27:E2:D2:23:31:4E
 4. (No Name)            | 4C:E1:DF:70:9F:7F
 5. (No Name)            | 72:FA:15:DA:E7:E3
 6. Charge 6             | C3:ED:E7:B4:53:A3
 7. PR BT 7CF6           | 00:1F:FF:A9:0F:06
    *** FOUND TARGET DEVICE! ***
 8. (No Name)            | 7A:9A:7E:79:86:91
 9. (No Name)            | D8:B6:63:75:B3:AB
10. (No Name)            | 76:A8:18:D6:64:02
11. (No Name)            | CC:7E:F4:FE:E8:D5
12. (No Name)            | E7:15:EB:BF:5A:E5
--------------------------------------------------
✓ Found PR BT 7CF6 at address: 00:1F:FF:A9:0F:06
Connecting to 00:1F:FF:A9:0F:06...
✗ Connection error: failed to discover services, device disconnected
   This usually means:
   1. The device disconnected during connection
   2. The device doesn't support the required BLE services
   3. There's a compatibility issue with the BLE stack
...
```  I changed the name it was searching for to "PR BT 7CF6" as that is what I saw on the list, not "Pico Client" as you had said could be used.  Are you sure we can choose the device name?  I am happy using whatever name the pico uses at this point.  Anyhow, the error shows "failed to discover services".  What is the problem with that?

### The Problem
"PR BT 7CF6" is not your Pico; it's a different device (possibly a Bluetooth speaker or similar). That device doesn't have the Nordic UART Service, which is why you're seeing "failed to discover services" — you're connecting to the wrong device.

### The Solution

The script now scans by service UUID instead of relying on device name:
First, it tries to scan directly for devices advertising the Nordic UART Service (most reliable)
If that doesn't work, it does a general scan and then connects to candidate devices to verify they have the service
Device name is now optional — it's nice to have a match, but the script will find the Pico by its service UUID regardless

The new version causes this error:

```sh
tim@raspberrypi:~/emoji-os $ python emoji_os_zero_1.py
Traceback (most recent call last):
  File "/usr/lib/python3/dist-packages/gpiozero/pins/pi.py", line 411, in pin
    pin = self.pins[info]
          ~~~~~~~~~^^^^^^
KeyError: PinInfo(number=13, name='GPIO27', names=frozenset({'J8:13', '27', 'BCM27', 'GPIO27', 27, 'WPI2', 'BOARD13'}), pull='', row=7, col=1, interfaces=frozenset({'', 'gpio', 'dpi', 'sdio', 'spi', 'jtag'}))

During handling of the above exception, another exception occurred:

Traceback (most recent call last):
  File "/home/tim/emoji-os/emoji_os_zero_1.py", line 216, in <module>
    disp = LCD_1in44.LCD()
           ^^^^^^^^^^^^^^^
  File "/home/tim/emoji-os/config.py", line 53, in __init__
    self.GPIO_RST_PIN= self.gpio_mode(rst,self.OUTPUT)
                       ^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^
  File "/home/tim/emoji-os/config.py", line 82, in gpio_mode
    return DigitalOutputDevice(Pin,active_high = True,initial_value =False)
           ^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^
  File "/usr/lib/python3/dist-packages/gpiozero/devices.py", line 108, in __call__
    self = super().__call__(*args, **kwargs)
           ^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^
  File "/usr/lib/python3/dist-packages/gpiozero/output_devices.py", line 192, in __init__
    super().__init__(pin, active_high=active_high,
  File "/usr/lib/python3/dist-packages/gpiozero/output_devices.py", line 74, in __init__
    super().__init__(pin, pin_factory=pin_factory)
  File "/usr/lib/python3/dist-packages/gpiozero/mixins.py", line 75, in __init__
    super().__init__(*args, **kwargs)
  File "/usr/lib/python3/dist-packages/gpiozero/devices.py", line 553, in __init__
    pin = self.pin_factory.pin(pin)
          ^^^^^^^^^^^^^^^^^^^^^^^^^
  File "/usr/lib/python3/dist-packages/gpiozero/pins/pi.py", line 413, in pin
    pin = self.pin_class(self, info)
          ^^^^^^^^^^^^^^^^^^^^^^^^^^
  File "/usr/lib/python3/dist-packages/gpiozero/pins/lgpio.py", line 126, in __init__
    lgpio.gpio_claim_input(
  File "/usr/lib/python3/dist-packages/lgpio.py", line 755, in gpio_claim_input
    return _u2i(_lgpio._gpio_claim_input(handle&0xffff, lFlags, gpio))
           ^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^
  File "/usr/lib/python3/dist-packages/lgpio.py", line 458, in _u2i
    raise error(error_text(v))
lgpio.error: 'GPIO busy'
```
