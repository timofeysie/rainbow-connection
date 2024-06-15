# The Game Medallion Project

## Setting up a Raspberry Pi Pico W

Download the latest [UF2 file from the link here](https://core-electronics.com.au/guides/raspberry-pi-pico/raspberry-pi-pico-w-connect-to-the-internet/).  More details about it are on the [official site](https://www.raspberrypi.com/documentation/microcontrollers/raspberry-pi-pico.html).

For me this file is: RPI_PICO_W-20240602-v1.23.0.uf2

Then do the usual to setup the Pico.

1. Hold the BOOTSEL button on the Pico W and connect to your computer and release the BOOTSEL button.

The Pico W will appear as a removable drive called RPI-RP2

2. Drag + Drop the MicroPython .uf2 file into RPI-RP2, unplug the Pico and plug it back in.  After the reboot, your Pico W is now running MicroPython

MicroPython v1.23.0 on 2024-06-02; Raspberry Pi Pico W with RP2040

## Using a RFID PiicoDev module with Prototyping Cables

I have the PiicoDev RFID Module (NFC 13.56MHz) which I have used successfully with a PiicoDev Cable connected to a Raspberry Pi Pico set in your PiicoDev LiPo Expansion Board.
However, now I am trying to use it with a PiicoDev Prototyping Cable (Male jumper cables) connect to a Raspberry Pi Pico using the labelled colors from your site:

- Black for GND
- Red for V+ with PiicoDev a
- Blue for SDA
- Yellow for SCL

The RFID module turns is LED on when the example app is running, but NFC cards are not read as they previously were with the regular PiicoDev cable.

Is there something I would need to change when using a PiicoDev Prototyping Cable?

The product page notes: PiicoDev expansion boards and adapters have inbuilt 4.7k pull-up resistors and 120 Ohm series resistors on the SDA and SCL lines, so we recommend adding these in if you're plugging straight into your dev board. For a closer look, check out the schematic for your relevant dev board over on our GitHub. What does this mean?  I don't see anything there that helps me understand the difference in the setup when using the prototyping cable with male jumpers.

On the forum I saw some other questions about this, but no accepted solutions there.

I saw one post with this code:

```py
from machine import Pin
from PiicoDev_TMP117 import PiicoDev_TMP117

my_sensor = PiicoDev_TMP117(bus=0, sda=Pin(8), scl=Pin(9), freq=100_000)
```

With the description:
I used the same pins in the example above to show the relation. sda and scl could be any of the Picos I2C pin pairs, where bus defines whether the pins are on the I2C0 or I2C1 bus.

```py
from PiicoDev_RFID import PiicoDev_RFID
from PiicoDev_Unified import sleep_ms
from machine import Pin

rfid = PiicoDev_RFID(bus=0, sda=Pin(8), scl=Pin(9), freq=400_000)

print('Place tag near the PiicoDev RFID Module')

while True:
    if rfid.tagPresent():    # if an RFID tag is present
        id = rfid.readID()
        if (id == "5B:6F:B8:08"):
            print("R12")
        elif (id == "DB:93:B7:08"):
            print("W3 - Clown")
        else:
            print(id)
    sleep_ms(100)
```

If I ```print(rfid)``` I will see this output:

```txt
Place tag near the PiicoDev RFID Module
<PiicoDev_RFID object at 200147a0>
```

With the same RFID module, previously I had added this:

```py
details = rfid.readID(detail=True) # gets more details eg. tag type
```

And seen the following details:

```js
{
 'type': 'classic',
 'id_formatted': '5B:6F:B8:08',
 'success': True,
 'id_integers': [91, 111, 184, 8]
}
```

That is why I was using the id "5B:6F:B8:08" from the working setup before trying to use jumper cable versions.

Trying the PiicoDev® OLED Display Module daisy chained to the RFID module (with the display going via the RFID)
https://core-electronics.com.au/piicodev-oled-display-module-128x64-ssd1306.html

It works and prints to the display:

```py
from PiicoDev_SSD1306 import *
display = create_PiicoDev_SSD1306()

display.text("Hello, World!", 0,0, 1) # literal string
display.show()
```

So I know the power on the RFID module works, and I know the display daisy chained via it works.

It seems to be a faulty RFID module.  I tested the same daisy chain setup with a different module and the above code works.

I also found out that there are two types of  Expansion Boards.

- PiicoDev LiPo Expansion Board for Raspberry Pi Pico, SKU: CE07693 Brand: PiicoDev Guides (5)
- PiicoDev Expansion Board for Pico (Non-Recharging), SKU: CE08677 Brand: PiicoDev

I bought  CE07693, so will have to explore how it is charged and how to know/display the battery status, which I have seen code samples of before but will have to search for that again.

The RFID sample code is here:
https://github.com/CoreElectronics/CE-PiicoDev-RFID-MicroPython-Module/blob/main/examples/read_id.py

## Forums links for the prototype cable issue

Piicodev Prototyping Cable
https://forum.core-electronics.com.au/top?period=monthly

PiicoDev RFID Module with Pi Pico not responding
https://forum.core-electronics.com.au/t/piicodev-rfid-module-with-pi-pico-not-responding/13715

## Part Docs Links

Review product	PiicoDev LiPo Expansion

https://core-electronics.com.au/piicodev-lipo-expansion-board-for-raspberry-pi-pico.html

The orientation for the Pico in the expansion board is this:  The Pico tail end has the daisy chain connector as a tail and the power cable goes in the front end.

PiicoDev RFID Module (NFC 13.56MHz)
https://core-electronics.com.au/piicodev-rfid-module.html

[Code samples](https://github.com/CoreElectronics/CE-PiicoDev-RFID-MicroPython-Module/blob/main/examples/read_id.py)

Display module [code samples](https://github.com/CoreElectronics/CE-PiicoDev-SSD1306-MicroPython-Module/blob/main/example/text.py).

RFID module [code samples](https://github.com/CoreElectronics/CE-PiicoDev-RFID-MicroPython-Module)

## Extra notes

Mqtt
https://core-electronics.com.au/guides/raspberry-pi-pico/getting-started-with-mqtt-on-raspberry-pi-pico-w-connect-to-the-internet-of-things/

Arduino ide
https://iotdesignpro.com/articles/getting-started-with-raspberry-pi-pico-w-using-arduino-ide

Bluetooth 
https://picockpit.com/raspberry-pi/everything-about-bluetooth-on-the-raspberry-pi-pico-w/

server: http://192.168.0.135/

Step 1
https://core-electronics.com.au/guides/raspberry-pi-pico/raspberry-pi-pico-w-connect-to-the-internet/

Connected ip = 192.168.0.135

Step 2 with the LED on/off buttons
https://core-electronics.com.au/guides/raspberry-pi-pico/raspberry-pi-pico-w-create-a-simple-http-server/

The Pico W server is listening for two specific query string in the request: 
?led=on and 
?led=off 

<button class="buttonGreen" name="led" value="on" type="submit">LED ON</button>

led_on = request.find('led=on')
This returns 8, which can be tested for.


Button with server question/answers
https://www.reddit.com/r/raspberrypipico/comments/wc0lod/pico_w_web_server_buttons_on_gpio/

Liam's solution forum post.
python package for Pico w web server that updates incoming data without refreshing the browser.
https://forum.core-electronics.com.au/t/homestation-a-pico-w-powered-webpage-dashboard/14900/4

Garage door
https://forum.core-electronics.com.au/t/project-by-michael-wifi-garage-door-controller-with-raspberry-pi-pico-w/14526/9


Issues with connecting:
https://datasheets.raspberrypi.com/picow/connecting-to-the-internet-with-pico-w.pdf
