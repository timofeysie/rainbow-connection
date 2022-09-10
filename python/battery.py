from machine import ADC, Pin
import utime
import time
led = Pin(15, Pin.OUT)
def blink(timer):
    led.toggle()
timer.init(freq=2.5, mode=Timer.PERIODIC, callback=blink)
vsys = ADC(29)              # reads the system input voltage
charging = Pin(24, Pin.IN)  # reading GP24 tells us whether or not USB power is connected
conversion_factor = 3 * 3.3 / 65535
full_battery = 4.2                  # these are our reference voltages for a full/empty battery, in volts
empty_battery = 2.8                 # the values could vary by battery size/manufacturer so you might need to adjust them
while True:
    voltage = vsys.read_u16() * conversion_factor
    percentage = 100 * ((voltage - empty_battery) / (full_battery - empty_battery))
    if percentage > 100:
        percentage = 100.00
    if charging.value() == 1:         # if it's plugged into USB power...
        print("Charging:", voltage, percentage)
    else:                            # if not, display the battery stats
        print('{:.2f}'.format(voltage) + "v", 15, 10, 240, 5)
        print('{:.0f}%'.format(percentage), 15, 50, 240, 5)
        # led.high()
        utime.sleep(.25)
        # led.low()
        # utime.sleep(.25)
