import glowbit
from machine import Pin
import time
from emojis import *

matrix = glowbit.matrix8x8()
matrix.pixelsFill(matrix.black())
button1 = Pin(22, Pin.IN, Pin.PULL_DOWN)
button2 = Pin(21, Pin.IN, Pin.PULL_DOWN)
button3 = Pin(20, Pin.IN, Pin.PULL_DOWN)
buzzer = Pin(11, Pin.OUT)

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
        # time.sleep(0.5)
    if pos == 2:
        matrix.drawRectangleFill(0,2, 1,3, matrix.green()) # 1 center square
        matrix.pixelsShow()
        # time.sleep(0.5)
    if pos == 3:
        matrix.drawRectangleFill(0,4, 1,5, matrix.green()) # 1 center square
        matrix.pixelsShow()
        # time.sleep(0.5)
    if pos == 4:
        matrix.drawRectangleFill(0,6, 1,7, matrix.green()) # 1 center square
        matrix.pixelsShow()
        # time.sleep(0.5)

def draw_neg():
    global neg
    if neg == 1:
        matrix.drawRectangleFill(5,0, 6,1, matrix.red()) # 1 center square
        matrix.pixelsShow()
        # time.sleep(0.5)
    if neg == 2:
        matrix.drawRectangleFill(5,2, 6,3, matrix.red()) # 1 center square
        matrix.pixelsShow()
        # time.sleep(0.5)
    if neg == 3:
        matrix.drawRectangleFill(5,4, 6,5, matrix.red()) # 1 center square
        matrix.pixelsShow()
        # time.sleep(0.5)
    if neg == 4:
        matrix.drawRectangleFill(5,6, 6,7, matrix.red()) # 1 center square
        matrix.pixelsShow()
        # time.sleep(0.5)

def reset_state():
    global state
    global menu
    global pos
    global neg
    state = "none"
    menu = 0
    pos = 0
    neg = 0

def buzz():
    buzzer.value(1)
    time.sleep(0.1)
    buzzer.value(0)

# draw the chosen emoji and reset values
def draw_emoji():
    global state
    global menu
    global pos
    global neg
    print ("draw emoji menu at", menu, "pos at", pos, "neg at", neg)
    matrix = glowbit.matrix8x8(rateLimitCharactersPerSecond = 0.7)
    #==========
    #POSITIVE 0
    # regular
    if (menu == 0 and pos == 1):
        print("menu 0 pos 1 normal")
        regular()
        time.sleep(0.5)
        reset_state()
    # happy
    if (menu == 0 and pos == 2):
        print("menu 0 pos 2 happy")
        happy()
        time.sleep(0.5)
        reset_state()
    # wry
    if (menu == 0 and pos == 3):
        print("menu 0 pos 3 wry")
        wry()
        time.sleep(0.5)
        reset_state()
    # heart bounce
    if (menu == 0 and pos == 4):
        print("menu 0 pos 4 heart bounce")
        heartBounce()
        time.sleep(0.5)
        reset_state()
    # NEGATIVE 0
    # thick lips
    if (menu == 0 and neg == 1):
        print("menu 0 neg 1 thick lips")
        thickLips()
        time.sleep(0.5)
        reset_state()
    # sad
    if (menu == 0 and neg == 2):
        print("menu 0 neg 2 sad")
        sad()
        time.sleep(0.5)
        reset_state()
    # angry
    if (menu == 0 and neg == 3):
        print("menu 0 neg 3 angry")
        angry()
        time.sleep(0.5)
        reset_state()
    # monster
    if (menu == 0 and neg == 4):
        print("menu 0 neg 4 green monster")
        greenMonster()
        time.sleep(0.5)
        reset_state()
    #==========
    #POSITIVE 1
    # fireworks
    if (menu == 1 and pos == 1):
        print("menu 1 pos 1 fireworks")
        matrix = glowbit.matrix8x8(rateLimitCharactersPerSecond = 1)
        matrix.fireworks()
        time.sleep(0.5)
        reset_state()
    # circularRainbow
    if (menu == 1 and pos == 2):
        print("menu 1 pos 2 circularRainbow")
        matrix = glowbit.matrix8x8(rateLimitCharactersPerSecond = 20)
        matrix.circularRainbow()        
        time.sleep(0.5)
        reset_state()
    # ???
    if (menu == 1 and pos == 3):
        print("menu 1 pos 3 ")
        # wry()
        time.sleep(0.5)
        reset_state()
    # ???
    if (menu == 1 and pos == 4):
        print("menu 1 pos 4 ")
        # heartBounce()
        time.sleep(0.5)
        reset_state()
    # NEGATIVE 1
    # rain
    if (menu == 1 and neg == 1):
        print("menu 1 neg 1 rain")
        matrix = glowbit.matrix8x8(rateLimitCharactersPerSecond = 5)
        matrix.rain()
        time.sleep(0.5)
        reset_state()
    # ??
    if (menu == 1 and neg == 2):
        print("menu 1 neg 2 ")
        # sad()
        time.sleep(0.5)
        reset_state()
    # ??
    if (menu == 1 and neg == 3):
        print("menu 1 neg 3")
        # angry()
        time.sleep(0.5)
        reset_state()
    # ??
    if (menu == 1 and neg == 4):
        print("menu 1 neg 4 green monster")
        #greenMonster()
        time.sleep(0.5)
        reset_state()
    #==========
    #POSITIVE 2
    # finn
    if (menu == 2 and pos == 1):
        print("menu 2 pos 1 finn")
        finn()
        time.sleep(0.5)
        reset_state()
    # pikachu
    if (menu == 2 and pos == 2):
        print("menu 2 pos 2 pikachu")
        pikachu()      
        time.sleep(0.5)
        reset_state()
    # crab
    if (menu == 2 and pos == 3):
        print("menu 2 pos 2 crab")
        crab()
        time.sleep(0.5)
        reset_state()
    # frog
    if (menu == 2 and pos == 4):
        print("menu 2 pos 2 frog")
        frog()
        time.sleep(0.5)
        reset_state()
    # NEGATIVE 2
    # bald
    if (menu == 2 and neg == 1):
        print("menu 2 neg 1 bald")
        bald()
        time.sleep(0.5)
        reset_state()
    # surprise
    if (menu == 2 and neg == 2):
        print("menu 2 neg 2 surprise")
        surprise()
        time.sleep(0.5)
        reset_state()
    #==========
    #POSITIVE 3
    # circle
    if (menu == 3 and pos == 1):
        print("menu 3 pos 1 circle")
        matrix.drawCircle(3, 3, 3, matrix.blue())
        matrix.pixelsShow()
        time.sleep(0.5)
        reset_state()
    # yes
    if (menu == 3 and pos == 2):
        print("menu 3 pos 2 pikachu")
        matrix.addTextScroll("YES")
        while matrix.scrollingText == True:
            matrix.updateTextScroll()
            matrix.pixelsShow()   
        time.sleep(0.5)
        reset_state()
    # Somi
    if (menu == 3 and pos == 3):
        print("menu 3 pos 2 pikachu")
        matrix.addTextScroll("Somi")
        while matrix.scrollingText == True:
            matrix.updateTextScroll()
            matrix.pixelsShow()   
        time.sleep(0.5)
        reset_state()
    # NEGATIVE 3
    # X
    if (menu == 3 and neg == 1):
        print("menu 3 neg 1")
        matrix.drawLine(0, 0, 7, 7, matrix.red())
        matrix.drawLine(0, 7, 7, 0, matrix.red())
        matrix.pixelsShow()
        time.sleep(0.5)
        reset_state()
    # no
    if (menu == 3 and neg == 2):
        print("menu 3 neg 2")
        matrix.addTextScroll("NO")
        while matrix.scrollingText == True:
            matrix.updateTextScroll()
            matrix.pixelsShow()   
        time.sleep(0.5)
        reset_state()
    else:
        reset_state()
while True:
    # blocks need to be in reverse order to stop the cascade throguh the conditions
    if button1.value():
        if state == "choosing":
            buzz()
            # increment positive choice
            pos = pos + 1
            neg = 0 # reset any negative value
            check_pos()
            print('button 1 pressed, menu ', menu, "pos", pos)
            matrix.pixelsFill(matrix.black())
            draw_menu()
            draw_pos()
        if state == "start":
            buzz()
            # increment positive choice
            state = "choosing"
            pos = pos + 1
            check_pos()
            print('button 1 pressed, menu ', menu, "pos", pos)
            matrix.pixelsFill(matrix.black())
            draw_menu()
            draw_pos()
    if button2.value():
        buzz()
        if state == "start":
            # start or increment main menu
            menu = menu + 1
            check_menu()
            matrix.pixelsFill(matrix.black())
            draw_menu()
            print('button 2 pressed, menu ', menu, "state", state)
        if state == "none":
            buzz()
            # start or increment main menu
            state = "start"
            check_menu()
            matrix.pixelsFill(matrix.black())
            draw_menu()
            print('button 2 pressed, menu ', menu, "state", state)
        if state == "choosing":
            buzz()
            # done choosing, draw emoji
            state = "done"
            print("finshed, draw emoji")
            matrix.pixelsFill(matrix.black())
            draw_emoji()
    if button3.value():
        buzz()
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
            buzz()
            # increment negative choice
            state = "choosing"
            neg = neg + 1
            check_neg()
            print('button 3 pressed, menu ', menu, "neg", neg)
            matrix.pixelsFill(matrix.black())
            draw_menu()
            draw_neg()
