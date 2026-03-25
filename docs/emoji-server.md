# Emoji Server — NestJS Design Exploration

A NestJS server that sits between the Raspberry Pi Zero controller and a web dashboard.
The Zero pushes status events to the server via HTTP; the server holds the current state
and streams live updates to the dashboard over WebSockets.

---

## System overview

```text
┌─────────────────────┐   BLE   ┌──────────────┐
│  Raspberry Pi Pico  │◄────────│  Pi Zero 2 W │
│  (emoji badge)      │         │  emoji-os    │
└─────────────────────┘         └──────┬───────┘
                                       │ HTTP POST
                                       ▼
                               ┌───────────────┐
                               │  NestJS server│
                               │  (this doc)   │
                               └──────┬────────┘
                                      │ WebSocket
                                      ▼
                               ┌───────────────┐
                               │  Dashboard    │
                               │  (frontend)   │
                               └───────────────┘
```

The server is likely deployed on the same local network — either on a home server, a
Pi, or a NAS. It does not need to be internet-facing.

---

## What the Zero needs to report

Based on the state tracked in `emoji-os-zero-0.3.0.py`, two categories of event
are worth sending.

### 1. BLE connection status changes

Fires whenever `ble_connection_status` changes.

```json
{
  "deviceId": "zero-living-room",
  "bleStatus": "connected",
  "timestamp": "2026-03-25T10:00:00.000Z"
}
```

Possible `bleStatus` values: `idle` | `connecting` | `connected` | `disconnected`

### 2. Emoji sent to Pico

Fires inside `send_emoji_command` after a successful write.

```json
{
  "deviceId": "zero-living-room",
  "menu": 0,
  "pos": 1,
  "neg": 0,
  "label": "regular",
  "timestamp": "2026-03-25T10:00:01.000Z"
}
```

`label` is a human-readable name derived from the menu/pos/neg mapping (computed
on the Zero or server-side from a shared lookup table).

---

## NestJS module structure

```text
src/
├── app.module.ts
├── status/
│   ├── status.module.ts
│   ├── status.controller.ts   ← POST /api/status
│   └── status.service.ts
├── emoji/
│   ├── emoji.module.ts
│   ├── emoji.controller.ts    ← POST /api/emoji
│   └── emoji.service.ts
├── state/
│   ├── state.module.ts
│   └── state.service.ts       ← in-memory current state
├── gateway/
│   ├── gateway.module.ts
│   └── events.gateway.ts      ← WebSocket gateway
└── common/
    └── dto/
        ├── status-event.dto.ts
        └── emoji-event.dto.ts
```

---

## REST API

### `POST /api/status`

Called by the Zero whenever `ble_connection_status` changes.

**Request body:**

```json
{
  "deviceId": "zero-living-room",
  "bleStatus": "connected",
  "timestamp": "2026-03-25T10:00:00.000Z"
}
```

**Response:** `201 Created`

**What the server does:**

1. Validates the DTO with `class-validator`
2. Updates `StateService.setBleStatus(deviceId, bleStatus)`
3. Emits a `status.changed` WebSocket event to all connected dashboard clients

---

### `POST /api/emoji`

Called by the Zero each time it sends an emoji command to the Pico.

**Request body:**

```json
{
  "deviceId": "zero-living-room",
  "menu": 0,
  "pos": 1,
  "neg": 0,
  "label": "regular",
  "timestamp": "2026-03-25T10:00:01.000Z"
}
```

**Response:** `201 Created`

**What the server does:**

1. Validates the DTO
2. Updates `StateService.setLastEmoji(deviceId, event)`
3. Appends to an in-memory event history (last N events)
4. Emits an `emoji.sent` WebSocket event

---

### `GET /api/state`

Called by the dashboard on initial load to get the full current state without
waiting for a WebSocket event.

**Response:**

```json
{
  "devices": {
    "zero-living-room": {
      "bleStatus": "connected",
      "lastEmoji": {
        "menu": 0,
        "pos": 1,
        "neg": 0,
        "label": "regular",
        "timestamp": "2026-03-25T10:00:01.000Z"
      },
      "updatedAt": "2026-03-25T10:00:01.000Z"
    }
  },
  "recentEvents": [...]
}
```

---

### `GET /api/events`

Returns the last N events (BLE status changes + emoji sends) across all devices,
newest first. Useful for an activity log on the dashboard.

```json
[
  { "type": "emoji.sent", "deviceId": "zero-living-room", "menu": 0, "pos": 1, ... },
  { "type": "status.changed", "deviceId": "zero-living-room", "bleStatus": "connected", ... }
]
```

---

## WebSocket gateway

Use the built-in `@WebSocketGateway` with Socket.io (the NestJS default).
The dashboard connects once and subscribes to events.

### Events emitted by the server

| Event name | Payload | Trigger |
|---|---|---|
| `status.changed` | `StatusEventDto` | `POST /api/status` received |
| `emoji.sent` | `EmojiEventDto` | `POST /api/emoji` received |
| `state.snapshot` | Full `GET /api/state` response | On client connect |

### Client subscribe pattern (dashboard)

```typescript
const socket = io('http://emoji-server.local:3000');

socket.on('connect', () => {
  // server automatically emits state.snapshot on connect
});

socket.on('status.changed', (event) => {
  updateBleIndicator(event.deviceId, event.bleStatus);
});

socket.on('emoji.sent', (event) => {
  updateEmojiDisplay(event.deviceId, event);
});
```

---

## DTOs

### `StatusEventDto`

```typescript
import { IsString, IsIn, IsDateString } from 'class-validator';

export class StatusEventDto {
  @IsString()
  deviceId: string;

  @IsIn(['idle', 'connecting', 'connected', 'disconnected'])
  bleStatus: string;

  @IsDateString()
  timestamp: string;
}
```

### `EmojiEventDto`

```typescript
import { IsString, IsInt, Min, Max, IsDateString, IsOptional } from 'class-validator';

export class EmojiEventDto {
  @IsString()
  deviceId: string;

  @IsInt() @Min(0) @Max(3)
  menu: number;

  @IsInt() @Min(0) @Max(4)
  pos: number;

  @IsInt() @Min(0) @Max(4)
  neg: number;

  @IsString() @IsOptional()
  label?: string;

  @IsDateString()
  timestamp: string;
}
```

---

## State service

Holds all current state in memory. No database is required for an MVP — a `Map`
keyed by `deviceId` is sufficient. Persistence (SQLite, Postgres) can be added
later if history across server restarts matters.

```typescript
@Injectable()
export class StateService {
  private readonly devices = new Map<string, DeviceState>();
  private readonly history: AnyEvent[] = [];
  private readonly maxHistory = 100;

  setBleStatus(deviceId: string, bleStatus: string): void { ... }
  setLastEmoji(deviceId: string, event: EmojiEventDto): void { ... }
  pushHistory(event: AnyEvent): void { ... }
  getSnapshot(): SnapshotDto { ... }
}
```

---

## Changes required on the Zero

The Zero needs to make outbound HTTP POST requests. The simplest addition is a
helper that fires and forgets:

```python
import requests
import threading

SERVER_URL = "http://emoji-server.local:3000"
DEVICE_ID  = "zero-living-room"

def post_to_server(path: str, payload: dict):
    def _post():
        try:
            requests.post(f"{SERVER_URL}{path}", json=payload, timeout=3)
        except Exception as e:
            print(f"Server post failed: {e}")
    threading.Thread(target=_post, daemon=True).start()
```

Call sites:

```python
# When ble_connection_status changes
post_to_server("/api/status", {
    "deviceId": DEVICE_ID,
    "bleStatus": ble_connection_status,
    "timestamp": datetime.utcnow().isoformat() + "Z",
})

# Inside send_emoji_command, after a successful write
post_to_server("/api/emoji", {
    "deviceId": DEVICE_ID,
    "menu": menu, "pos": pos, "neg": neg,
    "timestamp": datetime.utcnow().isoformat() + "Z",
})
```

Using a daemon thread means a slow or unreachable server never blocks the UI loop.

---

## Authentication

On a private home network, a simple shared API key in an `x-api-key` header is
sufficient. NestJS makes this easy with a `Guard`:

```typescript
@Injectable()
export class ApiKeyGuard implements CanActivate {
  canActivate(context: ExecutionContext): boolean {
    const request = context.switchToHttp().getRequest();
    return request.headers['x-api-key'] === process.env.API_KEY;
  }
}
```

Apply it globally or per controller. The Zero adds the header to every request.

---

## Open questions / future directions

| Topic | Options |
|---|---|
| **Persistence** | SQLite via TypeORM for event history across restarts |
| **Multiple devices** | The `deviceId` field already supports this — the dashboard just needs to render a card per device |
| **Pico status** | The server only knows what the Zero reports. If the disconnection detection from `emoji-badge-controller.md` is implemented, the Zero can also report `picoStatus: connected \| disconnected` |
| **Frontend framework** | React + Socket.io client is a natural fit; or a simple Svelte app |
| **Dashboard features** | Live BLE status indicator, last emoji sent, event log, per-device uptime |
| **Heartbeat endpoint** | `POST /api/heartbeat` — Zero pings every 30 s so the dashboard can show when the Zero itself is offline |
