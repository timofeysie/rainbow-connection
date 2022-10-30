import glowbit
from machine import Pin
import time
from array import *

button1 = Pin(22, Pin.IN, Pin.PULL_DOWN)
button2 = Pin(21, Pin.IN, Pin.PULL_DOWN)
button3 = Pin(20, Pin.IN, Pin.PULL_DOWN)
count = 0
last = 11

def draw_screen():
    matrix = glowbit.matrix8x8(rateLimitCharactersPerSecond = 0.7)
    if (count == 0):
        print("0. normal")
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
        time.sleep(1)
        T = [[0, 0, 0, 0, 0, 0, 0, 0],
             [0, 1, 1, 0, 0, 1, 1, 0],
             [1, 1, 1, 1, 1, 1, 1, 1],
             [1, 1, 1, 1, 1, 1, 1, 1],
             [1, 1, 1, 1, 1, 1, 1, 1],
             [0, 1, 1, 1, 1, 1, 1, 0],
             [0, 0, 1, 1, 1, 1, 0, 0],
             [0, 0, 0, 1, 1, 0, 0, 0]]
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
        time.sleep(1)
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
        time.sleep(1)
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
        print("6. finn the human")
        matrix.pixelsFill(matrix.black())
        T = [[matrix.rgbColour(64,196,254), matrix.rgbColour(64,196,254), matrix.rgbColour(255,255,255), matrix.rgbColour(64,196,254), matrix.rgbColour(64,196,254), matrix.rgbColour(64,196,254), matrix.rgbColour(255,255,255), matrix.rgbColour(64,196,254)],
             [matrix.rgbColour(64,196,254), matrix.rgbColour(64,196,254), matrix.rgbColour(255,255,255), matrix.rgbColour(255,255,255), matrix.rgbColour(255,255,255), matrix.rgbColour(255,255,255), matrix.rgbColour(255,255,255), matrix.rgbColour(64,196,254)],
             [matrix.rgbColour(64,196,254), matrix.rgbColour(64,196,254), matrix.rgbColour(255,255,255), matrix.rgbColour(0,0,0), matrix.rgbColour(250,220,100), matrix.rgbColour(250,220,100), matrix.rgbColour(0,0,0), matrix.rgbColour(64,196,254)],
             [matrix.rgbColour(134,188,70), matrix.rgbColour(121,173,65), matrix.rgbColour(255,255,255), matrix.rgbColour(250,220,100), matrix.rgbColour(250,220,100), matrix.rgbColour(250,220,100), matrix.rgbColour(250,220,100), matrix.rgbColour(64,196,254)],
             [matrix.rgbColour(24,88,28), matrix.rgbColour(164,199,122), matrix.rgbColour(121,197,233), matrix.rgbColour(31,140,226), matrix.rgbColour(31,140,226), matrix.rgbColour(31,140,226), matrix.rgbColour(31,140,226), matrix.rgbColour(64,196,254)],
             [matrix.rgbColour(250,220,100), matrix.rgbColour(24,88,28), matrix.rgbColour(31,140,226), matrix.rgbColour(31,140,226), matrix.rgbColour(31,140,226), matrix.rgbColour(31,140,226), matrix.rgbColour(31,140,226), matrix.rgbColour(250,220,100)],
             [matrix.rgbColour(100,216,2), matrix.rgbColour(100,216,2), matrix.rgbColour(11,61,138), matrix.rgbColour(11,61,138), matrix.rgbColour(11,61,138), matrix.rgbColour(11,61,138), matrix.rgbColour(11,61,138), matrix.rgbColour(100,216,2)],
             [matrix.rgbColour(100,216,2), matrix.rgbColour(100,216,2), matrix.rgbColour(250,220,100), matrix.rgbColour(100,216,2), matrix.rgbColour(100,216,2), matrix.rgbColour(100,216,2), matrix.rgbColour(250,220,100), matrix.rgbColour(100,216,2)]]
        row = 0
        col = 0
        for r in T:
            for c in r:
                color = matrix.black()
                matrix.pixelSetXY(col, row, c)
                col += 1
                if (col > 7):
                    col = 0
            row += 1
        matrix.pixelsShow()
        time.sleep(0.5)
    if (count == 7):
        print("7. pikachu")
        matrix.pixelsFill(matrix.black())
        T = [[matrix.rgbColour(255,255,255), matrix.rgbColour(66, 66, 66), matrix.rgbColour(66,66,66), matrix.rgbColour(255,255,255), matrix.rgbColour(255,255,255), matrix.rgbColour(255,255,255), matrix.rgbColour(255,255,255), matrix.rgbColour(64,66,66)],
             [matrix.rgbColour(255,255,255), matrix.rgbColour(255,255,255), matrix.rgbColour(255,236,60), matrix.rgbColour(255,152,0), matrix.rgbColour(255,255,255), matrix.rgbColour(255,255,255), matrix.rgbColour(255,255,255), matrix.rgbColour(255,152,0)],
             [matrix.rgbColour(255,255,255), matrix.rgbColour(255,255,255), matrix.rgbColour(255,255,255), matrix.rgbColour(255,236,60), matrix.rgbColour(255,236,60), matrix.rgbColour(250,220,100), matrix.rgbColour(255,236,60), matrix.rgbColour(255,152,0)],
             [matrix.rgbColour(255,152,0), matrix.rgbColour(255,152,0), matrix.rgbColour(255,255,255), matrix.rgbColour(250,220,100), matrix.rgbColour(0,0,0), matrix.rgbColour(250,220,100), matrix.rgbColour(250,220,100), matrix.rgbColour(0,0,0)],
             [matrix.rgbColour(255,152,0), matrix.rgbColour(255,152,0), matrix.rgbColour(255,255,255), matrix.rgbColour(234,30,4), matrix.rgbColour(254,241,0), matrix.rgbColour(254,241,0), matrix.rgbColour(254,241,0), matrix.rgbColour(255,152,0)],
             [matrix.rgbColour(255,255,255), matrix.rgbColour(162,89,0), matrix.rgbColour(255,255,255), matrix.rgbColour(254,241,0), matrix.rgbColour(230,137,0), matrix.rgbColour(254,241,0), matrix.rgbColour(255,152,0), matrix.rgbColour(255,255,255)],
             [matrix.rgbColour(255,255,255), matrix.rgbColour(176,97,0), matrix.rgbColour(250,238,0), matrix.rgbColour(255,152,0), matrix.rgbColour(251,238,0), matrix.rgbColour(162,89,0), matrix.rgbColour(251,238,0), matrix.rgbColour(255,255,255)],
             [matrix.rgbColour(255,255,255), matrix.rgbColour(255,255,255), matrix.rgbColour(250,238,0), matrix.rgbColour(210,123,0), matrix.rgbColour(162,89,0), matrix.rgbColour(177,98,0), matrix.rgbColour(177,98,0), matrix.rgbColour(255,255,255)]]
        row = 0
        col = 0
        for r in T:
            for c in r:
                color = matrix.black()
                matrix.pixelSetXY(col, row, c)
                col += 1
                if (col > 7):
                    col = 0
            row += 1
        matrix.pixelsShow()
        time.sleep(0.5)
    if (count == 8):
        matrix.addTextScroll("Not sure")
        while matrix.scrollingText == True:
            matrix.updateTextScroll()
            matrix.pixelsShow()
    if (count == 9):
        matrix = glowbit.matrix8x8(rateLimitCharactersPerSecond = 1)
        matrix.fireworks()
    if (count == 10):
        matrix = glowbit.matrix8x8(rateLimitCharactersPerSecond = 20)
        matrix.circularRainbow()
    if (count == 11):
        matrix = glowbit.matrix8x8(rateLimitCharactersPerSecond = 5)
        matrix.rain()

def adjust_count(new_count):
    if new_count > last:
        count = 0
    if new_count < 0:
        count = 11
        print('last ' + str(count))

while True:
    if button1.value():
        count = count - 1
        adjust_count(count)
        draw_screen()
    if button2.value():
        count = 0
        draw_screen()
    if button3.value():
        count = count + 1
        adjust_count(count)
        draw_screen()
    else:
        if count < 0:
            count = 11
        if count > last:
            count = 0
        print("same count " + str(count))
    time.sleep(0.2)
