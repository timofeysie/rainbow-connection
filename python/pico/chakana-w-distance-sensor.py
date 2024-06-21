import glowbit
from PiicoDev_VL53L1X import PiicoDev_VL53L1X
import time

matrix = glowbit.matrix8x8()
distSensor = PiicoDev_VL53L1X()
speed = 0.1

while (True):
    dist = round(distSensor.read()/1800 * 255)
    print(dist)
    RGB = (255,dist,dist)
    red = RGB[0]
    green = RGB[1]
    blue = RGB[2]
    step = -5
    matrix.drawRectangleFill(0,0, 7,7, matrix.rgbColour(red, green, blue)) # center square
    if all( map( lambda x: True if x < 0 else False, [red,green,blue] ) ):
        step = 1
    red += step
    green += step
    blue += step
    matrix.drawRectangleFill(3,0, 4,7, matrix.rgbColour(red, green, blue)) # 4 vertical
    matrix.drawRectangleFill(0,3, 7,4, matrix.rgbColour(red, green, blue)) # 4 horizontal
    matrix.drawRectangleFill(1,1, 6,6, matrix.rgbColour(red, green, blue)) # 4 center sauqre biggest
    if all( map( lambda x: True if x < 0 else False, [red,green,blue] ) ):
        step = 1
    red += step
    green += step
    blue += step
    matrix.drawRectangleFill(3,1, 4,6, matrix.rgbColour(red, green, blue)) # 3 vertical
    matrix.drawRectangleFill(1,3, 6,4, matrix.rgbColour(red, green, blue)) # 3 horizontal
    matrix.drawRectangleFill(2,2, 5,5, matrix.rgbColour(red, green, blue)) # 3 center sauqre bigger
    if all( map( lambda x: True if x < 0 else False, [red,green,blue] ) ):
        step = 1
    red += step
    green += step
    blue += step
    matrix.drawRectangleFill(3,2, 4,5, matrix.rgbColour(red, green, blue)) # 2 vertical
    matrix.drawRectangleFill(2,3, 5,4, matrix.rgbColour(red, green, blue)) # 2 horizontal
    if all( map( lambda x: True if x < 0 else False, [red,green,blue] ) ):
        step = 1
    red += step
    green += step
    blue += step
    matrix.drawRectangleFill(3,3, 4,4, matrix.rgbColour(red, green, blue)) # 1 center square
    matrix.pixelsShow()
    time.sleep(speed)
    matrix.pixelsShow()
    if all( map( lambda x: True if x < 0 else False, [red,green,blue] ) ):
        step = 1
    red += step
    green += step
    blue += step
