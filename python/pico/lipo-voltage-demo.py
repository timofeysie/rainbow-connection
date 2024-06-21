# This example shows how to read the voltage from a lipo battery connected to a Raspberry Pi Pico via our Pico Lipo SHIM, and uses this reading to calculate how much charge is left in the battery.
# It then displays the info on the screen of Pico Display or Pico Explorer.
# Remember to save this code as main.py on your Pico if you want it to run automatically!

from machine import ADC, Pin
import utime

# Set up and initialise display
buf = bytearray(display.get_width() * display.get_height() * 2)

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
        print("Charging!", 15, 55, 240, 4)
    else:                          98i   # if not, display the battery stats
        print('{:.2f}'.format(voltage) + "v", 15, 10, 240, 5)
        print('{:.0f}%'.format(percentage), 15, 50, 240, 5)

    utime.sleep(1)