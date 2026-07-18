---
title: 'Real-time Updates'
description: 'WebSocket for live order status. Streaming data to clients.'
---

# Real-time Updates

WebSocket for live order status. Streaming data to clients.

## The Need

Sandy's customers want live order tracking: "Your BLT is being prepared..."

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

## Next: Plugin System

Let's extend EVOID with plugins — [Plugin System](plugins.md).
