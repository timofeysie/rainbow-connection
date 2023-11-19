from PiicoDev_VL53L1X import PiicoDev_VL53L1X
from time import sleep
from machine import Pin

button = Pin(14, Pin.IN, Pin.PULL_DOWN)
led = Pin(15, Pin.OUT)
last_state = False;
current_state = False;

distSensor = PiicoDev_VL53L1X()

while True:
    dist = distSensor.read() # read the distance in millimetres
    print(str(dist) + " mm") # convert the number to a string and print
    sleep(0.1)
    current_state = button.value()
    if last_state == 0 and current_state == 1:
        led.toggle()
    
    last_state = current_state


