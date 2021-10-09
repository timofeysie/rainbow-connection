import machine
import utime

pot=machine.ADC(28)

while True:
    value = pot.read_u16()
    print(value)
    utime.sleep_ms(200)