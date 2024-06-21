import glowbit
import time

matrix = glowbit.matrix8x8()

speed = 0.2

while (True):
    matrix.pixelsFill(matrix.black())
    matrix.drawRectangleFill(3,3, 4,4, matrix.white()) # 1 center square
    matrix.pixelsShow()
    time.sleep(speed)

    matrix.drawRectangleFill(3,2, 4,5, matrix.white()) # 2 vertical
    matrix.drawRectangleFill(2,3, 5,4, matrix.white()) # 2 horizontal
    matrix.drawRectangleFill(3,3, 4,4, matrix.yellow()) # 1 center square
    matrix.pixelsShow()
    time.sleep(speed)

    matrix.drawRectangleFill(3,1, 4,6, matrix.white()) # 3 vertical
    matrix.drawRectangleFill(1,3, 6,4, matrix.white()) # 3 horizontal
    matrix.drawRectangleFill(2,2, 5,5, matrix.white()) # 3 center sauqre bigger
    matrix.drawRectangleFill(3,2, 4,5, matrix.yellow()) # 2 vertical
    matrix.drawRectangleFill(2,3, 5,4, matrix.yellow()) # 2 horizontal
    matrix.drawRectangleFill(3,3, 4,4, matrix.red()) # 1 center square
    matrix.pixelsShow()
    time.sleep(speed)

    matrix.drawRectangleFill(3,0, 4,7, matrix.white()) # 4 vertical
    matrix.drawRectangleFill(0,3, 7,4, matrix.white()) # 4 horizontal
    matrix.drawRectangleFill(1,1, 6,6, matrix.white()) # 4 center sauqre biggest
    matrix.drawRectangleFill(3,1, 4,6, matrix.yellow()) # 3 vertical
    matrix.drawRectangleFill(1,3, 6,4, matrix.yellow()) # 3 horizontal
    matrix.drawRectangleFill(2,2, 5,5, matrix.yellow()) # 3 center sauqre bigger
    matrix.drawRectangleFill(3,2, 4,5, matrix.red()) # 2 vertical
    matrix.drawRectangleFill(2,3, 5,4, matrix.red()) # 2 horizontal
    matrix.drawRectangleFill(3,3, 4,4, matrix.purple()) # 1 center square
    matrix.pixelsShow()
    time.sleep(speed)

    matrix.drawRectangleFill(0,0, 7,7, matrix.white()) # 5 center square
    matrix.drawRectangleFill(3,0, 4,7, matrix.yellow()) # 4 vertical
    matrix.drawRectangleFill(0,3, 7,4, matrix.yellow()) # 4 horizontal
    matrix.drawRectangleFill(1,1, 6,6, matrix.yellow()) # 4 center sauqre biggest
    matrix.drawRectangleFill(3,1, 4,6, matrix.red()) # 3 vertical
    matrix.drawRectangleFill(1,3, 6,4, matrix.red()) # 3 horizontal
    matrix.drawRectangleFill(2,2, 5,5, matrix.red()) # 3 center sauqre bigger
    matrix.drawRectangleFill(3,2, 4,5, matrix.purple()) # 2 vertical
    matrix.drawRectangleFill(2,3, 5,4, matrix.purple()) # 2 horizontal
    matrix.drawRectangleFill(3,3, 4,4, matrix.purple()) # 1 center square
    matrix.pixelsShow()
    time.sleep(speed)

    matrix.pixelsShow()
