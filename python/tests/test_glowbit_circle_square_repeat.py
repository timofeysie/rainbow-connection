import glowbit
import time
matrix = glowbit.matrix8x8()

while True:
    matrix.drawCircle(3, 3, 3, matrix.blue())
    matrix.pixelsShow()
    print("Circle drawn")
    time.sleep(1)
    matrix.pixelsFill(matrix.black())
    matrix.pixelsShow()
    print("Circle cleared")
    time.sleep(1)
    matrix.drawCircle(3, 3, 3, matrix.red())
    matrix.pixelsShow()
    print("Circle drawn")
    time.sleep(1)
    matrix.pixelsFill(matrix.black())
    matrix.pixelsShow()
    print("Circle cleared")
    time.sleep(1)