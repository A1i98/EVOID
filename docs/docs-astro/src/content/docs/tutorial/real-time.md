---
title: 'Real-time Updates'
description: 'WebSocket for live order status. Streaming data to clients.'
---

# Real-time Updates

WebSocket for live order status. Streaming data to clients.

## The Need

Sandy's customers want live order tracking: "Your BLT is being prepared..."

!!! info "Real-time = kitchen window"
    Instead of customers asking "is my order ready?" every 30 seconds, the kitchen shouts updates through a window. WebSocket is that window — bidirectional, persistent, no polling.

## WebSocket Adapter

```python
from evoid.adapters.websocket import create_ws_app

ws_app = create_ws_app(name="sandy-ws")

@ws_app.on("connect")
async def handle_connect(ctx):
    return {"status": "connected"}

@ws_app.on("message")
async def handle_message(ctx):
    data = ctx.metadata.get("data", {})
    if data.get("type") == "track_order":
        order_id = data.get("order_id")
        # Send live updates
        return {"order_id": order_id, "status": "preparing"}
    return {"error": "unknown message type"}

@ws_app.on("disconnect")
async def handle_disconnect(ctx):
    return {"status": "disconnected"}
```

## Server-Sent Events (SSE)

For simpler streaming:

```python
from evoid import Intent, Level, add_intent

STREAM_ORDERS = Intent(
    name="stream_orders",
    level=Level.STANDARD,
)

async def handle_stream(intent: Intent) -> list[dict]:
    """Return a list of events — adapter streams them."""
    return [
        {"event": "order_update", "data": {"id": 1, "status": "preparing"}},
        {"event": "order_update", "data": {"id": 1, "status": "ready"}},
    ]

add_intent(STREAM_ORDERS, handle_stream)
```

## Custom SSE Adapter

```python
import json
from starlette.applications import Starlette
from starlette.responses import StreamingResponse
from starlette.routing import Route
from evoid.core import Intent, Level, execute

async def handle_sse(request):
    async def generate():
        result = await execute(Intent(
            name="stream_orders",
            level=Level.STANDARD,
        ))
        if result.success:
            for event in result.value:
                yield f"data: {json.dumps(event)}\n\n"

    return StreamingResponse(generate(), media_type="text/event-stream")

app = Starlette(routes=[
    Route("/events", handle_sse, methods=["GET"]),
])
```

## What You Learned

| Concept | What It Is |
|---------|-----------|
| WebSocket | Bidirectional real-time communication |
| SSE | Server-to-client streaming |
| Custom adapters | Build your own transport layer |

## Beyond Sandy: Game Integration

The same real-time patterns power game servers. The `evoid-godot` and `evoid-transport` plugins bring IOP to game development:

```python
# Game client sends: EvoidApp.send_intent("player_move", {"x": 10, "y": 20})
# Server receives it as an Intent:

PLAYER_MOVE = Intent(
    name="game:my-game:player_move",
    level=Level.EPHEMERAL,  # Position updates are disposable
    metadata={"player_id": "abc", "x": 10, "y": 20},
)
# Pipeline: validate → handler (5s)
# Fast, no auth, no audit. Next frame corrects any errors.

# But a purchase? That's CRITICAL:
PURCHASE_ITEM = Intent(
    name="game:my-game:purchase_item",
    level=Level.CRITICAL,
    metadata={"player_id": "abc", "item": "sword", "price": 9.99},
)
# Pipeline: validate → authorize → audit → protect → handler (30s)
# Real money, full protection.
```

!!! example "Game transport: UDP for speed"
    ```python
    # WebSocket: ~2-5ms overhead (TCP, reliable, ordered)
    # UDP: ~0.5ms overhead (fast, but unreliable)
    
    # The evoid-transport plugin picks the right channel:
    # Channel 0 (RELIABLE) — card plays, purchases (CRITICAL)
    # Channel 1 (UNRELIABLE) — position updates (EPHEMERAL)
    # Channel 2 (CHAT) — chat messages (STANDARD)
    
    # Same IOP concept: level determines infrastructure.
    # Game state uses EPHEMERAL for speed.
    # Game purchases use CRITICAL for safety.
    ```

## Next: Plugin System

Let's extend EVOID with plugins — [Plugin System](plugins.md).
