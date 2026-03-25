# Emoji Badge Controller — Connection Reliability Notes

## The problem: the Zero has no way to know the Pico has gone

`emoji-os-zero-0.3.0.py` connects to the Pico once at startup and then treats the
connection as permanent. There is currently no mechanism that tells the Zero when the
Pico loses power or goes out of range.

Three specific gaps in the current code:

1. **No `disconnected_callback`** — `BleakClient` is created without one, so Bleak
   never notifies the application when the link drops.
2. **Write failures are silently swallowed** — `send_emoji_command` prints the error
   but does not update `ble_connection_status` or attempt to reconnect.
3. **No watchdog or heartbeat** — once `init_ble_connection()` finishes, the BLE event
   loop just runs `run_forever()` with nothing polling the link health.

The BLE radio itself *will* detect the drop — via the **connection supervision
timeout**, which is typically around six seconds — but the application is never
told about it.

---

## How to fix it: three complementary approaches

The three approaches below can be used independently or together.
Approach 1 (the callback) is the most important one; approaches 2 and 3 add extra
robustness.

### 1. Use Bleak's `disconnected_callback`

Bleak lets you register a callback that fires as soon as the host BLE stack detects
the link is gone (at the end of the supervision timeout).

```python
def _on_disconnect(client: BleakClient):
    global ble_connection_status
    print("⚠ Pico disconnected unexpectedly")
    ble_controller.connected = False
    ble_connection_status = "disconnected"
    # Queue a reconnect attempt from the BLE event loop
    asyncio.run_coroutine_threadsafe(_reconnect(), ble_event_loop)
    draw_connection_indicator()
    disp.LCD_ShowImage(image, 0, 0)

async def _reconnect():
    """Scan and reconnect after an unexpected drop."""
    await asyncio.sleep(2)          # brief back-off
    if await ble_controller.scan_for_device(timeout=10):
        await ble_controller.connect_to_device()
```

Then pass it when building the client inside `connect_to_device()`:

```python
self.client = BleakClient(
    self.device_address,
    disconnected_callback=_on_disconnect,
)
```

This alone is enough to update the on-screen indicator within ~6 seconds of the
Pico losing power.

---

### 2. Treat a failed write as a disconnection signal

`send_emoji_command` already catches write exceptions. Extend it to update the
connection state and trigger a reconnect when the write fails:

```python
async def send_emoji_command(self, menu, pos, neg):
    if not self.client or not self.client.is_connected:
        print("Not connected to any device")
        return False

    command = f"{menu}:{pos}:{neg}".encode("utf-8")
    try:
        await self.client.write_gatt_char(UART_RX_CHAR_UUID, command)
        print(f"✓ Sent emoji command: '{command.decode()}'")
        return True
    except Exception as e:
        print(f"✗ Send failed: {e} — marking as disconnected")
        self.connected = False
        global ble_connection_status
        ble_connection_status = "disconnected"
        draw_connection_indicator()
        disp.LCD_ShowImage(image, 0, 0)
        asyncio.run_coroutine_threadsafe(_reconnect(), ble_event_loop)
        return False
```

This catches cases where the supervision timeout has already elapsed by the time the
next emoji is sent.

---

### 3. Add a periodic heartbeat

A background task that sends a lightweight `STATUS` ping every few seconds gives you
a maximum detection latency that you control, rather than relying on the BLE
supervision timeout.

```python
async def _heartbeat_loop(interval_s: float = 5.0):
    """Send a STATUS ping on the UART RX characteristic to keep the link alive
    and detect drops quickly."""
    while True:
        await asyncio.sleep(interval_s)
        if ble_controller.client and ble_controller.client.is_connected:
            try:
                await ble_controller.client.write_gatt_char(
                    UART_RX_CHAR_UUID, b"STATUS"
                )
            except Exception:
                # Write failed — the disconnected_callback will handle clean-up,
                # but we can also trigger it here as a belt-and-braces measure.
                pass
```

Start it inside `connect_to_device()` after a successful connection:

```python
ble_event_loop.create_task(_heartbeat_loop(interval_s=5))
```

> **Note:** the Pico firmware needs to accept and silently ignore `STATUS` messages so
> they do not trigger unintended display changes.

---

## What the user sees

With approach 1 in place:

| Event | Display | Timing |
|-------|---------|--------|
| Pico powers off | Indicator switches to "not connected" | ≤ 6 s (supervision timeout) |
| Reconnect scan running | Indicator switches to "connecting" | Immediate |
| Pico powers back on and is found | Indicator switches to "connected" | Next scan window |

---

## Summary of recommended changes

| Priority | Change | File |
|----------|--------|------|
| High | Pass `disconnected_callback` to `BleakClient` | `emoji-os-zero-0.3.0.py` |
| High | Update `ble_connection_status` and redraw on write failure | `emoji-os-zero-0.3.0.py` |
| Medium | Add `_reconnect()` coroutine and call it from both failure paths | `emoji-os-zero-0.3.0.py` |
| Low | Add `_heartbeat_loop()` for faster detection when no emoji is sent | `emoji-os-zero-0.3.0.py` |
| Low | Make Pico firmware silently accept `STATUS` messages | Pico firmware |
