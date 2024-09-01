#        print(details)
from PiicoDev_RFID import PiicoDev_RFID
from PiicoDev_Unified import sleep_ms
from PiicoDev_SSD1306 import *

rfid = PiicoDev_RFID()   # Initialise the RFID module

print('Place tag near the PiicoDev RFID Module')
print(rfid)

while True:    
    if rfid.tagPresent():    # if an RFID tag is present
        id = rfid.readID()   # get the id
        if (id == "5B:6F:B8:08"):
            print("R12")
        elif (id == "DB:93:B7:08"):
            print("W3 - Clown")
        elif (id == "CB:61:B8:08"):
            print("9")
        else:
            print(id)
    sleep_ms(100)


