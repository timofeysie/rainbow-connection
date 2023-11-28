# for emoji os v0.1.4
import glowbit
import time
from large_image import large_image
matrix = glowbit.matrix8x8()

def scroll_large_image():
    transposed_image = list(map(list, zip(*large_image)))
    # Function to draw a section of the large image on the matrix
    def draw_section(section):
        matrix.pixelsFill(matrix.black())
        row = 0
        col = 0
        for r in section:
            for c in r:
                matrix.pixelSetXY(col, row, c)
                col += 1
                if (col > 7):
                    col = 0
            row += 1
        matrix.pixelsShow()

    # Scroll through the large image one row at a time
    for i in range(len(transposed_image[0]) - 7):
        print("row:", i) # Debugging line
        section = [row[i:i+8] for row in transposed_image]
        draw_section(section)
        time.sleep(0.6) # Add a delay of 0.1 seconds

def chakana():
    speed = 0.2
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

def regular():
    print("regular")
    matrix.pixelsFill(matrix.black())
    T = [[0, 0, 1, 1, 1, 1, 0, 0],
         [0, 1, 0, 0, 0, 0, 1, 0],
         [1, 0, 1, 0, 0, 1, 0, 1],
         [1, 0, 0, 0, 0, 0, 0, 1],
         [1, 0, 1, 1, 1, 1, 0, 1],
         [1, 0, 0, 0, 0, 0, 0, 1],
         [0, 1, 0, 0, 0, 0, 1, 0],
         [0, 0, 1, 1, 1, 1, 0, 0]]
    row = 0
    col = 0
    for r in T:
        for c in r:
            color = matrix.black()
            if (c > 0):
                color = matrix.white()
            matrix.pixelSetXY(col, row, color)
            col += 1
            if (col > 7):
                col = 0
        row += 1
    matrix.pixelsShow()
def sad():
    print("sad")
    T = [[0, 0, 1, 1, 1, 1, 0, 0],
            [0, 1, 0, 0, 0, 0, 1, 0],
            [1, 0, 1, 0, 0, 1, 0, 1],
            [1, 0, 0, 0, 0, 0, 0, 1],
            [1, 0, 0, 1, 1, 0, 0, 1],
            [1, 0, 1, 0, 0, 1, 0, 1],
            [0, 1, 0, 0, 0, 0, 1, 0],
            [0, 0, 1, 1, 1, 1, 0, 0]]
    row = 0
    col = 0
    for r in T:
        for c in r:
            color = matrix.black()
            if (c > 0):
                color = matrix.white()
            matrix.pixelSetXY(col, row, color)
            col += 1
            if (col > 7):
                col = 0
        row += 1
    matrix.pixelsShow()
def happy():
    matrix.pixelsFill(matrix.black())
    T = [[0, 0, 1, 1, 1, 1, 0, 0],
         [0, 1, 0, 0, 0, 0, 1, 0],
         [1, 0, 1, 0, 0, 1, 0, 1],
         [1, 0, 0, 0, 0, 0, 0, 1],
         [1, 0, 1, 0, 0, 1, 0, 1],
         [1, 0, 0, 1, 1, 0, 0, 1],
         [0, 1, 0, 0, 0, 0, 1, 0],
         [0, 0, 1, 1, 1, 1, 0, 0]]
    row = 0
    col = 0
    for r in T:
        for c in r:
            color = matrix.black()
            if (c > 0):
                color = matrix.white()
            matrix.pixelSetXY(col, row, color)
            col += 1
            if (col > 7):
                col = 0
        row += 1
    matrix.pixelsShow()
def thickLips():
    matrix.pixelsFill(matrix.black())
    T = [[0, 0, 1, 1, 1, 1, 0, 0],
         [0, 1, 0, 0, 0, 0, 1, 0],
         [1, 0, 1, 0, 0, 1, 0, 1],
         [1, 0, 0, 0, 0, 0, 0, 1],
         [1, 0, 1, 1, 1, 1, 0, 1],
         [1, 0, 1, 1, 1, 1, 0, 1],
         [0, 1, 0, 0, 0, 0, 1, 0],
         [0, 0, 1, 1, 1, 1, 0, 0]]
    row = 0
    col = 0
    for r in T:
        for c in r:
            color = matrix.black()
            if (c > 0):
                color = matrix.white()
            matrix.pixelSetXY(col, row, color)
            col += 1
            if (col > 7):
                col = 0
        row += 1
    matrix.pixelsShow()
def wry():
    print("wry")
    matrix.pixelsFill(matrix.black())
    T = [[0, 0, 1, 1, 1, 1, 0, 0],
         [0, 1, 0, 0, 0, 0, 1, 0],
         [1, 0, 1, 0, 1, 0, 0, 1],
         [1, 0, 1, 0, 1, 0, 0, 1],
         [1, 0, 0, 0, 0, 1, 0, 1],
         [1, 0, 1, 1, 1, 0, 0, 1],
         [0, 1, 0, 0, 0, 0, 1, 0],
         [0, 0, 1, 1, 1, 1, 0, 0]]
    row = 0
    col = 0
    for r in T:
        for c in r:
            color = matrix.black()
            if (c > 0):
                color = matrix.white()
            matrix.pixelSetXY(col, row, color)
            col += 1
            if (col > 7):
                col = 0
        row += 1
    matrix.pixelsShow()
def heartBounce():
    print("heart bounce")
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
def finn():
    print("finn the human")
    matrix.pixelsFill(matrix.black())
    T = [[matrix.rgbColour(64,196,254), matrix.rgbColour(64,196,254), matrix.rgbColour(255,255,255), matrix.rgbColour(64,196,254), matrix.rgbColour(64,196,254), matrix.rgbColour(64,196,254), matrix.rgbColour(255,255,255), matrix.rgbColour(64,196,254)],
            [matrix.rgbColour(64,196,254), matrix.rgbColour(64,196,254), matrix.rgbColour(255,255,255), matrix.rgbColour(255,255,255), matrix.rgbColour(255,255,255), matrix.rgbColour(255,255,255), matrix.rgbColour(255,255,255), matrix.rgbColour(64,196,254)],
            [matrix.rgbColour(64,196,254), matrix.rgbColour(64,196,254), matrix.rgbColour(255,255,255), matrix.rgbColour(0,0,0), matrix.rgbColour(250,220,100), matrix.rgbColour(250,220,100), matrix.rgbColour(0,0,0), matrix.rgbColour(64,196,254)],
            [matrix.rgbColour(134,188,70), matrix.rgbColour(121,173,65), matrix.rgbColour(255,255,255), matrix.rgbColour(250,220,100), matrix.rgbColour(250,220,100), matrix.rgbColour(250,220,100), matrix.rgbColour(250,220,100), matrix.rgbColour(64,196,254)],
            [matrix.rgbColour(24,88,28), matrix.rgbColour(164,199,122), matrix.rgbColour(121,197,233), matrix.rgbColour(31,140,226), matrix.rgbColour(31,140,226), matrix.rgbColour(31,140,226), matrix.rgbColour(31,140,226), matrix.rgbColour(64,196,254)],
            [matrix.rgbColour(250,220,100), matrix.rgbColour(24,88,28), matrix.rgbColour(31,140,226), matrix.rgbColour(31,140,226), matrix.rgbColour(31,140,226), matrix.rgbColour(31,140,226), matrix.rgbColour(31,140,226), matrix.rgbColour(250,220,100)],
            [matrix.rgbColour(100,216,2), matrix.rgbColour(100,216,2), matrix.rgbColour(11,61,138), matrix.rgbColour(11,61,138), matrix.rgbColour(11,61,138), matrix.rgbColour(11,61,138), matrix.rgbColour(11,61,138), matrix.rgbColour(100,216,2)],
            [matrix.rgbColour(100,216,2), matrix.rgbColour(100,216,2), matrix.rgbColour(250,220,100), matrix.rgbColour(100,216,2), matrix.rgbColour(100,216,2), matrix.rgbColour(100,216,2), matrix.rgbColour(250,220,100), matrix.rgbColour(100,216,2)]]
    row = 0
    col = 0
    for r in T:
        for c in r:
            color = matrix.black()
            matrix.pixelSetXY(col, row, c)
            col += 1
            if (col > 7):
                col = 0
        row += 1
    matrix.pixelsShow()
    time.sleep(0.5)
def angry():
    print("angry")
    matrix.pixelsFill(matrix.black())
    T = [[matrix.rgbColour(255,0,0),    matrix.rgbColour(0,0,0),      matrix.rgbColour(255,0,0),     matrix.rgbColour(255,0,0), matrix.rgbColour(255,0,0), matrix.rgbColour(255,0,0),     matrix.rgbColour(0,0,0),       matrix.rgbColour(255,0,0)],
            [matrix.rgbColour(255,0,0), matrix.rgbColour(255,0,0),    matrix.rgbColour(0,0,0),       matrix.rgbColour(255,0,0), matrix.rgbColour(255,0,0), matrix.rgbColour(0,0,0),       matrix.rgbColour(255,0,0),     matrix.rgbColour(255,0,0)],
            [matrix.rgbColour(255,0,0), matrix.rgbColour(64,196,254), matrix.rgbColour(255,255,255), matrix.rgbColour(0,0,0),   matrix.rgbColour(0,0,0),   matrix.rgbColour(64,196,253),  matrix.rgbColour(255,255,255), matrix.rgbColour(255,0,0)],
            [matrix.rgbColour(255,0,0), matrix.rgbColour(255,0,0),    matrix.rgbColour(255,0,0),     matrix.rgbColour(255,0,0), matrix.rgbColour(255,0,0), matrix.rgbColour(255,0,0),     matrix.rgbColour(255,0,0),     matrix.rgbColour(255,0,0)],
            [matrix.rgbColour(255,0,0), matrix.rgbColour(255,0,0),    matrix.rgbColour(255,0,0),     matrix.rgbColour(255,0,0), matrix.rgbColour(255,0,0), matrix.rgbColour(255,0,0),     matrix.rgbColour(255,0,0),     matrix.rgbColour(255,0,0)],
            [matrix.rgbColour(255,0,0), matrix.rgbColour(255,0,0),    matrix.rgbColour(0,0,0),       matrix.rgbColour(0,0,0),   matrix.rgbColour(0,0,0),   matrix.rgbColour(0,0,0),       matrix.rgbColour(255,0,0),     matrix.rgbColour(255,0,0)],
            [matrix.rgbColour(255,0,0), matrix.rgbColour(0,0,0),      matrix.rgbColour(255,0,0),     matrix.rgbColour(255,0,0), matrix.rgbColour(255,0,0), matrix.rgbColour(255,0,0),     matrix.rgbColour(0,0,0),       matrix.rgbColour(255,0,0)],
            [matrix.rgbColour(255,0,0), matrix.rgbColour(255,0,0),    matrix.rgbColour(255,0,0),     matrix.rgbColour(255,0,0), matrix.rgbColour(255,0,0), matrix.rgbColour(255,0,0),     matrix.rgbColour(255,0,0),     matrix.rgbColour(255,0,0)]]
    row = 0
    col = 0
    for r in T:
        for c in r:
            color = matrix.black()
            matrix.pixelSetXY(col, row, c)
            col += 1
            if (col > 7):
                col = 0
        row += 1
    matrix.pixelsShow()
def greenMonster():
    print("green monster")
    matrix.pixelsFill(matrix.black())
    T = [[matrix.rgbColour(0,0,0),      matrix.rgbColour(0,255,0),     matrix.rgbColour(0,255,0),       matrix.rgbColour(0,255,0),     matrix.rgbColour(0,255,0),     matrix.rgbColour(0,255,0),     matrix.rgbColour(0,255,0),       matrix.rgbColour(0,0,0)],
            [matrix.rgbColour(0,255,0), matrix.rgbColour(0,255,0),     matrix.rgbColour(0,255,0),       matrix.rgbColour(0,255,0),     matrix.rgbColour(0,255,0),     matrix.rgbColour(0,255,0),       matrix.rgbColour(0,255,0),     matrix.rgbColour(0,255,0)],
            [matrix.rgbColour(0,255,0), matrix.rgbColour(255,0,0),     matrix.rgbColour(0,255,0),       matrix.rgbColour(0,255,0),     matrix.rgbColour(255,0,0),     matrix.rgbColour(0,255,0),  matrix.rgbColour(0,255,0), matrix.rgbColour(0,255,0)],
            [matrix.rgbColour(0,255,0), matrix.rgbColour(0,255,0),     matrix.rgbColour(0,255,0),       matrix.rgbColour(0,255,0),     matrix.rgbColour(0,255,0),     matrix.rgbColour(0,255,0),     matrix.rgbColour(0,255,0),     matrix.rgbColour(0,255,0)],
            [matrix.rgbColour(0,255,0), matrix.rgbColour(0,255,0),     matrix.rgbColour(255,255,255),   matrix.rgbColour(0,0,0),       matrix.rgbColour(255,255,255), matrix.rgbColour(0,0,0),     matrix.rgbColour(255,255,255),     matrix.rgbColour(0,255,0)],
            [matrix.rgbColour(0,255,0), matrix.rgbColour(0,0,0),       matrix.rgbColour(0,0,0),         matrix.rgbColour(0,0,0),       matrix.rgbColour(0,0,0),       matrix.rgbColour(0,0,0),       matrix.rgbColour(0,0,0),     matrix.rgbColour(0,255,0)],
            [matrix.rgbColour(0,255,0), matrix.rgbColour(255,255,255), matrix.rgbColour(0,0,0),         matrix.rgbColour(255,255,255), matrix.rgbColour(0,0,0),       matrix.rgbColour(255,255,255),     matrix.rgbColour(0,0,0),       matrix.rgbColour(0,255,0)],
            [matrix.rgbColour(0,255,0), matrix.rgbColour(0,255,0),     matrix.rgbColour(0,255,0),       matrix.rgbColour(0,255,0),     matrix.rgbColour(0,255,0),     matrix.rgbColour(0,255,0),     matrix.rgbColour(0,255,0),     matrix.rgbColour(0,255,0)]]
    row = 0
    col = 0
    for r in T:
        for c in r:
            color = matrix.black()
            matrix.pixelSetXY(col, row, c)
            col += 1
            if (col > 7):
                col = 0
        row += 1
    matrix.pixelsShow()
def pikachu():
    print("7. pikachu")
    matrix.pixelsFill(matrix.black())
    T = [[matrix.rgbColour(255,255,255), matrix.rgbColour(66, 66, 66), matrix.rgbColour(66,66,66), matrix.rgbColour(255,255,255), matrix.rgbColour(255,255,255), matrix.rgbColour(255,255,255), matrix.rgbColour(255,255,255), matrix.rgbColour(64,66,66)],
            [matrix.rgbColour(255,255,255), matrix.rgbColour(255,255,255), matrix.rgbColour(255,236,60), matrix.rgbColour(255,152,0), matrix.rgbColour(255,255,255), matrix.rgbColour(255,255,255), matrix.rgbColour(255,255,255), matrix.rgbColour(255,152,0)],
            [matrix.rgbColour(255,255,255), matrix.rgbColour(255,255,255), matrix.rgbColour(255,255,255), matrix.rgbColour(255,236,60), matrix.rgbColour(255,236,60), matrix.rgbColour(250,220,100), matrix.rgbColour(255,236,60), matrix.rgbColour(255,152,0)],
            [matrix.rgbColour(255,152,0), matrix.rgbColour(255,152,0), matrix.rgbColour(255,255,255), matrix.rgbColour(250,220,100), matrix.rgbColour(0,0,0), matrix.rgbColour(250,220,100), matrix.rgbColour(250,220,100), matrix.rgbColour(0,0,0)],
            [matrix.rgbColour(255,152,0), matrix.rgbColour(255,152,0), matrix.rgbColour(255,255,255), matrix.rgbColour(234,30,4), matrix.rgbColour(254,241,0), matrix.rgbColour(254,241,0), matrix.rgbColour(254,241,0), matrix.rgbColour(255,152,0)],
            [matrix.rgbColour(255,255,255), matrix.rgbColour(162,89,0), matrix.rgbColour(255,255,255), matrix.rgbColour(254,241,0), matrix.rgbColour(230,137,0), matrix.rgbColour(254,241,0), matrix.rgbColour(255,152,0), matrix.rgbColour(255,255,255)],
            [matrix.rgbColour(255,255,255), matrix.rgbColour(176,97,0), matrix.rgbColour(250,238,0), matrix.rgbColour(255,152,0), matrix.rgbColour(251,238,0), matrix.rgbColour(162,89,0), matrix.rgbColour(251,238,0), matrix.rgbColour(255,255,255)],
            [matrix.rgbColour(255,255,255), matrix.rgbColour(255,255,255), matrix.rgbColour(250,238,0), matrix.rgbColour(210,123,0), matrix.rgbColour(162,89,0), matrix.rgbColour(177,98,0), matrix.rgbColour(177,98,0), matrix.rgbColour(255,255,255)]]
    row = 0
    col = 0
    for r in T:
        for c in r:
            color = matrix.black()
            matrix.pixelSetXY(col, row, c)
            col += 1
            if (col > 7):
                col = 0
        row += 1
    matrix.pixelsShow()

def crab():
    print("crab")
    matrix.pixelsFill(matrix.black())
    T = [[   matrix.rgbColour(0,0,0),   matrix.rgbColour(255,255,255), matrix.rgbColour(255,255,255), matrix.rgbColour(0,0,0),   matrix.rgbColour(255,255,255), matrix.rgbColour(255,255,255), matrix.rgbColour(0,0,0),    matrix.rgbColour(0,0,0)],
            [matrix.rgbColour(0,0,0),   matrix.rgbColour(255,255,255), matrix.rgbColour(0,0,255),     matrix.rgbColour(0,0,0),   matrix.rgbColour(255,255,255), matrix.rgbColour(0,0,255),     matrix.rgbColour(0,0,0),    matrix.rgbColour(0,0,0)],
            [matrix.rgbColour(0,0,0),   matrix.rgbColour(255,0,0),     matrix.rgbColour(0,0,0),       matrix.rgbColour(0,0,0),   matrix.rgbColour(255,0,0),     matrix.rgbColour(0,0,0),       matrix.rgbColour(0,0,0),    matrix.rgbColour(0,0,0)],
            [matrix.rgbColour(0,0,0),   matrix.rgbColour(255,0,0),     matrix.rgbColour(0,0,0),       matrix.rgbColour(0,0,0),   matrix.rgbColour(255,0,0),     matrix.rgbColour(0,0,0),       matrix.rgbColour(0,0,0),    matrix.rgbColour(0,0,0)],
            [matrix.rgbColour(255,0,0), matrix.rgbColour(255,0,0),     matrix.rgbColour(255,0,0),     matrix.rgbColour(255,0,0), matrix.rgbColour(255,0,0),     matrix.rgbColour(0,0,0),       matrix.rgbColour(255,0,0),  matrix.rgbColour(255,0,0)],
            [matrix.rgbColour(255,0,0), matrix.rgbColour(255,0,0),     matrix.rgbColour(0,0,0),       matrix.rgbColour(0,0,0),   matrix.rgbColour(255,0,0),     matrix.rgbColour(255,0,0),     matrix.rgbColour(255,0,0),  matrix.rgbColour(0,0,0)],
            [matrix.rgbColour(255,0,0), matrix.rgbColour(255,0,0),     matrix.rgbColour(255,0,0),     matrix.rgbColour(255,0,0), matrix.rgbColour(255,0,0),     matrix.rgbColour(0,0,0),       matrix.rgbColour(0,0,0),    matrix.rgbColour(255,0,0)],
            [matrix.rgbColour(255,0,0), matrix.rgbColour(0,0,0),       matrix.rgbColour(255,0,0),     matrix.rgbColour(0,0,0),   matrix.rgbColour(255,0,0),     matrix.rgbColour(0,0,0),       matrix.rgbColour(0,0,0),    matrix.rgbColour(0,0,0)]]
    row = 0
    col = 0
    for r in T:
        for c in r:
            color = matrix.black()
            matrix.pixelSetXY(col, row, c)
            col += 1
            if (col > 7):
                col = 0
        row += 1
    matrix.pixelsShow()

def frog():
    print("frog")
    matrix.pixelsFill(matrix.black())
    T = [[matrix.rgbColour(0,0,0),   matrix.rgbColour(0,255,0),     matrix.rgbColour(0,255,0),     matrix.rgbColour(0,255,0),   matrix.rgbColour(0,255,0),     matrix.rgbColour(0,255,0),    matrix.rgbColour(0,255,0),   matrix.rgbColour(0,255,0)],
         [matrix.rgbColour(0,0,0),   matrix.rgbColour(0,255,0),     matrix.rgbColour(0,0,0),       matrix.rgbColour(0,255,0),   matrix.rgbColour(0,255,0),     matrix.rgbColour(0,255,0),    matrix.rgbColour(0,0,0),     matrix.rgbColour(0,255,0)],
         [matrix.rgbColour(0,255,0), matrix.rgbColour(0,255,0),     matrix.rgbColour(0,255,0),     matrix.rgbColour(0,255,0),   matrix.rgbColour(0,255,0),     matrix.rgbColour(0,255,0),    matrix.rgbColour(0,255,0),   matrix.rgbColour(0,255,0)],
         [matrix.rgbColour(0,255,0), matrix.rgbColour(0,0,0),       matrix.rgbColour(0,0,0),       matrix.rgbColour(0,0,0),     matrix.rgbColour(0,0,0),       matrix.rgbColour(0,0,0),      matrix.rgbColour(0,0,0),     matrix.rgbColour(0,0,0)],
         [matrix.rgbColour(0,255,0), matrix.rgbColour(0,255,0),     matrix.rgbColour(0,255,0),     matrix.rgbColour(0,255,0),   matrix.rgbColour(0,255,0),     matrix.rgbColour(0,255,0),    matrix.rgbColour(0,255,0),   matrix.rgbColour(0,255,0)],
         [matrix.rgbColour(0,255,0), matrix.rgbColour(0,255,0),     matrix.rgbColour(0,255,0),     matrix.rgbColour(0,255,0),   matrix.rgbColour(0,255,0),     matrix.rgbColour(0,255,0),    matrix.rgbColour(0,255,0),   matrix.rgbColour(0,255,0)],
         [matrix.rgbColour(0,255,0), matrix.rgbColour(0,255,0),     matrix.rgbColour(0,255,0),     matrix.rgbColour(0,255,0),   matrix.rgbColour(0,255,0),     matrix.rgbColour(0,255,0),     matrix.rgbColour(0,255,0),  matrix.rgbColour(0,255,0)],
         [matrix.rgbColour(0,255,0), matrix.rgbColour(0,255,0),     matrix.rgbColour(0,0,0),       matrix.rgbColour(0,255,0),   matrix.rgbColour(0,255,0),     matrix.rgbColour(0,255,0),     matrix.rgbColour(0,0,0),    matrix.rgbColour(0,255,0)]]
    row = 0
    col = 0
    for r in T:
        for c in r:
            color = matrix.black()
            matrix.pixelSetXY(col, row, c)
            col += 1
            if (col > 7):
                col = 0
        row += 1
    matrix.pixelsShow()

def bald():
    print("bald")
    matrix.pixelsFill(matrix.black())
    T = [[matrix.rgbColour(0,0,0),    matrix.rgbColour(68,59,49),    matrix.rgbColour(68,59,49),    matrix.rgbColour(68,59,49),  matrix.rgbColour(68,59,49),    matrix.rgbColour(68,59,49),    matrix.rgbColour(68,59,49),   matrix.rgbColour(0,0,0)],
         [matrix.rgbColour(68,59,49), matrix.rgbColour(68,59,49),    matrix.rgbColour(68,59,49),    matrix.rgbColour(68,59,49),   matrix.rgbColour(68,59,49),     matrix.rgbColour(68,59,49),    matrix.rgbColour(68,59,49),     matrix.rgbColour(68,59,49)],
         [matrix.rgbColour(68,59,49), matrix.rgbColour(68,59,49),    matrix.rgbColour(68,59,49),    matrix.rgbColour(68,59,49),   matrix.rgbColour(68,59,49),     matrix.rgbColour(68,59,49),    matrix.rgbColour(68,59,49),   matrix.rgbColour(68,59,49)],
         [matrix.rgbColour(68,59,49), matrix.rgbColour(68,59,49),    matrix.rgbColour(68,59,49),    matrix.rgbColour(68,59,49),     matrix.rgbColour(68,59,49),       matrix.rgbColour(68,59,49),      matrix.rgbColour(68,59,49),     matrix.rgbColour(68,59,49)],
         [matrix.rgbColour(68,59,49), matrix.rgbColour(68,59,49),    matrix.rgbColour(68,59,49),    matrix.rgbColour(68,59,49),   matrix.rgbColour(68,59,49),     matrix.rgbColour(68,59,49),    matrix.rgbColour(68,59,49),   matrix.rgbColour(68,59,49)],
         [matrix.rgbColour(100,100,100),    matrix.rgbColour(68,59,49),    matrix.rgbColour(68,59,49),    matrix.rgbColour(68,59,49),   matrix.rgbColour(100,100,100),       matrix.rgbColour(68,59,49),    matrix.rgbColour(68,59,49),   matrix.rgbColour(68,59,49)],
         [matrix.rgbColour(68,59,49), matrix.rgbColour(68,59,49),    matrix.rgbColour(68,59,49),    matrix.rgbColour(68,59,49),   matrix.rgbColour(68,59,49),     matrix.rgbColour(68,59,49),     matrix.rgbColour(68,59,49),  matrix.rgbColour(68,59,49)],
         [matrix.rgbColour(68,59,49), matrix.rgbColour(0,0,0),       matrix.rgbColour(0,0,0),       matrix.rgbColour(0,0,0),      matrix.rgbColour(68,59,49),     matrix.rgbColour(68,59,49),     matrix.rgbColour(68,59,49),    matrix.rgbColour(0,0,0)]]
    row = 0
    col = 0
    for r in T:
        for c in r:
            color = matrix.black()
            matrix.pixelSetXY(col, row, c)
            col += 1
            if (col > 7):
                col = 0
        row += 1
    matrix.pixelsShow()

def surprise():
    print("surprise")
    matrix.pixelsFill(matrix.black())
    T = [[matrix.rgbColour(150,70,0), matrix.rgbColour(150,70,0),    matrix.rgbColour(150,70,0),    matrix.rgbColour(150,70,0),  matrix.rgbColour(150,70,0),    matrix.rgbColour(150,70,0),    matrix.rgbColour(150,70,0),   matrix.rgbColour(150,70,0)],
         [matrix.rgbColour(68,59,49), matrix.rgbColour(68,59,49),    matrix.rgbColour(68,59,49),    matrix.rgbColour(68,59,49),   matrix.rgbColour(68,59,49),     matrix.rgbColour(68,59,49),    matrix.rgbColour(68,59,49),     matrix.rgbColour(150,70,0)],
         [matrix.rgbColour(68,59,49), matrix.rgbColour(0,0,0),       matrix.rgbColour(100,100,100),    matrix.rgbColour(68,59,49),   matrix.rgbColour(0,0,0),     matrix.rgbColour(100,100,100),    matrix.rgbColour(68,59,49),   matrix.rgbColour(150,70,0)],
         [matrix.rgbColour(68,59,49), matrix.rgbColour(100,100,100), matrix.rgbColour(100,100,100),    matrix.rgbColour(68,59,49),     matrix.rgbColour(100,100,100),       matrix.rgbColour(100,100,100),      matrix.rgbColour(68,59,49),     matrix.rgbColour(150,70,0)],
         [matrix.rgbColour(68,59,49), matrix.rgbColour(68,59,49),    matrix.rgbColour(68,59,49),    matrix.rgbColour(68,59,49),   matrix.rgbColour(68,59,49),     matrix.rgbColour(68,59,49),    matrix.rgbColour(68,59,49),   matrix.rgbColour(68,59,49)],
         [matrix.rgbColour(68,59,49),    matrix.rgbColour(68,59,49),    matrix.rgbColour(0,0,0),    matrix.rgbColour(0,0,0),   matrix.rgbColour(68,59,49),       matrix.rgbColour(68,59,49),    matrix.rgbColour(68,59,49),   matrix.rgbColour(68,59,49)],
         [matrix.rgbColour(68,59,49), matrix.rgbColour(68,59,49),    matrix.rgbColour(0,0,0),    matrix.rgbColour(0,0,0),   matrix.rgbColour(68,59,49),     matrix.rgbColour(68,59,49),     matrix.rgbColour(68,59,49),  matrix.rgbColour(150,70,0)],
         [matrix.rgbColour(0,0,0),    matrix.rgbColour(68,59,49),    matrix.rgbColour(68,59,49),       matrix.rgbColour(68,59,49),      matrix.rgbColour(68,59,49),     matrix.rgbColour(68,59,49),     matrix.rgbColour(68,59,49),    matrix.rgbColour(0,0,0)]]
    row = 0
    col = 0
    for r in T:
        for c in r:
            color = matrix.black()
            matrix.pixelSetXY(col, row, c)
            col += 1
            if (col > 7):
                col = 0
        row += 1
    matrix.pixelsShow()
