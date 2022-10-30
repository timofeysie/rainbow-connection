from machine import Pin
import time

button1 = Pin(22, Pin.IN, Pin.PULL_DOWN)
button2 = Pin(21, Pin.IN, Pin.PULL_DOWN)
button3 = Pin(20, Pin.IN, Pin.PULL_DOWN)

while True:
    if button1.value():
        print('button 1 pin 22')
        time.sleep(0.5)
    if button2.value():
        print('button 2 pin 21')
        time.sleep(0.5)
    if button3.value():
        print('button 3 pin 20')
        time.sleep(0.5)
    else:
        print('buttons not pressed')
        time.sleep(0.5)
