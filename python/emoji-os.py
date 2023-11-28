# emoji os v0.1.4
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
# preserve the previous state for pos/neg flipping
prev_menu = 0
prev_pos = 0
prev_neg = 0
prev_state = "none" # or done
pause = 0.2

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
    global pause
    if menu == 0:
        matrix.drawRectangleFill(3,0, 4,1, matrix.white()) # 1 center square
        matrix.pixelsShow()
        time.sleep(pause)
    if menu == 1:
        matrix.drawRectangleFill(3,2, 4,3, matrix.white()) # 1 center square
        matrix.pixelsShow()
        time.sleep(pause)
    if menu == 2:
        matrix.drawRectangleFill(3,4, 4,5, matrix.white()) # 1 center square
        matrix.pixelsShow()
        time.sleep(pause)
    if menu == 3:
        matrix.drawRectangleFill(3,6, 4,7, matrix.white()) # 1 center square
        matrix.pixelsShow()
        time.sleep(pause)

# draw the positive state value.  possibly we will hide these
# pos & neg start at 1.  0 means either one has not been selected
def draw_pos():
    global pos
    if pos == 1:
        matrix.drawRectangleFill(0,0, 1,1, matrix.green()) # 1 center square
        matrix.pixelsShow()
        time.sleep(pause)
    if pos == 2:
        matrix.drawRectangleFill(0,2, 1,3, matrix.green()) # 1 center square
        matrix.pixelsShow()
        time.sleep(pause)
    if pos == 3:
        matrix.drawRectangleFill(0,4, 1,5, matrix.green()) # 1 center square
        matrix.pixelsShow()
        time.sleep(pause)
    if pos == 4:
        matrix.drawRectangleFill(0,6, 1,7, matrix.green()) # 1 center square
        matrix.pixelsShow()
        time.sleep(pause)

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
    global prev_state
    global prev_menu
    global prev_pos
    global prev_neg
    prev_state = "done"
    prev_menu = menu
    prev_pos = pos
    prev_neg = neg
    state = "none"
    menu = 0
    pos = 0
    neg = 0

def reset_prev():
    global prev_state
    global prev_menu
    global prev_pos
    global prev_neg
    prev_state = "none"
    prev_menu = 0
    prev_pos = 0
    prev_neg = 0
    
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
    print ("draw emoji menu at", menu, "pos at", pos, "neg at", neg, "state", state)
    matrix = glowbit.matrix8x8(rateLimitCharactersPerSecond = 0.7)
    #==========
    #POSITIVE 0
    # regular
    if (menu == 0 and pos == 1):
        print("menu 0 pos 1 normal")
        regular()
    # happy
    if (menu == 0 and pos == 2):
        print("menu 0 pos 2 happy")
        happy()
    # wry
    if (menu == 0 and pos == 3):
        print("menu 0 pos 3 wry")
        wry()
    # heart bounce
    if (menu == 0 and pos == 4):
        print("menu 0 pos 4 heart bounce")
        heartBounce()
    # NEGATIVE 0
    # thick lips
    if (menu == 0 and neg == 1):
        print("menu 0 neg 1 thick lips")
        thickLips()
    # sad
    if (menu == 0 and neg == 2):
        print("menu 0 neg 2 sad")
        sad()
    # angry
    if (menu == 0 and neg == 3):
        print("menu 0 neg 3 angry")
        angry()
    # monster
    if (menu == 0 and neg == 4):
        print("menu 0 neg 4 green monster")
        greenMonster()
    #==========
    #POSITIVE 1
    # fireworks
    if (menu == 1 and pos == 1):
        print("menu 1 pos 1 fireworks " + state)
        matrix = glowbit.matrix8x8(rateLimitCharactersPerSecond = 1)
        matrix.fireworks()
    # circularRainbow
    if (menu == 1 and pos == 2):
        print("menu 1 pos 2 circularRainbow")
        matrix = glowbit.matrix8x8(rateLimitCharactersPerSecond = 20)
        matrix.circularRainbow()
    # scroll_large_image
    if (menu == 1 and pos == 3):
        print("menu 1 pos 3 scroll_large_image")
        print("scrolling")
        scroll_large_image()
    # chakana
    if (menu == 1 and pos == 4):
        print("menu 1 pos 4 chacana")
        chakana()
    # NEGATIVE 1
    # rain
    if (menu == 1 and neg == 1):
        print("menu 1 neg 1 rain")
        matrix = glowbit.matrix8x8(rateLimitCharactersPerSecond = 5)
        matrix.rain()
    # ??
    if (menu == 1 and neg == 2):
        print("menu 1 neg 2 ")
        # sad()
    # ??
    if (menu == 1 and neg == 3):
        print("menu 1 neg 3")
        # angry()
    # ??
    if (menu == 1 and neg == 4):
        print("menu 1 neg 4 green monster")
        #greenMonster()
    #==========
    #POSITIVE 2
    # finn
    if (menu == 2 and pos == 1):
        print("menu 2 pos 1 finn")
        finn()
    # pikachu
    if (menu == 2 and pos == 2):
        print("menu 2 pos 2 pikachu")
        pikachu()
    # crab
    if (menu == 2 and pos == 3):
        print("menu 2 pos 2 crab")
        crab()
    # frog
    if (menu == 2 and pos == 4):
        print("menu 2 pos 2 frog")
        frog()
    # NEGATIVE 2
    # bald
    if (menu == 2 and neg == 1):
        print("menu 2 neg 1 bald")
        bald()
    # surprise
    if (menu == 2 and neg == 2):
        print("menu 2 neg 2 surprise")
        surprise()
    #==========
    #POSITIVE 3
    # circle
    if (menu == 3 and pos == 1):
        print("menu 3 pos 1 circle")
        matrix.drawCircle(3, 3, 3, matrix.blue())
        matrix.pixelsShow()
    # yes
    if (menu == 3 and pos == 2):
        print("menu 3 pos 2 pikachu")
        matrix.addTextScroll("YES")
        while matrix.scrollingText == True:
            matrix.updateTextScroll()
            matrix.pixelsShow()
    # Somi
    if (menu == 3 and pos == 3):
        print("menu 3 pos 2 pikachu")
        matrix.addTextScroll("Somi")
        while matrix.scrollingText == True:
            matrix.updateTextScroll()
            matrix.pixelsShow()
    # NEGATIVE 3
    # X
    if (menu == 3 and neg == 1):
        print("menu 3 neg 1")
        matrix.drawLine(0, 0, 7, 7, matrix.red())
        matrix.drawLine(0, 7, 7, 0, matrix.red())
        matrix.pixelsShow()
    # no
    if (menu == 3 and neg == 2):
        print("menu 3 neg 2")
        matrix.addTextScroll("NO")
        while matrix.scrollingText == True:
            matrix.updateTextScroll()
            matrix.pixelsShow()
    else:
        # do we need this in scrolling mode?
        reset_state()
while True:
    # blocks need to be in reverse order to stop the cascade throguh the conditions
    if button1.value():
        print('debug btn 1 menu ', menu, "pos", pos, "neg", neg, "state", state, "prev_pos", prev_pos, "prev_neg", prev_neg, "prev_state", prev_state)
        if state == "choosing":
            buzz()
            # increment positive choice
            pos = pos + 1
            neg = 0 # reset any negative value
            check_pos()
            print('button 1 pressed, menu ', menu, "pos", pos, "state", state)
            matrix.pixelsFill(matrix.black())
            draw_menu()
            draw_pos()
        if state == "start":
            buzz()
            # increment positive choice
            state = "choosing"
            pos = pos + 1
            check_pos()
            print('button 1 pressed, menu ', menu, "pos", pos, "state", state)
            matrix.pixelsFill(matrix.black())
            draw_menu()
            draw_pos()
        if prev_state == "done":
            if (prev_neg > 0):
                # reverse previous neg choice
                buzz()
                matrix.pixelsFill(matrix.black())
                pos = prev_neg
                neg = 0
                menu = prev_menu
                print('button 1 pressed again, menu ', menu, "pos", pos, "neg", neg, "state", state)
                draw_emoji()
            if (prev_pos > 0):
                # play last pos
                buzz()
                matrix.pixelsFill(matrix.black())
                pos = prev_pos
                neg = 0
                menu = prev_menu
                print('button 3 pressed again, menu ', menu, "pos", pos, "neg", neg, "state", state)
                draw_emoji()
    if button2.value():
        reset_prev()
        print('debug btn 2 menu ', menu, "pos", pos, "neg", neg, "state", state, "prev_pos", prev_pos, "prev_neg", prev_neg, "prev_state", prev_state)
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
            print("finshed, draw emoji")
            matrix.pixelsFill(matrix.black())
            draw_emoji()
    if button3.value():
        print('debug btn 3 menu ', menu, "pos", pos, "neg", neg, "state", state, "prev_pos", prev_pos, "prev_neg", prev_neg, "prev_state", prev_state)
        buzz()
        if state == "choosing":
            # increment negative choice
            neg = neg + 1
            pos = 0 # reset positive
            check_neg()
            print('button 3 pressed, menu ', menu, "neg", neg, "state", state)
            matrix.pixelsFill(matrix.black())
            draw_menu()
            draw_neg()
        if state == "start":
            buzz()
            # increment negative choice
            state = "choosing"
            neg = neg + 1
            check_neg()
            print('button 3 pressed, menu ', menu, "neg", neg, "state", state)
            matrix.pixelsFill(matrix.black())            
            draw_menu()
            draw_neg()
        if prev_state == "done":
            print("prev_pos", prev_pos)
            if (prev_pos > 0):
                # toggle pos to neg response
                buzz()
                matrix.pixelsFill(matrix.black())
                neg = prev_pos
                pos = 0
                menu = prev_menu
                print('button 3 pressed again, menu ', menu, "pos", pos, "neg", neg, "state", state)
                draw_emoji()
            if (prev_neg > 0):
                # play last neg
                buzz()
                matrix.pixelsFill(matrix.black())
                neg = prev_neg
                pos = 0
                menu = prev_menu
                print('button 3 pressed again, menu ', menu, "pos", pos, "neg", neg, "state", state)
                draw_emoji()
