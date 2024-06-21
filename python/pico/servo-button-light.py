from PiicoDev_VL53L1X import PiicoDev_VL53L1X
from time import sleep
from machine import Pin
import utime
distSensor = PiicoDev_VL53L1X()
button = Pin(14, Pin.IN, Pin.PULL_DOWN)
led = Pin(15, Pin.OUT)
last_state = False;
current_state = False;
def button_callback(pin):
    if led.value() == 0:
        servo_run()
        led.toggle()
        print('-----------1')
        print('led1', led.value())
    else:
        servo_write(servo, 10)
        led.toggle()
        print('-----------2')
    print('led1', led.value())
button.irq(button_callback, Pin.IRQ_RISING | Pin.IRQ_FALLING)
servo = machine.PWM(machine.Pin(13))
servo.freq(50)

def interval_mapping(x, in_min, in_max, out_min, out_max):
    return (x - in_min) * (out_max - out_min) / (in_max - in_min) + out_min

def servo_write(pin, angle):
    pulse_width = interval_mapping(angle, 0, 180, 0.5,2.5)
    duty = int(interval_mapping(pulse_width, 0, 20, 0,65535))
    pin.duty_u16(duty)

def servo_run():
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

while True:
    dist = distSensor.read() # read the distance in millimetres
    #print(str(dist) + " mm") # convert the number to a string and print
    sleep(0.1)
