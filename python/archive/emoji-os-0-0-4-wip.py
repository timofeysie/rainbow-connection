import glowbit
from machine import Pin
import time
from emojis import *

matrix = glowbit.matrix8x8()
matrix.pixelsFill(matrix.black())
button1 = Pin(22, Pin.IN, Pin.PULL_DOWN)
button2 = Pin(21, Pin.IN, Pin.PULL_DOWN)
button3 = Pin(20, Pin.IN, Pin.PULL_DOWN)

menu = 0
pos = 0
neg = 0
state = "none" # start end or none


def check_menu():
    global menu
    if menu > 3:
        menu = 0
    if menu < 0:
        menu = 3

def check_pos():
    global pos
    if pos > 4:
        pos = 1

def check_neg():
    global neg
    if neg > 4:
        neg = 1

# drawing the menu could be considered a training mode
def draw_menu():
    global menu
    if menu == 0:
        matrix.drawRectangleFill(3,0, 4,1, matrix.white()) # 1 center square
        matrix.pixelsShow()
        time.sleep(0.5)
    if menu == 1:
        matrix.drawRectangleFill(3,2, 4,3, matrix.white()) # 1 center square
        matrix.pixelsShow()
        time.sleep(0.5)
    if menu == 2:
        matrix.drawRectangleFill(3,4, 4,5, matrix.white()) # 1 center square
        matrix.pixelsShow()
        time.sleep(0.5)
    if menu == 3:
        matrix.drawRectangleFill(3,6, 4,7, matrix.white()) # 1 center square
        matrix.pixelsShow()
        time.sleep(0.5)

# draw the positive state value.  possibly we will hide these
# pos & neg start at 1.  0 means either one has not been selected
def draw_pos():
    global pos
    if pos == 1:
        matrix.drawRectangleFill(0,0, 1,1, matrix.green()) # 1 center square
        matrix.pixelsShow()
        time.sleep(0.5)
    if pos == 2:
        matrix.drawRectangleFill(0,2, 1,3, matrix.green()) # 1 center square
        matrix.pixelsShow()
        time.sleep(0.5)
    if pos == 3:
        matrix.drawRectangleFill(0,4, 1,5, matrix.green()) # 1 center square
        matrix.pixelsShow()
        time.sleep(0.5)
    if pos == 4:
        matrix.drawRectangleFill(0,6, 1,7, matrix.green()) # 1 center square
        matrix.pixelsShow()
        time.sleep(0.5)

def draw_neg():
    global neg
    if neg == 1:
        matrix.drawRectangleFill(5,0, 6,1, matrix.red()) # 1 center square
        matrix.pixelsShow()
        time.sleep(0.5)
    if neg == 2:
        matrix.drawRectangleFill(5,2, 6,3, matrix.red()) # 1 center square
        matrix.pixelsShow()
        time.sleep(0.5)
    if neg == 3:
        matrix.drawRectangleFill(5,4, 6,5, matrix.red()) # 1 center square
        matrix.pixelsShow()
        time.sleep(0.5)
    if neg == 4:
        matrix.drawRectangleFill(5,6, 6,7, matrix.red()) # 1 center square
        matrix.pixelsShow()
        time.sleep(0.5)

def reset_state():
    global state
    global menu
    global pos
    global neg
    state = "none"
    menu = 0
    pos = 0
    neg = 0

# draw the chosen emoji and reset values
def draw_emoji():
    global state
    global menu
    global pos
    global neg
    print ("draw emoji menu at", menu, "pos at", pos, "neg at", neg)
    matrix = glowbit.matrix8x8(rateLimitCharactersPerSecond = 0.7)
    # regular
    if (menu == 0 and pos == 1):
        print("menu 0 pos 1 normal")
        regular()
        time.sleep(0.5)
        reset_state()

    # sad
    if (menu == 0 and neg == 2):
        print("menu 0 neg 2 sad")
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
        reset_state()
    # happy
    if (menu == 0 and pos == 2):
        print("menu 0 pos 2 happy")
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
        reset_state()
    # thick lips
    if (menu == 0 and neg == 1):
        print("menu 0 neg 1 thick lips")
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
        reset_state()
    else:
        reset_state()
while True:
    # blocks need to be in reverse order to stop the cascade throguh the conditions
    if button1.value():
        if state == "choosing":
            # increment positive choice
            pos = pos + 1
            neg = 0 # reset any negative value
            check_pos()
            print('button 1 pressed, menu ', menu, "pos", pos)
            matrix.pixelsFill(matrix.black())
            draw_menu()
            draw_pos()
        if state == "start":
            # increment positive choice
            state = "choosing"
            pos = pos + 1
            check_pos()
            print('button 1 pressed, menu ', menu, "pos", pos)
            matrix.pixelsFill(matrix.black())
            draw_menu()
            draw_pos()
    if button2.value():
        if state == "start":
            # start or increment main menu
            menu = menu + 1
            check_menu()
            matrix.pixelsFill(matrix.black())
            draw_menu()
            print('button 2 pressed, menu ', menu, "state", state)
        if state == "none":
            # start or increment main menu
            state = "start"
            check_menu()
            matrix.pixelsFill(matrix.black())
            draw_menu()
            print('button 2 pressed, menu ', menu, "state", state)
        if state == "choosing":
            # done choosing, draw emoji
            state = "done"
            print("finshed, draw emoji")
            matrix.pixelsFill(matrix.black())
            draw_emoji()
    if button3.value():
        if state == "choosing":
            # increment negative choice
            neg = neg + 1
            pos = 0 # reset positive
            check_neg()
            print('button 3 pressed, menu ', menu, "neg", neg)
            matrix.pixelsFill(matrix.black())
            draw_menu()
            draw_neg()
        if state == "start":
            # increment negative choice
            state = "choosing"
            neg = neg + 1
            check_neg()
            print('button 3 pressed, menu ', menu, "neg", neg)
            matrix.pixelsFill(matrix.black())
            draw_menu()
            draw_neg()
