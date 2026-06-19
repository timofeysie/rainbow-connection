# nfc-zero-with-pairing.py
# Runs on the Raspberry Pi Zero W (CPython 3, bleak).
# Scans for a Pico running nfc-pico-with-pairing.py, performs the
# PAIR:<name> / PAIR_OK handshake, then subscribes to BLE notify and
# prints any TAG:<uid> messages received from the Pico.
#
# Usage:
#   python nfc-zero-with-pairing.py
#
# Dependencies:
#   pip install bleak
#
# Optional: create a pair_config.py in the directory above the repo root
# (or next to this file) containing:
#   PAIR_NAME = "living-room"
# to match the PAIR_NAME on the Pico.

import asyncio
import os
import sys

# === Pairing ===
_HERE = os.path.dirname(os.path.abspath(__file__))
# tests/ -> python/ -> <repo>/ -> <repo_parent>/
_PAIR_CONFIG_DIR = os.path.normpath(os.path.join(_HERE, "..", "..", ".."))
_PAIR_CONFIG_PATH = os.path.join(_PAIR_CONFIG_DIR, "pair_config.py")

if os.path.isfile(_PAIR_CONFIG_PATH) and _PAIR_CONFIG_DIR not in sys.path:
    sys.path.insert(0, _PAIR_CONFIG_DIR)

try:
    from pair_config import PAIR_NAME  # type: ignore  # noqa: F401
except Exception:
    PAIR_NAME = "default"

TARGET_DEVICE_NAME = "Pico-NFC-" + PAIR_NAME
PAIR_HANDSHAKE_TIMEOUT_S = 5.0

print("PAIR_NAME='{}' — looking for '{}'".format(PAIR_NAME, TARGET_DEVICE_NAME), flush=True)

from bleak import BleakScanner, BleakClient
from bleak.backends.characteristic import BleakGATTCharacteristic

# Nordic UART Service UUIDs (same as Pico side)
UART_SERVICE_UUID = "6E400001-B5A3-F393-E0A9-E50E24DCCA9E"
UART_RX_CHAR_UUID = "6E400002-B5A3-F393-E0A9-E50E24DCCA9E"  # write
UART_TX_CHAR_UUID = "6E400003-B5A3-F393-E0A9-E50E24DCCA9E"  # notify


async def scan_for_device(timeout: float = 10.0) -> str | None:
    """Return the BLE address of the target Pico, or None if not found."""
    print("Scanning for '{}' ({}s)...".format(TARGET_DEVICE_NAME, timeout), flush=True)

    # Prefer service-UUID-filtered scan so we avoid iterating every BLE device.
    try:
        devices = await BleakScanner.discover(
            timeout=timeout,
            service_uuids=[UART_SERVICE_UUID],
        )
        for device in devices:
            if device.name == TARGET_DEVICE_NAME:
                print("Found by service scan: {} ({})".format(device.name, device.address), flush=True)
                return device.address
        if devices:
            print("Service scan found {} device(s) but none matched '{}'.".format(
                len(devices), TARGET_DEVICE_NAME), flush=True)
    except Exception as e:
        print("Service-UUID scan error: {} — falling back to general scan.".format(e), flush=True)

    # Fallback: general scan
    devices = await BleakScanner.discover(timeout=timeout)
    print("General scan found {} device(s):".format(len(devices)), flush=True)
    for device in devices:
        name = device.name or "(no name)"
        print("  {} | {}".format(name, device.address), flush=True)
        if device.name == TARGET_DEVICE_NAME:
            print("Found by general scan: {} ({})".format(device.name, device.address), flush=True)
            return device.address

    print("Device '{}' not found.".format(TARGET_DEVICE_NAME), flush=True)
    print("Troubleshooting:", flush=True)
    print("  1. Confirm nfc-pico-with-pairing.py is running on the Pico.", flush=True)
    print("  2. Confirm PAIR_NAME matches on both sides (currently '{}').".format(PAIR_NAME), flush=True)
    print("  3. Move the devices closer together.", flush=True)
    return None


async def do_pair_handshake(client: BleakClient) -> bool:
    """Send PAIR:<PAIR_NAME> and wait for PAIR_OK on the TX notify characteristic."""
    pair_event = asyncio.Event()
    pair_response: list[str] = []

    def _on_notify(_sender: BleakGATTCharacteristic, data: bytearray) -> None:
        try:
            text = bytes(data).decode("utf-8", "ignore").strip()
        except Exception:
            text = ""
        print("[PAIR] notify: {!r}".format(text), flush=True)
        pair_response.append(text)
        pair_event.set()

    try:
        await client.start_notify(UART_TX_CHAR_UUID, _on_notify)
    except Exception as e:
        print("[PAIR] start_notify failed: {}".format(e), flush=True)
        return False

    pair_msg = "PAIR:{}".format(PAIR_NAME).encode("utf-8")
    try:
        await client.write_gatt_char(UART_RX_CHAR_UUID, pair_msg)
        print("[PAIR] sent {!r}".format(pair_msg), flush=True)
    except Exception as e:
        print("[PAIR] write failed: {}".format(e), flush=True)
        try:
            await client.stop_notify(UART_TX_CHAR_UUID)
        except Exception:
            pass
        return False

    try:
        await asyncio.wait_for(pair_event.wait(), timeout=PAIR_HANDSHAKE_TIMEOUT_S)
    except asyncio.TimeoutError:
        print("[PAIR] handshake timed out after {}s".format(PAIR_HANDSHAKE_TIMEOUT_S), flush=True)
        try:
            await client.stop_notify(UART_TX_CHAR_UUID)
        except Exception:
            pass
        return False

    # Leave notify running so we receive TAG notifications after pairing.
    response = pair_response[0] if pair_response else ""
    if response == "PAIR_OK":
        print("[PAIR] OK — paired with PAIR_NAME='{}'".format(PAIR_NAME), flush=True)
        return True

    print("[PAIR] rejected by Pico: {!r}".format(response), flush=True)
    try:
        await client.stop_notify(UART_TX_CHAR_UUID)
    except Exception:
        pass
    return False


async def listen_for_tags(client: BleakClient) -> None:
    """Subscribe to TX notify and print TAG:<uid> messages until disconnected."""
    tag_event = asyncio.Event()

    def _on_notify(_sender: BleakGATTCharacteristic, data: bytearray) -> None:
        try:
            text = bytes(data).decode("utf-8", "ignore").strip()
        except Exception:
            text = ""
        if text.startswith("TAG:"):
            uid = text[4:]
            print("NFC tag received: {}".format(uid), flush=True)
        else:
            print("BLE notify: {!r}".format(text), flush=True)

    try:
        await client.start_notify(UART_TX_CHAR_UUID, _on_notify)
    except Exception as e:
        print("start_notify failed: {}".format(e), flush=True)
        return

    print("Listening for NFC tags — press Ctrl+C to stop.", flush=True)
    try:
        # Block here until the connection drops or the user interrupts.
        while client.is_connected:
            await asyncio.sleep(0.5)
    except asyncio.CancelledError:
        pass
    finally:
        try:
            await client.stop_notify(UART_TX_CHAR_UUID)
        except Exception:
            pass


async def main() -> None:
    address = await scan_for_device(timeout=10.0)
    if address is None:
        return

    print("Connecting to {} ({})...".format(TARGET_DEVICE_NAME, address), flush=True)
    async with BleakClient(address) as client:
        if not client.is_connected:
            print("Failed to connect.", flush=True)
            return

        print("BLE connected — running pair handshake...", flush=True)

        if not await do_pair_handshake(client):
            print("Pairing failed — disconnecting.", flush=True)
            return

        # Stop the notify subscription opened by do_pair_handshake and re-open
        # it cleanly for the tag-listening phase so the callback is replaced.
        try:
            await client.stop_notify(UART_TX_CHAR_UUID)
        except Exception:
            pass

        await listen_for_tags(client)

    print("Disconnected.", flush=True)


if __name__ == "__main__":
    try:
        asyncio.run(main())
    except KeyboardInterrupt:
        print("\nStopped by user.", flush=True)
