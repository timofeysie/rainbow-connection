import machine
import utime

servo = machine.PWM(machine.Pin(15))
servo.freq(50)
pot=machine.ADC(28)

def interval_mapping(x, in_min, in_max, out_min, out_max):
    return (x - in_min) * (out_max - out_min) / (in_max - in_min) + out_min

def servo_write(pin, angle):
    pulse_width = interval_mapping(angle, 0, 180, 0.5,2.5)
    duty = int(interval_mapping(pulse_width, 0, 20, 0,65535))
    pin.duty_u16(duty)

while True:
    value = pot.read_u16()
    servo_write(servo, value / 100)
    print(value)
    utime.sleep_ms(200)
    