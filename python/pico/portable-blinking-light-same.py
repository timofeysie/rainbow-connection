from machine import Pin
import utime
trigger = Pin(3, Pin.OUT)
echo = Pin(2, Pin.IN)
signalon = utime.ticks_us()
signaloff = utime.ticks_us()
while True:
    utime.sleep_us(1)
    trigger.low()
    utime.sleep_us(1)
    trigger.high()
    utime.sleep_us(1)
    trigger.low()
    while echo.value() == 0:
        signaloff = utime.ticks_us()
    while echo.value() == 1:
        signalon = utime.ticks_us()
    timepassed = signalon - signaloff
    distance = (timepassed * 0.0343) / 2
    print("The distance from object is ",distance,"cm")
    utime.sleep(1)
