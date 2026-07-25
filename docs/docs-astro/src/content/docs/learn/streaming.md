---
title: 'Streaming'
description: 'WebSocket connections and streaming responses in EVOID.'
---

# Streaming

EVOID supports streaming through adapters. The WebSocket adapter converts bidirectional messages to Intents.

## WebSocket Adapter

```python
from evoid.adapters.websocket import WebSocketAdapter

adapter = WebSocketAdapter()
```

Each WebSocket message becomes an Intent that flows through the pipeline. Responses are sent back to the client.

## Streaming HTTP Responses

For server-sent events or chunked responses, return an async generator from your handler:

```python
@get("/stream")
async def stream_data(ctx):
    for chunk in read_large_file():
        yield chunk
```

The ASGI adapter detects the generator and streams the response.

## Game State Sync

The Godot adapter uses streaming for real-time game state. The `evoid-transport` plugin provides low-latency UDP streaming:

```python
from evoid_transport import EvoidUDPPort

transport = EvoidUDPPort()
await transport.broadcast_state_sync(game_state, tick=60)
```

## Related

- [Adapters](adapters.md): how adapters handle different transports
- [Real-time Updates](../tutorial/real-time.md): tutorial example
