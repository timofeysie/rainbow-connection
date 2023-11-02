from PIL import Image

def get_rgb_values(image_path):
    img = Image.open(image_path)
    img_rgb = img.convert('RGB')
    width, height = img.size

    # Create a list to hold the pixel data
    pixel_data = []

    # Loop through each pixel in the image
    for x in range(width):
        column = []
        for y in range(height):
            # Get the RGB values of the pixel
            r, g, b = img_rgb.getpixel((x, y))
            # Append the RGB values to the column list
            column.append((r, g, b))
        # Append the column to the pixel_data list
        pixel_data.append(column)

    return pixel_data

# Use the function to get the RGB values from an image
rgb_values = get_rgb_values('large-image-3.jpg')

# Print out the RGB values in a format that can be used in MicroPython
print("large_image = [")
for column in rgb_values:
    print("    [", end="")
    for rgb in column:
        print("matrix.rgbColour" + str(rgb) + ",", end=" ")
    print("],")
print("]")