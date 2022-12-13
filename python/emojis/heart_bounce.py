import glowbit
import time
matrix = glowbit.matrix8x8()
def heart_bounce():
    print("4 heart")
    matrix.pixelsFill(matrix.black())
    T = [[0, 1, 1, 0, 0, 1, 1, 0],
         [1, 1, 1, 1, 1, 1, 1, 1],
         [1, 1, 1, 1, 1, 1, 1, 1],
         [1, 1, 1, 1, 1, 1, 1, 1],
         [0, 1, 1, 1, 1, 1, 1, 0],
         [0, 0, 1, 1, 1, 1, 0, 0],
         [0, 0, 0, 1, 1, 0, 0, 0],
         [0, 0, 0, 0, 0, 0, 0, 0]]
    row = 0
    col = 0
    for r in T:
        for c in r:
            color = matrix.black()
            if (c > 0):
                color = matrix.red()
            matrix.pixelSetXY(col, row, color)
            col += 1
            if (col > 7):
                col = 0
        row += 1
    matrix.pixelsShow()
    time.sleep(1)
    T = [[0, 0, 0, 0, 0, 0, 0, 0],
         [0, 1, 1, 0, 0, 1, 1, 0],
         [1, 1, 1, 1, 1, 1, 1, 1],
         [1, 1, 1, 1, 1, 1, 1, 1],
         [1, 1, 1, 1, 1, 1, 1, 1],
         [0, 1, 1, 1, 1, 1, 1, 0],
         [0, 0, 1, 1, 1, 1, 0, 0],
         [0, 0, 0, 1, 1, 0, 0, 0]]
    row = 0
    col = 0
    for r in T:
        for c in r:
            color = matrix.black()
            if (c > 0):
                color = matrix.red()
            matrix.pixelSetXY(col, row, color)
            col += 1
            if (col > 7):
                col = 0
        row += 1
    matrix.pixelsShow()
    time.sleep(1)
    T = [[0, 1, 1, 0, 0, 1, 1, 0],
         [1, 1, 1, 1, 1, 1, 1, 1],
         [1, 1, 1, 1, 1, 1, 1, 1],
         [1, 1, 1, 1, 1, 1, 1, 1],
         [0, 1, 1, 1, 1, 1, 1, 0],
         [0, 0, 1, 1, 1, 1, 0, 0],
         [0, 0, 0, 1, 1, 0, 0, 0],
         [0, 0, 0, 0, 0, 0, 0, 0]]
    row = 0
    col = 0
    for r in T:
        for c in r:
            color = matrix.black()
            if (c > 0):
                color = matrix.red()
            matrix.pixelSetXY(col, row, color)
            col += 1
            if (col > 7):
                col = 0
        row += 1
    matrix.pixelsShow()
    time.sleep(1)
