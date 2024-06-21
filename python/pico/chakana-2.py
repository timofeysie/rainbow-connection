import glowbit
import time

matrix = glowbit.matrix8x8()

while (True):
    matrix.pixelsFill(matrix.black())
    matrix.drawRectangleFill(3,3, 4,4, matrix.white()) # center square
    matrix.pixelsShow()
    time.sleep(1)

    matrix.drawRectangleFill(3,2, 4,5, matrix.yellow()) # vertical
    matrix.drawRectangleFill(2,3, 5,4, matrix.yellow()) # horizontal
    matrix.drawRectangleFill(3,3, 4,4, matrix.yellow()) # center square
    matrix.drawRectangleFill(3,3, 4,4, matrix.white()) # center square
    matrix.pixelsShow()
    time.sleep(1)

    matrix.drawRectangleFill(3,1, 4,6, matrix.yellow()) # vertical
    matrix.drawRectangleFill(1,3, 6,4, matrix.yellow()) # horizontal
    matrix.drawRectangleFill(2,2, 5,5, matrix.yellow()) # center sauqre bigger
    matrix.drawRectangleFill(3,3, 4,4, matrix.white()) # center square
    matrix.pixelsShow()
    time.sleep(1)

    matrix.drawRectangleFill(3,0, 4,7, matrix.yellow()) # vertical
    matrix.drawRectangleFill(0,3, 7,4, matrix.yellow()) # horizontal
    matrix.drawRectangleFill(1,1, 6,6, matrix.yellow()) # center sauqre biggest
    matrix.drawRectangleFill(3,3, 4,4, matrix.white()) # center square
    matrix.pixelsShow()
    time.sleep(1)
    matrix.pixelsShow()
