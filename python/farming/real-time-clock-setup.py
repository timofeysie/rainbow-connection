# PiicoDev Real Time Clock RV-3028
# An example of how to set and read the date, time, and weekday

from PiicoDev_RV3028 import PiicoDev_RV3028
from PiicoDev_Unified import sleep_ms

rtc = PiicoDev_RV3028() # Initialise the RTC module, enable charging

# Set the time by assigning values to rtc's attributes
# Replace the following values with the current date/time
rtc.day = 2
rtc.month = 3
rtc.year = 2026
rtc.hour = 18
rtc.minute = 0
rtc.second = 0
rtc.ampm = '24' # 'AM','PM' or '24'. Defaults to 24-hr time
rtc.weekday = 1 # Rolls over at midnight; 0=Monday. March 2 2026 is Tuesday
rtc.setDateTime() # Sets the time with the above values

# Get the current time
rtc.getDateTime()

# Print the current time, and today's name
# You can read from individual time attributes eg hour, minute, weekday.
print("The time is " + str(rtc.hour) + ":" + str(rtc.minute))
print("Today is " + str(rtc.weekdayName) + "\n") # weekdayName assumes counting from 0=Monday. 

while True:
    print(rtc.timestamp()) # timestamp() automatically updates time, and returns a pre-formatted string. Useful for printing and datalogging!
    sleep_ms(1000)