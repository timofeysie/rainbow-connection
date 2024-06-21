import glowbit
from machine import Pin
import time
from array import *

button = Pin(22, Pin.IN, Pin.PULL_DOWN)
matrix = glowbit.matrix8x8(rateLimitCharactersPerSecond = 1)
count = 0

while True:
    if button.value():
        matrix.pixelsFill(matrix.black())
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
            matrix.drawTriangle(0, 0, 7, 7, 0, 7, matrix.white())
            matrix.pixelsShow()
            time.sleep(0.5)
        if (count == 3):
            print("start 3 - test")
            matrix.pixelsFill(matrix.black())
            T = [[0, 0, 1, 1, 1, 1, 0, 0],
                 [0, 1, 0, 0, 0, 0, 1, 0],
                 [1, 0, 1, 0, 1, 0, 0, 1],
                 [1, 0, 1, 0, 1, 0, 0, 1],
                 [1, 0, 0, 0, 0, 1, 0, 1],
                 [1, 0, 1, 1, 1, 0, 0, 1],
                 [0, 1, 0, 0, 0, 0, 1, 0],
                 --[0, 0, 1, 1, 1, 1, 0, 0]]
            row = 0
            col = 0
            for r in T:
                for c in r:
                    color = matrix.black()
                    if (c > 0):
                        color = matrix.white()
                    print(row, col, color)
                    matrix.pixelSetXY(col, row, color)
                    col += 1
                    print("inc col")
                    if (col > 7):
                        col = 0
                row += 1
                print("inc row")
            matrix.pixelsShow()
            time.sleep(1)
        if (count == 4):
            for i in range(512):
                c =-


                matrix.wheel(i)
                matrix.pixelsFill(c)
                matrix.pixelsShow()
        if (count == 5):
            matrix.addTextScroll("Mahler Symphony Number One")
            while matrix.scrollingText == True:
                matrix.updateTextScroll()
                matrix.pixelsShow()
        if (count == 6):
            matrix.demo()
        count = count + 1
