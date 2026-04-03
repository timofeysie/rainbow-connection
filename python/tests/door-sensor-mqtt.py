"""Door sensor (GP2 + GND) + WiFi + MQTT for Home Assistant.

Run on Raspberry Pi Pico W / Pico 2 W (MicroPython).

Prerequisites on the Raspberry Pi (Home Assistant host):
- Mosquitto MQTT broker (e.g. Home Assistant add-on "Mosquitto broker"), same LAN as the Pico.
- Settings - Devices & services - MQTT - Configure - Submit (broker URL usually matches the Pi).

On the Pico:
1. Copy secrets_door_example.py to secrets_door.py and fill WiFi + MQTT_HOST (Pi IP or hostname).
2. If ImportError: umqtt - run: mpremote mip install umqtt.simple
3. Deploy this file as main.py along with secrets_door.py.

Home Assistant - MQTT binary sensor (YAML or UI "MQTT" helper), example:

  mqtt:
    binary_sensor:
      - name: "Pico door test"
        unique_id: pico_door_pico
        state_topic: "home/door/pico/state"
        payload_on: "ON"
        payload_off: "OFF"
        device_class: door

Pin value: LOW = reed closed (magnet near), HIGH = open. MQTT: OFF = closed, ON = open.
"""

from machine import Pin, unique_id  # type: ignore[import-untyped]
import binascii
import network  # type: ignore[import-untyped]
import time

try:
    from umqtt.simple import MQTTClient  # type: ignore[import-untyped]
except ImportError as e:
    raise ImportError(
        "Install MQTT client: mpremote mip install umqtt.simple"
    ) from e

try:
    from secrets_door import (
        MQTT_HOST,
        MQTT_PASSWORD,
        MQTT_PORT,
        MQTT_USER,
        STATE_TOPIC,
        WIFI_PASSWORD,
        WIFI_SSID,
    )
except ImportError:
    raise ImportError(
        "Create secrets_door.py on the Pico (copy from secrets_door_example.py)."
    )

PIN = 2
DEBOUNCE_MS = 50
MQTT_KEEPALIVE_S = 60


def connect_wifi():
    wlan = network.WLAN(network.STA_IF)
    wlan.active(True)
    wlan.connect(WIFI_SSID, WIFI_PASSWORD)
    for _ in range(40):
        if wlan.status() < 0 or wlan.status() >= 3:
            break
        time.sleep_ms(250)
    if wlan.status() != 3:
        raise RuntimeError("WiFi failed, status=%s" % wlan.status())
    print("WiFi OK:", wlan.ifconfig()[0])
    return wlan


def make_client_id():
    return b"pico-door-" + binascii.hexlify(unique_id())


def connect_mqtt():
    cid = make_client_id()
    c = MQTTClient(
        cid,
        MQTT_HOST,
        port=MQTT_PORT,
        user=MQTT_USER,
        password=MQTT_PASSWORD,
        keepalive=MQTT_KEEPALIVE_S,
    )
    c.connect()
    print("MQTT OK, client_id=", cid.decode())
    return c


def door_payload(pin_value):
    # HIGH (1) = reed open -> ON; LOW (0) = closed -> OFF
    return "ON" if pin_value else "OFF"


def main():
    pin = Pin(PIN, Pin.IN, Pin.PULL_UP)
    last_value = None
    last_change_ms = 0
    wlan = connect_wifi()
    mqtt = connect_mqtt()

    def publish_state(raw):
        payload = door_payload(raw)
        mqtt.publish(STATE_TOPIC, payload, retain=True)
        print("MQTT", STATE_TOPIC, payload)

    # Initial state so HA sees something after subscribe
    publish_state(pin.value())
    last_ping_ms = time.ticks_ms()

    while True:
        if not wlan.isconnected():
            print("WiFi lost, reconnecting...")
            try:
                mqtt.disconnect()
            except OSError:
                pass
            wlan = connect_wifi()
            mqtt = connect_mqtt()
            publish_state(pin.value())
            last_ping_ms = time.ticks_ms()

        v = pin.value()
        now = time.ticks_ms()
        if v != last_value:
            if last_value is None or time.ticks_diff(now, last_change_ms) >= DEBOUNCE_MS:
                last_value = v
                last_change_ms = now
                try:
                    publish_state(v)
                except OSError as e:
                    print("MQTT publish error:", e)
                    try:
                        mqtt.disconnect()
                    except OSError:
                        pass
                    time.sleep_ms(500)
                    mqtt = connect_mqtt()
                    publish_state(v)

        try:
            mqtt.check_msg()
            if time.ticks_diff(time.ticks_ms(), last_ping_ms) >= (MQTT_KEEPALIVE_S * 500):
                ping = getattr(mqtt, "ping", None)
                if ping:
                    ping()
                last_ping_ms = time.ticks_ms()
        except OSError as e:
            print("MQTT check_msg:", e)
            try:
                mqtt.disconnect()
            except OSError:
                pass
            time.sleep_ms(500)
            mqtt = connect_mqtt()
            last_ping_ms = time.ticks_ms()

        time.sleep_ms(10)


if __name__ == "__main__":
    main()
