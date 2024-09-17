# Errors

It's always good to have a record of what went wrong and record the solution in case it happens again later after the solution can't be recalled.

## time data '24:00:00' does not match format '%H:%M:%S'

I was trying to just turn off the time condition to test the cameras night view.  When that didn't work, I hastily took a picture manually and went to sleep, expecting the script would run in the morning.  However, this was the error I saw when starting the script to see why there were no images:

```txt
Current Time: 08:39:01.395287
Traceback (most recent call last):
  File "/home/tim/python/capture_image.py", line 31, in <module>
    capture_image()  # Capture an image if the time is between 9 AM and 5 PM
  File "/home/tim/python/capture_image.py", line 15, in capture_image
    if current_time >= datetime.strptime("05:45:00", "%H:%M:%S").time() and current_time <= datetime.strptime("24:00:00", "%H:%M:%S").time():
  File "/usr/lib/python3.9/_strptime.py", line 568, in _strptime_datetime
    tt, fraction, gmtoff_fraction = _strptime(data_string, format)
  File "/usr/lib/python3.9/_strptime.py", line 349, in _strptime
    raise ValueError("time data %r does not match format %r" %
ValueError: time data '24:00:00' does not match format '%H:%M:%S'
```

For completeness, here is the whole script at the moment:

```py
import os
import picamera
from time import sleep
from datetime import datetime

# Function to capture an image and save it with a timestamp-based filename
def capture_image():
    # Get the current date and time
    current_time = datetime.now().time()

    # Log the current time (for debugging)
    print("Current Time:", current_time)

    # Check if the current time is between 9 AM and 5 PM
    if current_time >= datetime.strptime("05:45:00", "%H:%M:%S").time() and current_time <= datetime.strptime("24:00:00", "%H:%M:%S").time():
        # Define the image file path
        timestamp = datetime.now().strftime("%Y-%m-%d_%H-%M-%S")
        image_path = "/var/www/html/images/image_{}.jpg".format(timestamp)

        # Log the image path (for debugging)
        print("Image Path:", image_path)

        # Capture an image and save it
        os.system("libcamera-jpeg --output {}".format(image_path))
    else:
        # Add an 'else' block for actions to be taken when the condition is not met
        print("Outside of capture time range. No image captured.")

# Main program loop
while True:
    capture_image()  # Capture an image if the time is between 9 AM and 5 PM
    sleep(10)  # Wait for 60 seconds before checking the time again
```

Instead of "24:00:00" the correct format should be "23:59:59" for the end of the day.
