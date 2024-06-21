import glowbit
from machine import Pin
import time
from array import *

button = Pin(22, Pin.IN, Pin.PULL_DOWN)

count = 0

matrix = glowbit.matrix8x8()
while True:
    if button.value():
        matrix.pixelsFill(matrix.black())
        count = count + 1
        if count > 6:
            count = 0
            matrix.pixelsFill(matrix.black())
        print(count)
        if (count == 0):
            matrix.drawCircle(3, 3, 3, matrix.white())
            matrix.pixelsShow()
            time.sleep(0.5)
        if (count == 1):
            matrix.drawRectangle(0,0, 7,7, matrix.white())
            matrix.pixelsShow()
            time.sleep(0.5)
        if (count == 2):
            matrix.drawTriangle(0, 0, 3, 3, 7, 7, matrix.white())
            matrix.pixelsShow()
            time.sleep(0.5)
        if (count == 3):
            matrix.pixelsFill(matrix.black())
            T = [[11, 12, 5, 2], [15, 6, 10, 0], [10, 8, 12, 5], [12, 15, 8, 6]]
            for i, r in T:
                for j, c in r:
                    color = matrix.black()
                    if (r > 0)
                        matrix.pixelSetXY(i, j, matrix.yellow())
        if (count == 4):
            for i in range(512):
                c = matrix.wheel(i)
                matrix.pixelsFill(c)
                matrix.pixelsShow()
        if (count == 5):
            matrix.addTextScroll("Hello there!")
            while matrix.scrollingText == True:
                matrix.updateTextScroll()
                matrix.pixelsShow()
        if (count == 6):
            matrix.demo()
