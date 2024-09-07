# This is a combination test designed by starting with the nfc test code
# and combining with the glowbit test and adding the test-3-button code
# along with some emojis.  It might be helpful to have a purely diagnostic
# script like this to test all the integrated hardware before assembly.
 
from PiicoDev_RFID import PiicoDev_RFID
from PiicoDev_Unified import sleep_ms
from PiicoDev_SSD1306 import *
import glowbit
from machine import Pin
import time

button1 = Pin(22, Pin.IN, Pin.PULL_DOWN)
button2 = Pin(21, Pin.IN, Pin.PULL_DOWN)
button3 = Pin(20, Pin.IN, Pin.PULL_DOWN)

rfid = PiicoDev_RFID()   # Initialise the RFID module

print('Place tag near the PiicoDev RFID Module')
print(rfid)

matrix = glowbit.matrix8x8()

matrix.drawCircle(3, 3, 3, matrix.blue())
matrix.pixelsShow()

def regular():
    print("regular")
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
def sad():
    print("sad")
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
def happy():
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

while True:
    if button1.value():
        print('button 1 pin 22')
        sad()
        time.sleep(0.5)
    if button2.value():
        print('button 2 pin 21')
        regular()
        time.sleep(0.5)
    if button3.value():
        print('button 3 pin 20')
        happy()
        time.sleep(0.5)
    
    if rfid.tagPresent():    # if an RFID tag is present
        id = rfid.readID()   # get the id
        if (id == "5B:6F:B8:08"):
            print("R12")
        elif (id == "DB:93:B7:08"):
            print("W3 - Clown")
        elif (id == "CB:61:B8:08"):
            print("9")
            matrix.drawRectangle(0,0, 7,7, matrix.white())
            matrix.pixelsShow()
        else:
            print(id)
    sleep_ms(100)
