from machine import Pin
button = Pin(14, Pin.IN, Pin.PULL_DOWN)


while True:
        print('value', button.value())