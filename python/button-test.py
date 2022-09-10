from machine import Pin
import time

button = Pin(22, Pin.IN, Pin.PULL_DOWN)
mode = 'a'

while True:
    if button.value():
        print('mode a: button pressed')
        time.sleep(0.5)
    else:
        print('mode b: not pressed')
        time.sleep(0.5)
