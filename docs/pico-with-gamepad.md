# Pico with gamepad

Raspberry Pi Pico as a BLE peripheral and as a BLE central device

GATT Generic Attribute Profile

Starting with this tutorial [Raspberry Pi Pico W Bluetooth Low Energy Micropython](https://randomnerdtutorials.com/raspberry-pi-pico-w-bluetooth-low-energy-micropython/) which covers both central and periheral mode.  I was interested in trying to put the Pico W in central mode.

## The 8BitDo Zero 2 Bluetooth Gamepad

The [manual](https://manuals.plus/8bitdo/zero-2-bluetooth-gamepad-manual) shows four styles of pairing.

### Keyboard mode

press R & start to turn on the controller. Blue LED blinks 5 times per cycle
Press the select button for 3 seconds to enter its pairing mode. The LED starts to rapidly blink
go to your device’s Bluetooth setting, pair with [8BitDo Zero 2 gamepad]. Blue LED becomes solid when the connection is successful
the controller will auto-reconnect to your device with the press of start once it has been paired
on keyboard mode, please make sure the input language on your device is in English

### macOS 8BitDo Zero 2 Bluetooth Gamepad - icon2

press A & start to turn on the controller. Blue LED blinks 3 times per cycle
Press the select button for 3 seconds to enter its pairing mode. The LED starts to rapidly blink

### Windows (X – input) 8BitDo Zero 2 Bluetooth Gamepad - icon

press X & start to turn on the controller. Blue LED blinks twice per cycle

### Android 8BitDo Zero 2 Bluetooth Gamepad - icon1

press B & start to turn on the controller. Blue LED blinks once per cycle
Press the select button for 3 seconds to enter its pairing mode. The LED starts to rapidly blink go to your Android device’s Bluetooth setting, pair with [8BitDo Zero 2 gamepad]. Blue LED becomes solid when the connection is successful

## Testing the gamepad

### Gamepad-2

```txt
Looking for 8BitDo Zero 2 gamepad...
Scanning for devices to test...
Found device: 50:a9:63:82:f8:eb
Found device: 88:c6:26:ac:57:74
Found device: cd:4d:7c:66:43:1a
Found device: 36:35:67:85:42:cd
Found device: 1b:e2:31:26:af:48
Found device: 4a:33:32:0c:bb:10
Found device: 6b:bd:a4:4c:9f:c9
Found device: c9:82:97:0f:19:ed
Found device: 5d:19:2d:3a:d5:9f
Found device: e2:f8:b7:3b:af:43
Found device: e4:d9:51:15:e6:08
Found device: e1:f4:19:98:90:49
Found device: 1f:84:72:52:4a:0e
Found 13 devices. Testing each for HID services...
Trying to connect to 50:a9:63:82:f8:eb...
Connected to 50:a9:63:82:f8:eb
Found HID service on 50:a9:63:82:f8:eb - This might be our gamepad!
Connecting to gamepad...
Connected successfully!
Discovering HID service...
HID service found
Discovering characteristics...
Service discovery error: 'NoneType' object has no attribute 'characteristics'
Looking for 8BitDo Zero 2 gamepad...
Scanning for devices to test...
```

### Gamepad-3

```txt
Looking for 8BitDo Zero 2 gamepad...
Scanning for devices to test...
Found device: 12:23:24:f8:94:57
Found device: 88:c6:26:ac:57:74
Found device: d0:8d:86:b8:a8:fd
Found device: 4d:da:87:2b:22:d0
Found device: cd:4d:7c:66:43:1a
Found device: 4a:33:32:0c:bb:10
Found device: 6b:bd:a4:4c:9f:c9
Found device: 78:3a:18:d7:5d:7c
Found device: c6:80:be:2d:cf:df
Found device: c9:82:97:0f:19:ed
Found device: 50:a9:63:82:f8:eb
Found device: c3:6b:9c:09:d3:19
Found device: e4:d9:51:15:e6:08
Found device: 5d:19:2d:3a:d5:9f
Found device: 1b:15:ec:8a:5f:d8
Found device: e2:f8:b7:3b:af:43
Found device: 36:35:67:85:42:cd
Found 17 devices. Testing each for HID services...
Trying to connect to 12:23:24:f8:94:57...
Connection timeout to 12:23:24:f8:94:57
Trying to connect to 88:c6:26:ac:57:74...
Connection error to 88:c6:26:ac:57:74: [Errno 22] EINVAL
Trying to connect to d0:8d:86:b8:a8:fd...
Connection error to d0:8d:86:b8:a8:fd: [Errno 22] EINVAL
Trying to connect to 4d:da:87:2b:22:d0...
Connection error to 4d:da:87:2b:22:d0: [Errno 22] EINVAL
Trying to connect to cd:4d:7c:66:43:1a...
Connection error to cd:4d:7c:66:43:1a: [Errno 22] EINVAL
Trying to connect to 4a:33:32:0c:bb:10...
Connection error to 4a:33:32:0c:bb:10: [Errno 22] EINVAL
Trying to connect to 6b:bd:a4:4c:9f:c9...
Connection error to 6b:bd:a4:4c:9f:c9: [Errno 22] EINVAL
Trying to connect to 78:3a:18:d7:5d:7c...
Connection error to 78:3a:18:d7:5d:7c: [Errno 22] EINVAL
Trying to connect to c6:80:be:2d:cf:df...
Connection error to c6:80:be:2d:cf:df: [Errno 22] EINVAL
Trying to connect to c9:82:97:0f:19:ed...
Connection error to c9:82:97:0f:19:ed: [Errno 22] EINVAL
Trying to connect to 50:a9:63:82:f8:eb...
Connection error to 50:a9:63:82:f8:eb: [Errno 22] EINVAL
Trying to connect to c3:6b:9c:09:d3:19...
Connection error to c3:6b:9c:09:d3:19: [Errno 22] EINVAL
Trying to connect to e4:d9:51:15:e6:08...
Connection error to e4:d9:51:15:e6:08: [Errno 22] EINVAL
Trying to connect to 5d:19:2d:3a:d5:9f...
Connection error to 5d:19:2d:3a:d5:9f: [Errno 22] EINVAL
Trying to connect to 1b:15:ec:8a:5f:d8...
Connection error to 1b:15:ec:8a:5f:d8: [Errno 22] EINVAL
Trying to connect to e2:f8:b7:3b:af:43...
Connection error to e2:f8:b7:3b:af:43: [Errno 22] EINVAL
Trying to connect to 36:35:67:85:42:cd...
Connection error to 36:35:67:85:42:cd: [Errno 22] EINVAL
8BitDo Zero 2 gamepad not found. Make sure it's in pairing mode (Start + Right shoulder button).
Retrying in 10 seconds...
```

### Gamepad-3

```txt
=== 8BitDo Zero 2 Gamepad Scanner ===
Make sure your gamepad is in pairing mode:
- Hold Start + Y for 3 seconds, OR
- Hold Start + Right shoulder button
- LED should be flashing rapidly

Detailed scan for 8BitDo Zero 2...
No gamepad candidates found. Retrying in 10 seconds...
```

### Gamepad-4

```txt
Found: 
  Services: ["uuid('72daa6c3-29c2-6283-0c4a-2818e4d37e75')"]
  Confidence: 0%
---
Found: No Name (06:c4:c3:2b:21:41)
  Services: []
  Confidence: 0%
---
Found: No Name (12:37:a0:e4:e3:78)
  Services: []
  Confidence: 0%
---

❌ No 8BitDo Zero 2 found!

Troubleshooting:
1. Make sure you pressed the correct button combination:
   - X + Start (for Windows mode)
   - R + Start (for Keyboard mode)
2. Then press SELECT for 3 seconds (LED should blink rapidly)
3. Make sure the gamepad is close to your Pico W
4. Try turning the gamepad off and on again

Retrying in 15 seconds...
```

## Pico to Pico communication

After failing to get the gamepad to work with the Pico W, I decided to try to get the Pico W to talk to itself.

One pico will act as the controller and the other will act as the receiver.

I save the controller-complete.py code to main.py and run it.

```txt
>>> %Run -c $EDITOR_CONTENT
=== Access Point Only Test ===
✅ AP interface activated
Trying config method 1: {'channel': 6, 'essid': 'PicoController', 'password': 'pico1234', 'authmode': 3}
❌ Config method 1 failed: unknown config param
Trying config method 2: {'password': 'pico1234', 'essid': 'PicoController'}
✅ Config method 2 succeeded
✅ Access Point is active!
   IP: 192.168.4.1
   Netmask: 255.255.255.0
   Gateway: 192.168.4.1
   DNS: 0.0.0.0

📡 Network 'PicoController' should now be visible!
   Try scanning for WiFi networks on another device
   Press Ctrl+C when done testing
```

I disconnect it an plug it in to a usb cable connected to an electricity outlet.

Then I connect the second pico w to the computer and load and run the python\pico_w\receiver_client.py on that one to see the ouput in thonny.

I save the controller code and save it to main.py.

I run it and see this output:

```txt
>>> %Run -c $EDITOR_CONTENT
🎮 Fixed PicoController Starting
========================================
📡 Setting up Access Point...
✅ AP interface activated
🔧 Configuring AP with simple method...
✅ AP configured successfully!
   Network: PicoController
   Password: pico1234
   IP: 192.168.4.1
📡 UDP server ready on port 8888
🎮 Controller ready!

🚀 Controller running!
💓 Status: 0 receivers
```

I disconnect it from my laptop and connect it to another usb power source.

I see the PICO3B73 in the wifi list on my phone.

I connect the other pico w to my computer and connect it to Thonny and run the receiver_enhanced.py code.

I see this output:

```txt
>> %Run -c $EDITOR_CONTENT
🎮 Enhanced Gamepad Receiver Starting...
=============================================
🔍 Looking for controller network...
📡 Found 'PICO3B73' (Signal: -41 dBm, Auth: 7)

🔗 Trying 'PICO3B73' with password: 'pico1234'
   Connecting... (1s)
   Connecting... (4s)
   Connecting... (7s)
   Connecting... (10s)
   Connecting... (13s)
❌ Connection to 'PICO3B73' timed out

🔗 Trying 'PICO3B73' with password: 'micropythoN'
   Connecting... (1s)
   Connecting... (4s)
   Connecting... (7s)
   Connecting... (10s)
   Connecting... (13s)
❌ Connection to 'PICO3B73' timed out

🔗 Trying 'PICO3B73' with password: None (Open)
   Connecting... (1s)
   Connecting... (4s)
   Connecting... (7s)
   Connecting... (10s)
   Connecting... (13s)
❌ Connection to 'PICO3B73' timed out
❌ Failed to connect to controller

❌ Receiver not ready - connection failed```
```

I think  I will actually need two computers so I can have each pico connected to Thonny so see the logging and confirm what is happening in detail to sort this out.  The gamepad would be ideal, as it is a stylish little thing.  The Waveshare display hat with two buttons and joystick looks custom yet cumbersome as it would require its own power source and a case to house that - a lot more work.

## Pico 2 W

The above was all using the Pico W.  However, I finally found my Pico 2 W, so will give that a try again with the gamepad.

Using the The 8BitDo Zero 2 Bluetooth Gamepad to connect to the Pico 2 W in central mode, which binding method should I use?

This method will require the aioble lib.  When trying to install it, I get this message: *This doesn't look like MicroPython/CircuiPython package.  Are you sure you want to install it?*

With the Pico W version 1, this actually caused some errors, but on the Pico 2 W, it seems to complete without issue despite the message.

### Binding Method for 8BitDo Zero 2

- Power on the gamepad (it should be in normal mode, not pairing mode initially)
- Press and hold Start + Y for 3 seconds - this puts it in BLE mode
- The LED should flash slowly (not rapidly like Classic Bluetooth mode)

### Why This Matters

- Start + Y (3 seconds) = BLE mode ✅
- Start + Right Shoulder = Classic Bluetooth mode ❌ (won't work with Pico 2 W)
- The Pico 2 W supports BLE much better than the original Pico W, so the 8BitDo Zero 2 should work in BLE mode.

Cursor says The Pico 2 W supports BLE much better than the original Pico W, so the 8BitDo Zero 2 should work in BLE mode.

However, the first attempt shows this output:

```txt
>>> %Run -c $EDITOR_CONTENT
�� 8BitDo Zero 2 Gamepad Reader for Pico 2 W
==================================================
🔍 Scanning for 8BitDo Zero 2...
💡 Make sure gamepad is in BLE mode (Start + Y for 3 seconds)
   LED should flash slowly, not rapidly
❌ 8BitDo Zero 2 not found
💡 Check:
   - Gamepad is powered on
   - Gamepad is in BLE mode (Start + Y)
   - Gamepad is nearby
✅ Disconnected
```

Adding more logging to the script, I see this output:

```txt
🎮 8BitDo Zero 2 Gamepad Reader for Pico 2 W
==================================================
Updated for actual manual pairing modes
==================================================
🔧 Initializing BLE system...
📱 BLE active state: False
🔧 Activating BLE...
📱 BLE active state after activation: True
🔧 Setting up BLE IRQ handler...
🔧 Resetting BLE state...
✅ BLE system initialized successfully
🔍 Scanning for 8BitDo Zero 2...

💡 Pairing Instructions (from manual):
1. Power on with one of these combinations:
   - B + Start (Android mode) - LED blinks once per cycle
   - X + Start (Windows mode) - LED blinks twice per cycle
   - A + Start (macOS mode) - LED blinks 3 times per cycle
   - R + Start (Keyboard mode) - LED blinks 5 times per cycle
2. Press SELECT for 3 seconds to enter pairing mode
   LED should start rapidly blinking
3. Keep gamepad close to Pico 2 W

🔍 Starting scan...
🔧 Starting BLE scan for 10000ms...
🔧 Scan parameters: interval=30000, window=30000, active=False
✅ BLE scan started successfully
⏳ Waiting for scan results...
🔔 BLE IRQ Event: 5
🔔 BLE IRQ Event: 5
🔔 BLE IRQ Event: 5
...
🔔 BLE IRQ Event: 5
🔔 BLE IRQ Event: 6
⏱️ Scan wait completed. Time elapsed: 12001ms
❌ 8BitDo Zero 2 not found
📊 Scan results: 0 devices found
✅ Disconnected
```

## Raspberry Pi Zero W as Controller to work as a controller

How can we setup Raspberry Pi Zero W as Controller to work as a controller?

Raspberry Pi Zero W (or Zero 2 W)
Small display (1.44" or 2.4" TFT, or even just an OLED)
Buttons and joystick (GPIO connected)
Power supply (USB power bank works great)
