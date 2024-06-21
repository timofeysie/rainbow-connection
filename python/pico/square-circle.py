import glowbit
from machine import Pin
import time

button = Pin(22, Pin.IN, Pin.PULL_DOWN)

matrix = glowbit.matrix8x8()
while True:
    if button.value():
        matrix.pixelsFill(matrix.black())
        matrix.drawCircle(3, 3, 3, matrix.white())
        matrix.pixelsShow()
        time.sleep(0.5)
    else:
        matrix.pixelsFill(matrix.black())
        matrix.drawRectangle(0,0, 7,7, matrix.white())
        matrix.pixelsShow()
        time.sleep(0.5)
