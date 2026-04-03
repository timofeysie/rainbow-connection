# Home Assistant

## Door Switch Sensor

I have a Door Switch Sensor (Normally Open) which I want to use with a raspberry pi pico 2 w.
Then I want to connect the pico to the home assistant server and use the sensor to trigger a automation.

The door sensor product details are:

Around 10mm of detection range, though you could use a different (stronger) magnet to increase the range.

The sensor contains a reed switch, a magnetic field shorts the two wires. Use a falling edge interrupt to detect an open.

Use the mounting holes or double-sided adhesive tape to secure it.

Screws: 4Gx12mm.

Specifications:

- Maximum current: 100 mA
- Sensor size: 30 x 16 x 10 mm
- Cable Length: 280 mm

## MQTT setup for Pico door sensor

Use these steps after installing the Mosquitto broker add-on in Home Assistant.

### 1. Start Mosquitto add-on

- In Home Assistant, go to `Settings` -> `Apps` -> `Mosquitto broker`.
- Click `Start`.
- Turn on `Start on boot`.
- Optional but useful during setup: turn on `Watchdog`.
- Open `Log` and confirm the broker is running without auth errors.

### 2. Create MQTT user credentials

- In Home Assistant, go to `Settings` -> `People` -> `Users`.
- Create a dedicated user for the Pico (for example `pico-door`).
- Set a strong password and keep it for the Pico secrets file.

### 3. Configure MQTT integration in Home Assistant

- Go to `Settings` -> `Devices & services`.
- Add integration: `MQTT` (if not already present).
- Use broker host `127.0.0.1` if Mosquitto runs as the add-on on the same HA host.
- Use port `1883`.
- Enter the MQTT username and password created above.
- Submit and verify integration is connected.

### 4. Configure Pico secrets

Update the Pico `secrets_door.py` values to match your network and broker:

- `WIFI_SSID` and `WIFI_PASSWORD`: Wi-Fi used by the Pico.
- `MQTT_HOST`: Home Assistant IP, for example `192.168.68.58`.
- `MQTT_PORT`: `1883`.
- `MQTT_USER` and `MQTT_PASSWORD`: the MQTT user created in HA.
- `STATE_TOPIC`: for example `home/door/pico/state`.

### 5. Validate broker from Home Assistant

- In Home Assistant, go to `Developer Tools` -> `MQTT` -> `Listen to a topic`.
- Listen on `home/door/pico/state`.
- Run `python/tests/door-sensor-mqtt.py` on the Pico.
- Move the magnet and confirm `ON` and `OFF` payloads appear.

### 6. Expected troubleshooting outcomes

- `OSError: [Errno 104] ECONNRESET` on Pico usually means broker reachable but connection rejected (wrong user/password or broker not started).
- `status=-3` during Wi-Fi connect means wrong Wi-Fi password.
- `status=-2` during Wi-Fi connect means AP not found from Pico (SSID/band/coverage issue).
