# Issues

## Issues modifying the emoji-os-pico.py

Using the pico code to work with the Waveshare 1.44inch LCD HAT on a Raspberry Pi Zero 2 W was not working after a few attempts.

I think the code written for the emoji-os-zero.py still needs some work.  When I try to run it on the zero with the waveshare 1.44inch LED hat, I am seeing this error:

```sh
tim@raspberrypi:~/emoji-os $ python emoji-os-zero.py
Traceback (most recent call last):
  File "/usr/lib/python3/dist-packages/gpiozero/pins/pi.py", line 411, in pin
    pin = self.pins[info]
          ~~~~~~~~~^^^^^^
KeyError: PinInfo(number=31, name='GPIO6', names=frozenset({'BOARD31', 6, 'GPIO6', '6', 'J8:31', 'BCM6', 'WPI22'}), pull='', row=16, col=1, interfaces=frozenset({'', 'uart', 'gpio', 'smi', 'spi', 'i2c', 'dpi'}))

During handling of the above exception, another exception occurred:

Traceback (most recent call last):
  File "/home/tim/emoji-os/emoji-os-zero.py", line 32, in <module>
    disp = LCD_1in44.LCD()
           ^^^^^^^^^^^^^^^
  File "/home/tim/emoji-os/config.py", line 63, in __init__
    self.GPIO_KEY_UP_PIN     = self.gpio_mode(KEY_UP_PIN,self.INPUT,True,None)
                               ^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^
  File "/home/tim/emoji-os/config.py", line 84, in gpio_mode
    return DigitalInputDevice(Pin,pull_up=pull_up,active_state=active_state)
           ^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^               ^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^
  File "/usr/lib/python3/dist-packages/gpiozero/input_devices.py", line 162, in __init__
    super().__init__(
  File "/usr/lib/python3/dist-packages/gpiozero/mixins.py", line 243, in __init__
    super().__init__(*args, **kwargs)
  File "/usr/lib/python3/dist-packages/gpiozero/input_devices.py", line 79, in __init__
    super().__init__(pin, pin_factory=pin_factory)
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

Both libraries are trying to use the same GPIO pin (in your case, GPIO 6, 19, etc.), and this causes a conflict?  Since our demo code runs which is seen in the key_demo.py script, how about we apply our menu and emoji selection code to the working wy_demo.py so that we can proceed from a working standpoint?

But I still see the runtime error: "Please set pin numbering mode using GPIO.setmode(GPIO.BOARD) or GPIO.setmode(GPIO.BCM)" at line 24.
