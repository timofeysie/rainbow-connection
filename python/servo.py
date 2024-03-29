import machine
import utime

servo = machine.PWM(machine.Pin(13))
servo.freq(50)

def interval_mapping(x, in_min, in_max, out_min, out_max):
    return (x - in_min) * (out_max - out_min) / (in_max - in_min) + out_min

def servo_write(pin, angle):
    pulse_width = interval_mapping(angle, 0, 180, 0.5,2.5)
    duty = int(interval_mapping(pulse_width, 0, 20, 0,65535))
    pin.duty_u16(duty)

while True:
    servo_write(servo, 10)
    utime.sleep_ms(200)
    servo_write(servo, 20)
    utime.sleep_ms(200)
    servo_write(servo, 30)
    utime.sleep_ms(200)
    servo_write(servo, 40)
    utime.sleep_ms(200)
    servo_write(servo, 50)
    utime.sleep_ms(200)
    servo_write(servo, 60)
    utime.sleep_ms(200)
    servo_write(servo, 70)
    utime.sleep_ms(200)
    servo_write(servo, 80)
    utime.sleep_ms(200)
    servo_write(servo, 90)
    utime.sleep_ms(200)
    servo_write(servo, 100)
    utime.sleep_ms(200)