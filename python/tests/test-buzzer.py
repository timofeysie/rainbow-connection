import machine
from machine import Pin
import utime

buzzer_pin = Pin(11, Pin.OUT)
buzzer_state = 0  # 0 for off, 1 for on

while True:
    print('buzz')
    
    if buzzer_state == 0:
        buzzer_pin.value(1)
        buzzer_state = 1
    else:
        buzzer_pin.value(0)
        buzzer_state = 0

    utime.sleep(1)
