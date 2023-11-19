import glowbit
from machine import Pin
import time
from array import *

button = Pin(22, Pin.IN, Pin.PULL_DOWN)
matrix = glowbit.matrix8x8(rateLimitCharactersPerSecond = 0.7)
count = 0

while True:
    if button.value():
        matrix.pixelsFill(matrix.black())
        if count > 7:
            count = 0
            matrix.pixelsFill(matrix.black())
        if (count == 0):
            print("0. normal")
            matrix.pixelsFill(matrix.black())
            T = [[0, 0, 1, 1, 1, 1, 0, 0],
                 [0, 1, 0, 0, 0, 0, 1, 0],
                 [1, 0, 1, 0, 0, 1, 0, 1],
                 [1, 0, 0, 0, 0, 0, 0, 1],
                 [1, 0, 1, 1, 1, 1, 0, 1],
                 [1, 0, 0, 0, 0, 0, 0, 1],
                 [0, 1, 0, 0, 0, 0, 1, 0],
                 [0, 0, 1, 1, 1, 1, 0, 0]]
            row = 0
            col = 0
            for r in T:
                for c in r:
                    color = matrix.black()
                    if (c > 0):
                        color = matrix.white()
                    matrix.pixelSetXY(col, row, color)
                    col += 1
                    if (col > 7):
                        col = 0
                row += 1
            matrix.pixelsShow()
            time.sleep(0.5)
        if (count == 1):
            print("1. happy")
            matrix.pixelsFill(matrix.black())
            T = [[0, 0, 1, 1, 1, 1, 0, 0],
                 [0, 1, 0, 0, 0, 0, 1, 0],
                 [1, 0, 1, 0, 0, 1, 0, 1],
                 [1, 0, 0, 0, 0, 0, 0, 1],
                 [1, 0, 1, 0, 0, 1, 0, 1],
                 [1, 0, 0, 1, 1, 0, 0, 1],
                 [0, 1, 0, 0, 0, 0, 1, 0],
                 [0, 0, 1, 1, 1, 1, 0, 0]]
            row = 0
            col = 0
            for r in T:
                for c in r:
                    color = matrix.black()
                    if (c > 0):
                        color = matrix.white()
                    matrix.pixelSetXY(col, row, color)
                    col += 1
                    if (col > 7):
                        col = 0
                row += 1
            matrix.pixelsShow()
            time.sleep(0.5)
        if (count == 2):
            print("2. sad")
            matrix.pixelsFill(matrix.black())
            T = [[0, 0, 1, 1, 1, 1, 0, 0],
                 [0, 1, 0, 0, 0, 0, 1, 0],
                 [1, 0, 1, 0, 0, 1, 0, 1],
                 [1, 0, 0, 0, 0, 0, 0, 1],
                 [1, 0, 0, 1, 1, 0, 0, 1],
                 [1, 0, 1, 0, 0, 1, 0, 1],
                 [0, 1, 0, 0, 0, 0, 1, 0],
                 [0, 0, 1, 1, 1, 1, 0, 0]]
            row = 0
            col = 0
            for r in T:
                for c in r:
                    color = matrix.black()
                    if (c > 0):
                        color = matrix.white()
                    matrix.pixelSetXY(col, row, color)
                    col += 1
                    if (col > 7):
                        col = 0
                row += 1
            matrix.pixelsShow()
            time.sleep(0.5)
        if (count == 3):
            print("3. thick lips")
            matrix.pixelsFill(matrix.black())
            T = [[0, 0, 1, 1, 1, 1, 0, 0],
                 [0, 1, 0, 0, 0, 0, 1, 0],
                 [1, 0, 1, 0, 0, 1, 0, 1],
                 [1, 0, 0, 0, 0, 0, 0, 1],
                 [1, 0, 1, 1, 1, 1, 0, 1],
                 [1, 0, 1, 1, 1, 1, 0, 1],
                 [0, 1, 0, 0, 0, 0, 1, 0],
                 [0, 0, 1, 1, 1, 1, 0, 0]]
            row = 0
            col = 0
            for r in T:
                for c in r:
                    color = matrix.black()
                    if (c > 0):
                        color = matrix.white()
                    matrix.pixelSetXY(col, row, color)
                    col += 1
                    if (col > 7):
                        col = 0
                row += 1
            matrix.pixelsShow()
            time.sleep(0.5)
        if (count == 4):
            print("4 heart")
            matrix.pixelsFill(matrix.black())
            T = [[0, 1, 1, 0, 0, 1, 1, 0],
                 [1, 1, 1, 1, 1, 1, 1, 1],
                 [1, 1, 1, 1, 1, 1, 1, 1],
                 [1, 1, 1, 1, 1, 1, 1, 1],
                 [0, 1, 1, 1, 1, 1, 1, 0],
                 [0, 0, 1, 1, 1, 1, 0, 0],
                 [0, 0, 0, 1, 1, 0, 0, 0],
                 [0, 0, 0, 0, 0, 0, 0, 0]]
            row = 0
            col = 0
            for r in T:
                for c in r:
                    color = matrix.black()
                    if (c > 0):
                        color = matrix.red()
                    matrix.pixelSetXY(col, row, color)
                    col += 1
                    if (col > 7):
                        col = 0
                row += 1
            matrix.pixelsShow()
            time.sleep(0.5)
        if (count == 5):
            print("5 wry")
            matrix.pixelsFill(matrix.black())
            T = [[0, 0, 1, 1, 1, 1, 0, 0],
                 [0, 1, 0, 0, 0, 0, 1, 0],
                 [1, 0, 1, 0, 1, 0, 0, 1],
                 [1, 0, 1, 0, 1, 0, 0, 1],
                 [1, 0, 0, 0, 0, 1, 0, 1],
                 [1, 0, 1, 1, 1, 0, 0, 1],
                 [0, 1, 0, 0, 0, 0, 1, 0],
                 [0, 0, 1, 1, 1, 1, 0, 0]]
            row = 0
            col = 0
            for r in T:
                for c in r:
                    color = matrix.black()
                    if (c > 0):
                        color = matrix.white()
                    matrix.pixelSetXY(col, row, color)
                    col += 1
                    if (col > 7):
                        col = 0
                row += 1
            matrix.pixelsShow()
            time.sleep(0.5)
        if (count == 6):
            matrix.addTextScroll("Not sure")
            while matrix.scrollingText == True:
                matrix.updateTextScroll()
                matrix.pixelsShow()
        if (count == 7):
            matrix = glowbit.matrix8x8(rateLimitCharactersPerSecond = 0.5)
            matrix.demo()
        count = count + 1
