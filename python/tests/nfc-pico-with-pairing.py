# nfc-pico-with-pairing.py
# Runs on the Raspberry Pi Pico 2 W (MicroPython).
# Reads NFC tags via the PiicoDev RFID module and sends the tag UID over BLE
# using the same PAIR:<name> / PAIR_OK handshake as emoji-os-pico-*.py.
# The paired Zero script (nfc-zero-with-pairing.py) listens for TAG:<uid>
# notifications and prints them.

# === Pairing ===
# Override by placing a pair_config.py next to this file containing e.g.
# PAIR_NAME = "living-room"
try:
    from pair_config import PAIR_NAME  # type: ignore  # noqa: F401
except Exception:
    PAIR_NAME = "default"

from machine import Pin
import time
import bluetooth
from ble_advertising import advertising_payload
from micropython import const
from PiicoDev_RFID import PiicoDev_RFID
from PiicoDev_Unified import sleep_ms

# === BLE Constants ===
_IRQ_CENTRAL_CONNECT = const(1)
_IRQ_CENTRAL_DISCONNECT = const(2)
_IRQ_GATTS_WRITE = const(3)

_FLAG_READ = const(0x0002)
_FLAG_WRITE_NO_RESPONSE = const(0x0004)
_FLAG_WRITE = const(0x0008)
_FLAG_NOTIFY = const(0x0010)

_ADV_TYPE_COMPLETE_NAME = const(0x09)

# Nordic UART Service UUIDs
_UART_UUID = bluetooth.UUID("6E400001-B5A3-F393-E0A9-E50E24DCCA9E")
_UART_TX = (
    bluetooth.UUID("6E400003-B5A3-F393-E0A9-E50E24DCCA9E"),
    _FLAG_READ | _FLAG_NOTIFY,
)
_UART_RX = (
    bluetooth.UUID("6E400002-B5A3-F393-E0A9-E50E24DCCA9E"),
    _FLAG_WRITE | _FLAG_WRITE_NO_RESPONSE,
)
_UART_SERVICE = (
    _UART_UUID,
    (_UART_TX, _UART_RX),
)


def _build_name_scan_response(name):
    """Encode the Complete Local Name AD structure for the BLE scan response."""
    name_bytes = name.encode("utf-8") if isinstance(name, str) else bytes(name)
    if len(name_bytes) > 29:
        print("PAIR_NAME-derived BLE name is too long ({}); truncating".format(len(name_bytes)))
        name_bytes = name_bytes[:29]
    return bytes((len(name_bytes) + 1, _ADV_TYPE_COMPLETE_NAME)) + name_bytes


# === BLE Peripheral ===
class BLESimplePeripheral:
    """BLE Peripheral advertising Nordic UART Service with PAIR handshake."""

    def __init__(self, ble, name="Pico-NFC"):
        self._ble = ble
        self._ble.active(False)
        time.sleep(0.1)
        self._ble.active(True)
        time.sleep(0.1)
        try:
            self._ble.config(gap_name=name)
        except Exception as e:
            print("Could not set gap_name: {}".format(e))
        self._ble.irq(self._irq)

        # Log MAC address
        try:
            mac_data = self._ble.config('mac')
            if isinstance(mac_data, tuple) and len(mac_data) >= 2:
                mac_bytes = mac_data[1]
                if isinstance(mac_bytes, bytes) and len(mac_bytes) == 6:
                    print("BLE MAC: " + ':'.join('{:02X}'.format(b) for b in mac_bytes))
        except Exception as e:
            print("Could not read MAC: {}".format(e))

        ((self._handle_tx, self._handle_rx),) = self._ble.gatts_register_services((_UART_SERVICE,))

        self._connections = set()
        self._authenticated = {}
        self._pair_name = PAIR_NAME
        self._payload = advertising_payload(services=[_UART_UUID])
        self._resp_payload = _build_name_scan_response(name)
        self._advertise()

    def _irq(self, event, data):
        if event == _IRQ_CENTRAL_CONNECT:
            conn_handle, _, _ = data
            print("Connected: {}".format(conn_handle))
            self._connections.add(conn_handle)
            self._authenticated[conn_handle] = False
        elif event == _IRQ_CENTRAL_DISCONNECT:
            conn_handle, _, _ = data
            print("Disconnected: {}".format(conn_handle))
            self._connections.discard(conn_handle)
            self._authenticated.pop(conn_handle, None)
            self._advertise()
        elif event == _IRQ_GATTS_WRITE:
            conn_handle, value_handle = data
            if value_handle != self._handle_rx:
                return
            value = self._ble.gatts_read(value_handle)
            if not self._authenticated.get(conn_handle, False):
                self._handle_pair_attempt(conn_handle, value)

    def _handle_pair_attempt(self, conn_handle, value):
        try:
            text = value.decode('utf-8').strip()
        except Exception:
            text = ""
        expected = "PAIR:" + self._pair_name
        if text == expected:
            self._authenticated[conn_handle] = True
            print("Paired conn={} PAIR_NAME='{}'".format(conn_handle, self._pair_name))
            try:
                self._ble.gatts_notify(conn_handle, self._handle_tx, b"PAIR_OK")
            except Exception as e:
                print("Failed to send PAIR_OK: {}".format(e))
        else:
            print("Pair failed conn={} got={!r} expected={!r}".format(conn_handle, text, expected))
            try:
                self._ble.gatts_notify(conn_handle, self._handle_tx, b"PAIR_FAIL")
            except Exception:
                pass

    def notify_all_paired(self, data):
        """Send data to all authenticated (paired) central devices."""
        for conn_handle in self._connections:
            if self._authenticated.get(conn_handle, False):
                try:
                    self._ble.gatts_notify(conn_handle, self._handle_tx, data)
                except Exception as e:
                    print("Notify error on conn={}: {}".format(conn_handle, e))

    def is_any_paired(self):
        return any(self._authenticated.get(ch, False) for ch in self._connections)

    def _advertise(self, interval_us=500000):
        print("Advertising as '{}' (PAIR_NAME='{}')...".format(DEVICE_NAME, PAIR_NAME))
        self._ble.gap_advertise(
            interval_us,
            adv_data=self._payload,
            resp_data=self._resp_payload,
        )


# === NFC Init ===
sleep_ms(200)
rfid = None
for attempt in range(5):
    try:
        rfid = PiicoDev_RFID(bus=0, sda=Pin(16), scl=Pin(17), freq=100_000)
        break
    except OSError as err:
        print("RFID init attempt {} failed ({}); retrying...".format(attempt + 1, err))
        sleep_ms(200)
if rfid is None:
    raise SystemExit("RFID init failed after retries - check wiring/pull-ups")

print("NFC module ready. Place tag near the PiicoDev RFID Module.")

# === BLE Init ===
DEVICE_NAME = "Pico-NFC-" + PAIR_NAME
ble = bluetooth.BLE()
p = BLESimplePeripheral(ble, DEVICE_NAME)

print("NFC Pico BLE ready — device: '{}', PAIR_NAME: '{}'".format(DEVICE_NAME, PAIR_NAME))
print("Waiting for Zero to connect and pair...")

# === Main Loop ===
last_uid = None
last_uid_time = 0
DEBOUNCE_MS = 1500  # avoid re-sending the same tag within this window

while True:
    if rfid.tagPresent():
        uid = rfid.readID()
        now = time.ticks_ms()
        if uid and (uid != last_uid or time.ticks_diff(now, last_uid_time) > DEBOUNCE_MS):
            last_uid = uid
            last_uid_time = now
            print("TAG: {}".format(uid))
            if p.is_any_paired():
                msg = "TAG:{}".format(uid).encode("utf-8")
                p.notify_all_paired(msg)
                print("Sent via BLE: TAG:{}".format(uid))
            else:
                print("(no paired central connected — tag not sent)")
    sleep_ms(100)
