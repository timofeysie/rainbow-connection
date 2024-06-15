from PiicoDev_RFID import PiicoDev_RFID
from PiicoDev_Unified import sleep_ms
from PiicoDev_SSD1306 import *
display = create_PiicoDev_SSD1306()

rfid = PiicoDev_RFID()   # Initialise the RFID module

print('Place tag near the PiicoDev RFID Module')
print(rfid)

while True:    
    if rfid.tagPresent():    # if an RFID tag is present
        id = rfid.readID()   # get the id
#        details = rfid.readID(detail=True) # gets more details eg. tag type
#{
# 'type': 'classic',
# 'id_formatted': '5B:6F:B8:08',
# 'success': True,
# 'id_integers': [91, 111, 184, 8]
#}
#        print(details)
        if (id == "5B:6F:B8:08"):
            display.fill(0)
            print("R12")
            display.text("R12", 0,0, 1)
        elif (id == "DB:93:B7:08"):
            display.fill(0)
            print("W3 - Clown")
            display.text("W3 - Clown", 0,0, 1)
        else:
            print(id)
            display.fill(0)
            display.text(id, 0,0, 1)
        display.show()
    sleep_ms(100)

