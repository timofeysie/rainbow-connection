import machine
from machine import Pin
import utime
from PiicoDev_SSD1306 import *

display = create_PiicoDev_SSD1306()
analog_value = machine.ADC(28)
buzzer = Pin(11, Pin.OUT)

while True:
        display.fill(0)
        reading = int(analog_value.read_u16() / 1000)
        if reading > 48:
            print('buzz')
            buzzer.value(1)
            utime.sleep(1)
            buzzer.value(0)
        else:
            buzzer.value(0)
        print("ADC: ",reading)
        display.text("ADC: " + str(reading), 0,0, 1) # use formatted-print
        display.show()
        utime.sleep(1)
