# Emoji Server — API and Pi Zero integration

This document describes the HTTP contract between the Pi Zero controller
(`emoji-os-zero-0.3.0.py`) and a dashboard backend. The original shape was a NestJS
design exploration; the **emoji-app** deployment implements the same `POST /api/status`
and `POST /api/emoji` payloads, plus `GET /api/badges` for the Badges UI.

The Zero pushes events over HTTPS; the server holds current state and can push live
updates to the dashboard over WebSockets (with polling fallback when WebSockets are
unavailable, for example on some cloud hosts).

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
                               │  emoji server │
                               │  (API + UI)   │
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

The Zero tracks `ble_connection_status` locally as `idle` | `connecting` |
`connected` | `disconnected`. **HTTP `POST /api/status` only sends `connected` or
`disconnected`**, matching the emoji-app validator (see Pi Zero implementation below
for when each is posted).

```json
{
  "controllerId": "zero-living-room",
  "badgeId": "badge-kitchen",
  "bleStatus": "connected",
  "timestamp": "2026-03-25T10:00:00.000Z"
}
```

### 2. Emoji sent to Pico

Fires inside `send_emoji_command` after a successful write.

```json
{
  "controllerId": "zero-living-room",
  "badgeId": "badge-kitchen",
  "menu": 0,
  "pos": 1,
  "neg": 0,
  "label": "regular",
  "timestamp": "2026-03-25T10:00:01.000Z"
}
```

`label` is a human-readable name derived from the menu/pos/neg mapping (computed
on the Zero or server-side from a shared lookup table).

## REST API

### `POST /api/status`

Called by the Zero whenever `ble_connection_status` changes.

**Request body:**

```json
{
  "controllerId": "zero-living-room",
  "badgeId": "badge-kitchen",
  "bleStatus": "connected",
  "timestamp": "2026-03-25T10:00:00.000Z"
}
```

**Response:** `201 Created` with body like `{ "ok": true }` (emoji-app).

**What the server does:**

1. Validates the request body
2. Updates stored BLE status for the `(controllerId, badgeId)` row (for example in
   `GET /api/badges`)
3. May emit a WebSocket event to dashboard clients when supported

---

### `POST /api/emoji`

Called by the Zero each time it sends an emoji command to the Pico.

**Request body:**

```json
{
  "controllerId": "zero-living-room",
  "badgeId": "badge-kitchen",
  "menu": 0,
  "pos": 1,
  "neg": 0,
  "label": "regular",
  "timestamp": "2026-03-25T10:00:01.000Z"
}
```

**Response:** `201 Created` with body like `{ "ok": true }` (emoji-app).

**What the server does:**

1. Validates the request body
2. Updates last emoji / label for the `(controllerId, badgeId)` row
3. May append to an event history and emit WebSocket updates when supported

---

### `GET /api/state`

Called by the dashboard on initial load to get the full current state without
waiting for a WebSocket event.

**Response:**

```json
{
  "controllers": {
    "zero-living-room": {
      "badges": {
        "badge-kitchen": {
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
      "updatedAt": "2026-03-25T10:00:01.000Z"
    }
  },
  "recentEvents": [...]
}
```

---

### `GET /api/badges`

Used by the **emoji-app** Badges page on load and during polling fallback. Returns
current rows for all badges the server knows about (typically keyed by
`controllerId` + `badgeId`). Exact JSON shape depends on the app; expect a
`badges` array (or similar) listing link status and last emoji per row.

---

### `GET /api/events`

Returns the last N events (BLE status changes + emoji sends) across all devices,
newest first. Useful for an activity log on the dashboard.

```json
[
  { "type": "emoji.sent", "controllerId": "zero-living-room", "badgeId": "badge-kitchen", "menu": 0, "pos": 1, ... },
  { "type": "status.changed", "controllerId": "zero-living-room", "badgeId": "badge-kitchen", "bleStatus": "connected", ... }
]
```

---

## WebSocket gateway

In **emoji-app** production, the browser typically connects to
`wss://<host>/ws` (same origin as the HTTPS site). Some hosts (for example AWS App
Runner) may not support WebSocket upgrades; the Badges UI can fall back to polling
`GET /api/badges` on an interval (for example about every 10 seconds), pausing while
the tab is hidden.

For a self-hosted NestJS stack, use the built-in `@WebSocketGateway` with
Socket.io (the NestJS default). The dashboard connects once and subscribes to events.

### Events emitted by the server

|Event name|Payload|Trigger|
|---|---|---|
|`status.changed`|`StatusEventDto`|`POST /api/status` received|
|`emoji.sent`|`EmojiEventDto`|`POST /api/emoji` received|
|`state.snapshot`|Full `GET /api/state` response|On client connect|

### Client subscribe pattern (dashboard)

```typescript
const socket = io('http://emoji-server.local:3000');

socket.on('connect', () => {
  // server automatically emits state.snapshot on connect
});

socket.on('status.changed', (event) => {
  updateBleIndicator(event.controllerId, event.badgeId, event.bleStatus);
});

socket.on('emoji.sent', (event) => {
  updateEmojiDisplay(event.controllerId, event.badgeId, event);
});
```

---

## DTOs

### `StatusEventDto`

```typescript
import { IsString, IsIn, IsDateString } from 'class-validator';

export class StatusEventDto {
  @IsString()
  controllerId: string;

  @IsString()
  badgeId: string;

  @IsIn(['connected', 'disconnected'])
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
  controllerId: string;

  @IsString()
  badgeId: string;

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
keyed by `controllerId + badgeId` is sufficient. Persistence (SQLite, Postgres)
can be added later if history across server restarts matters.

```typescript
@Injectable()
export class StateService {
  private readonly controllers = new Map<string, ControllerState>();
  private readonly history: AnyEvent[] = [];
  private readonly maxHistory = 100;

  setBleStatus(controllerId: string, badgeId: string, bleStatus: string): void { ... }
  setLastEmoji(controllerId: string, badgeId: string, event: EmojiEventDto): void { ... }
  pushHistory(event: AnyEvent): void { ... }
  getSnapshot(): SnapshotDto { ... }
}
```

---

## Pi Zero controller implementation (`emoji-os-zero-0.3.0.py`)

The in-repo Zero firmware implements the HTTP client as follows.

### Configuration

|Variable|Purpose|
|---|---|
|`SERVER_URL`|Base URL only, **no trailing slash** (for example `https://…awsapprunner.com`). Empty disables all posts.|
|`CONTROLLER_ID`|Stable logical id for this Pi Zero; sent as `controllerId` on every request.|
|`BADGE_ID`|Optional. If non-empty (after strip), used as `badgeId` on every request. If empty, `badgeId` is derived from the BLE peer (see below).|
|`API_HEADERS`|Optional dict merged into `requests.post(..., headers=...)`, for example `{"x-api-key": "…"}`.|

### `badgeId` resolution

1. If `BADGE_ID` is set, it is used as `badgeId`.
2. Otherwise Bleak’s `device.address` for the connected Pico is normalized to a
   stable slug: lower-case MAC with colons replaced by hyphens, prefixed with
   `badge-` (for example `badge-28-cd-c1-05-ab-a4`).
3. If no address is available at post time, `badgeId` is `"unknown"`.

### `label` for `POST /api/emoji`

The helper `_emoji_label(menu, pos, neg)` maps the same selections as the on-device
UI (`get_main_emoji`) to short slugs (for example menu `0`, pos `1`, neg `0` →
`"regular"`). Unmapped triples fall back to `"m{menu}-{pos}-{neg}"`.

### Payload builders

- `_status_payload(ble_status)` builds `{ controllerId, badgeId, bleStatus, timestamp }`.
- `_emoji_payload(menu, pos, neg)` adds `menu`, `pos`, `neg`, `label`, `timestamp`.
- `_utc_iso_timestamp()` uses `datetime.now(timezone.utc).isoformat()`.

### When HTTP posts run

`post_to_server` is a no-op if `SERVER_URL` is empty. Otherwise it runs the request
in a **daemon thread** with a short timeout so the UI loop never blocks.

|Event|Endpoint|Notes|
|---|---|---|
|BLE connect succeeds|`POST /api/status`|`bleStatus`: `connected`|
|BLE write fails or link drops|`POST /api/status`|`bleStatus`: `disconnected`|
|Unexpected Pico disconnect (Bleak callback)|`POST /api/status`|`disconnected`|
|User-initiated `disconnect()`|`POST /api/status`|`disconnected`|
|Emoji command written successfully|`POST /api/emoji`|Includes `label` from `_emoji_label`|

Local states `idle` and `connecting` are **not** sent on `POST /api/status` in this
implementation.

### Example (trimmed)

```python
def post_to_server(path: str, payload: dict):
    if not SERVER_URL:
        return
    def _post():
        try:
            kw = {"json": payload, "timeout": 3}
            if API_HEADERS:
                kw["headers"] = API_HEADERS
            requests.post(f"{SERVER_URL}{path}", **kw)
        except Exception as e:
            print(f"Server post failed ({path}): {e}")
    threading.Thread(target=_post, daemon=True).start()
```

### Expected HTTP responses (emoji-app)

|HTTP status|Meaning|
|---|---|
|`201`|Success; body often `{ "ok": true }`|
|`400`|Validation error; server may return `error` / `details`|

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

Apply it globally or per controller. The Zero can send the same key via
`API_HEADERS` on every `post_to_server` request when configured.

---

## Open questions / future directions

|Topic|Options|
|---|---|
|**Persistence**|SQLite via TypeORM for event history across restarts|
|**Pico status**|The server only knows what the Zero reports. If the disconnection detection from `emoji-badge-controller.md` is implemented, the Zero can also report `picoStatus: connected \| disconnected`|
|**Frontend framework**|React + Socket.io client is a natural fit; or a simple Svelte app|
|**Dashboard features**|Live BLE status indicator, last emoji sent, event log, per-device uptime|
|**Heartbeat endpoint**|`POST /api/heartbeat` — Zero pings every 30 s so the dashboard can show when the Zero itself is offline|

---

## Future multi-device support

This API should treat `controllerId` and `badgeId` as first-class identifiers.

- `controllerId` identifies the Pi Zero unit sending the HTTP event.
- `badgeId` identifies the Pico badge currently connected over BLE.
- The tuple `(controllerId, badgeId)` is the primary state key.

For implementation safety and rollout:

1. Add `controllerId` and `badgeId` to `StatusEventDto` and `EmojiEventDto`.
2. Keep `deviceId` as optional input during migration.
3. In controllers, map old payloads to the new shape:
   - `controllerId = deviceId` when `controllerId` is missing
   - `badgeId = "unknown"` when `badgeId` is missing
4. Emit only the new event shape over WebSocket.
5. Update dashboard selectors to render cards by `controllerId` and `badgeId`.
6. After clients are upgraded, remove `deviceId` from DTOs and docs.

Identifier guidance:

- Do not use Windows `COMx` values as badge identity in the API.
- Prefer a stable logical `badgeId` (for example, `badge-kitchen`).
- Keep BLE MAC address as metadata for diagnostics and pairing workflows.
