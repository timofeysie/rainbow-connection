# Emoji Landscape Picture Project

## The get_rgb_values utility

Currently you have to edit the name of the input image in the python\utils\rgb_values.py file.  I will add the filename as an argument when I have some more time.

When you run the script rgb_values.py it loads the image and creates a large_image = [ ... array data ... ] string and prints it out.  The array represents a long series of 8 pixel high rgb color sets for use on the glowbit 8x8 screen.  The auto-play version of the emoji badge code then scrolls the images.  This version is designed to go in a frame and be hung on a wall.  At least that's the initial idea of this project.

Next create a new file such as large_image.py and add the output from the rgb_values.py script after the required imports:

```py
import glowbit
matrix = glowbit.matrix8x8()

large_image = [
    [matrix.rgbColour(197, 207, 216), matrix.rgbColour(213, 223, 225), matrix.rgbColour(232, 237, 233), matrix.rgbColour(196, 207, 211), matrix.rgbColour(157, 176, 180), matrix.rgbColour(166, 186, 187), matrix.rgbColour(105, 118, 109), matrix.rgbColour(50, 55, 35), ],
    ...
]
```

Add a function to use it in the emojis.py file:

```py
from large_image import large_image

def scroll_large_image():
    transposed_image = list(map(list, zip(*large_image)))
    # Function to draw a section of the large image on the matrix
    def draw_section(section):
        print("Drawing section") # Debugging line
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
        print("Scrolling to row:", i) # Debugging line
        section = [row[i:i+8] for row in transposed_image]
        draw_section(section)
        time.sleep(0.6) # Add a delay of 0.1 seconds
```

Then use this function in the python\emoji-os-0-1-2-auto-play.py file:

```py
from emojis import *

matrix = glowbit.matrix8x8()
matrix.pixelsFill(matrix.black())

def draw_emoji():
    matrix = glowbit.matrix8x8(rateLimitCharactersPerSecond = 0.5)
    scroll_cloud_landscape()
```

Using three of these results in this error:

```txt
>>> %Run -c $EDITOR_CONTENT
Traceback (most recent call last):
  File "<stdin>", line 4, in <module>
  File "emojis.py", line 6, in <module>
MemoryError: memory allocation failed, allocating 136 bytes
```

I cut back on the amount of columns and at 132 loc (lines of code), the error goes away.
