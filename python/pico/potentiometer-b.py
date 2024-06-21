from machine import ADC, Pin
import time

adc = ADC(Pin(26))
x
while True:
    print(adc.read_u16())
    time.sleep(1)