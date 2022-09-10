from machine import Pin
import time

led = Pin(15, Pin.OUT)
button = Pin(14, Pin.IN, Pin.PULL_DOWN)
mode = 'a'

while True:
    if button.value():
        led.toggle()
        time.sleep(0.5)
        print('mode a')
    else:
        print('mode b')
        time.sleep(0.5)
