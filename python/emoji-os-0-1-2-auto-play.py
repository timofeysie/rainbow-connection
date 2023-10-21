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
pause = 100

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
    print("scrolling")
    scroll_large_image()
    print("menu 0 pos 1 normal")
    regular()
    time.sleep(pause)
    # happy
    print("menu 0 pos 2 happy")
    happy()
    time.sleep(pause)
    # wry
    print("menu 0 pos 3 wry")
    wry()
    time.sleep(pause)
    # heart bounce
    print("menu 0 pos 4 heart bounce")
    heartBounce()
    heartBounce()
    heartBounce()
    heartBounce()
    heartBounce()
    heartBounce()
    heartBounce()
    heartBounce()
    heartBounce()
    # NEGATIVE 0
    # thick lips
    print("menu 0 neg 1 thick lips")
    thickLips()
    time.sleep(pause)
    # sad
    print("menu 0 neg 2 sad")
    sad()
    time.sleep(pause)
    # angry
    print("menu 0 neg 3 angry")
    angry()
    time.sleep(pause)
    # monster
    print("menu 0 neg 4 green monster")
    greenMonster()
    time.sleep(pause)
    #==========
    #POSITIVE 1
    # fireworks
    print("menu 1 pos 1 fireworks " + state)
    matrix = glowbit.matrix8x8(rateLimitCharactersPerSecond = 1)
    matrix.fireworks()
    matrix.fireworks()
    matrix.fireworks()
    matrix.fireworks()
    matrix.fireworks()
    matrix.fireworks()
    # circularRainbow
    print("menu 1 pos 2 circularRainbow")
    matrix = glowbit.matrix8x8(rateLimitCharactersPerSecond = 20)
    matrix.circularRainbow()
    matrix.circularRainbow()
    matrix.circularRainbow()
    matrix.circularRainbow()
    matrix.circularRainbow()
    matrix.circularRainbow()
    matrix.circularRainbow()
    matrix.circularRainbow()
    # rain
    print("menu 1 neg 1 rain")
    matrix = glowbit.matrix8x8(rateLimitCharactersPerSecond = 5)
    matrix.rain()
    matrix.rain()
    matrix.rain()
    matrix.rain()
    matrix.rain()
    matrix.rain()
    matrix.rain()
    matrix.rain()
    matrix.rain()
    matrix.rain()
    matrix.rain()
    #==========
    #POSITIVE 2
    # finn
    print("menu 2 pos 1 finn")
    finn()
    time.sleep(pause)
    # pikachu
    print("menu 2 pos 2 pikachu")
    pikachu()
    time.sleep(pause)
    # crab
    print("menu 2 pos 2 crab")
    crab()
    time.sleep(pause)
    # frog
    print("menu 2 pos 2 frog")
    frog()
    time.sleep(pause)
    # NEGATIVE 2
    # bald
    print("menu 2 neg 1 bald")
    bald()
    time.sleep(pause)
    # surprise
    print("menu 2 neg 2 surprise")
    surprise()
    time.sleep(pause)
    #==========
    #POSITIVE 3
    # circle
    print("menu 3 pos 1 circle")
    matrix.drawCircle(3, 3, 3, matrix.blue())
    matrix.pixelsShow()
    time.sleep(pause)
    # yes
    print("menu 3 pos 2 pikachu")
    matrix.addTextScroll("YES")
    while matrix.scrollingText == True:
        matrix.updateTextScroll()
        matrix.pixelsShow()
    time.sleep(pause)
    # Somi
    print("menu 3 pos 2 pikachu")
    matrix.addTextScroll("Somi")
    while matrix.scrollingText == True:
        matrix.updateTextScroll()
        matrix.pixelsShow()
    time.sleep(pause)
    # NEGATIVE 3
    # X
    print("menu 3 neg 1")
    matrix.drawLine(0, 0, 7, 7, matrix.red())
    matrix.drawLine(0, 7, 7, 0, matrix.red())
    matrix.pixelsShow()
    time.sleep(pause)
    # no
    print("menu 3 neg 2")
    matrix.addTextScroll("NO")
    while matrix.scrollingText == True:
        matrix.updateTextScroll()
        matrix.pixelsShow()
    time.sleep(pause)

# start
while True:
    draw_emoji()
