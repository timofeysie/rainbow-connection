# Emoji OS Demo Mode 1

import glowbit
from machine import Pin
import time
from emojis import *

matrix = glowbit.matrix8x8()
matrix.pixelsFill(matrix.black())

pause = 60
halfPause = 50

# draw the chosen emoji and reset values
def draw_emoji():
    matrix = glowbit.matrix8x8(rateLimitCharactersPerSecond = 2)
    #==========
    print("hello")
    matrix.addTextScroll("hello")

    print("scrolling")
    scroll_large_image()

    print("human as nature")
    matrix.addTextScroll("human as nature, nature as human, welcome to the show ... ")
    while matrix.scrollingText == True:
        matrix.updateTextScroll()
        matrix.pixelsShow()
    time.sleep(1)
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
    #==========
    #POSITIVE 1
    # fireworks
    print("menu 1 pos 1 fireworks ")
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

    print("Animism")
    matrix.addTextScroll("The ancient idea of Animism recognizes the potential of all nature to be animated and alive, possessing distinctive spirits.")
    while matrix.scrollingText == True:
        matrix.updateTextScroll()
        matrix.pixelsShow()
    time.sleep(1)

# start
while True:
    draw_emoji()

