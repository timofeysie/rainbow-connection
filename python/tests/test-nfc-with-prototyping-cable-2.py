while True:
    try:
        result = rfid.readTagID()

        if result['success']:
            tag_id = result['id_formatted']

            if tag_id == "5B:6F:B8:08":
                print("R12 - Monkey")
            elif tag_id == "DB:93:B7:08":
                print("W3 - Clown")
            elif tag_id == "CB:61:B8:08":
                print("9")
            else:
                print(tag_id)

    except OSError as err:
        print("RFID I2C error:", err)
        sleep_ms(500)

    sleep_ms(100)