import glowbit
from machine import Pin
import time
from emojis import *

matrix = glowbit.matrix8x8()
matrix.pixelsFill(matrix.black())

pause = 100
halfPause = 50

# draw the chosen emoji and reset values
def draw_emoji():
    matrix = glowbit.matrix8x8(rateLimitCharactersPerSecond = 1)
    #==========
    print("hello")
    matrix.addTextScroll("hello")

    print("scroll cloud_landscape")
    while matrix.scrollingText == True:
        matrix.updateTextScroll()
        matrix.pixelsShow()
    time.sleep(1)
    scroll_cloud_landscape()

    print("scrolling")
    scroll_large_image()

    print("scroll_large_image2")
    scroll_large_image2()

    print("human as nature")
    matrix.addTextScroll("human as nature, nature as human, welcome to the show ... ")
    while matrix.scrollingText == True:
        matrix.updateTextScroll()
        matrix.pixelsShow()
    time.sleep(1)

    print("menu 0 pos 1 normal")
    regular()
    time.sleep(halfPause)
    # happy
    print("menu 0 pos 2 happy")
    happy()
    time.sleep(halfPause)
    # wry
    print("menu 0 pos 3 wry")
    wry()
    time.sleep(halfPause)
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
    time.sleep(halfPause)
    # sad
    print("menu 0 neg 2 sad")
    sad()
    time.sleep(halfPause)
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

    # bald
    print("menu 2 neg 1 bald")
    bald()
    time.sleep(pause)

    # surprise
    print("menu 2 neg 2 surprise")
    surprise()
    time.sleep(pause)

    # circle
    print("menu 3 pos 1 circle")
    matrix.drawCircle(3, 3, 3, matrix.blue())
    matrix.pixelsShow()
    time.sleep(halfPause)

    print("Animism")
    matrix.addTextScroll("The ancient idea of Animism recognizes the potential of all nature to be animated and alive, possessing distinctive spirits.  This is instinctive for young artists, and fits in well with the Human as Nature theme.  In this case, nature is also human, as the cloud enjoys raining on the people, and the sun joyfully placates the cloud to a small friend to bring it's sunshine back.")
    while matrix.scrollingText == True:
        matrix.updateTextScroll()
        matrix.pixelsShow()
    time.sleep(1)

# start
while True:
    draw_emoji()
