---
title: 'Microservices Without the Overhead'
description: 'How EVOID eliminates network overhead between services while keeping the benefits of microservices architecture.'
---

# Microservices Without the Overhead

Traditional microservices communicate over HTTP. EVOID services communicate through the runtime — no network, no serialization, no latency.

## The Problem with Traditional Microservices

Consider a game with a chat system:

```
┌─────────────┐    HTTP/WebSocket    ┌─────────────┐
│  Game API   │ ◄──────────────────► │  Chat API   │
│  (FastAPI)  │    network overhead  │  (FastAPI)  │
└─────────────┘                      └─────────────┘
       │                                      │
       ▼                                      ▼
  PostgreSQL                             Redis Cache
```

Every interaction between Game and Chat requires:
- HTTP request/response (or WebSocket)
- Serialization (JSON encode/decode)
- Network latency (round-trip time)
- Error handling for network failures
- Separate dependency management per service
- Separate deployment, monitoring, scaling

## How EVOID Solves This

```
┌─────────────────────────────────────────────┐
│             EVOID Runtime (IOP)              │
│  ┌──────────────┐      ┌──────────────┐     │
│  │  Game Service │      │  Chat Service │     │
│  │  (Intents:    │      │  (Intents:    │     │
│  │   route,      │      │   route,      │     │
│  │   validate,   │      │   validate,   │     │
│  │   cache,      │      │   cache,      │     │
│  │   authorize)  │      │   authorize)  │     │
│  └──────┬───────┘      └──────┬───────┘     │
│         │                     │               │
│         └──────────┬──────────┘               │
│                    ▼                          │
│         ┌─────────────────────┐               │
│         │   Shared Engines    │               │
│         │  - Validation       │               │
│         │  - Serialization    │               │
│         │  - Cache            │               │
│         │  - Authorization    │               │
│         └─────────────────────┘               │
└─────────────────────────────────────────────┘
          ▲                    ▲
          │                    │
    Game Client           Chat Client
```

Both services run in the same runtime. Communication is direct function calls, not HTTP.

## Inter-Service Communication

### Traditional: HTTP between services

```python
# Game Service needs to send a chat message
import httpx

async def send_chat_message(game_id: str, player: str, message: str):
    # HTTP request to Chat API — network overhead!
    async with httpx.AsyncClient() as client:
        response = await client.post(
            "http://chat-api:8000/messages",
            json={"game_id": game_id, "player": player, "message": message}
        )
        return response.json()
```

Problems: network latency, serialization, error handling, connection management.

### EVOID: Direct function call through message bus

```python
from evoid.core.service import Service, call, on
from evoid import Intent, Level

# Game Service
game_service = Service(name="game")
chat_service = Service(name="chat")

# Chat Service handles message intents
async def handle_chat_message(intent: Intent) -> dict:
    message = intent.metadata["message"]
    # Save to database
    await db.save_message(message)
    return {"status": "sent"}

on(chat_service, "send_message", handle_chat_message)

# Game Service calls Chat Service directly — no HTTP!
async def player_sends_chat(player: str, message: str):
    intent = Intent(
        name="send_message",
        level=Level.STANDARD,
        metadata={"player": player, "message": message},
    )
    result = await call(game_service, intent)
    return result
```

**No HTTP. No serialization. Direct function call through the message bus.**

## Shared Engines

In traditional microservices, each service manages its own dependencies:

```
Game API:  pip install pydantic cachetools redis pyjwt
Chat API:  pip install pydantic cachetools redis pyjwt
```

In EVOID, engines are shared across all services:

```python
from evoid.engines.serializer import set_serializer
from evoid.engines.schema import set_validator

# Configure once — all services use it
set_serializer(MySerializer())
set_validator(MyValidator())

# Both services automatically use the same engines
# No duplicate dependencies, no configuration drift
```

## Real-World Scenario: Game + Chat

A player sends a message in chat:

### Traditional architecture

```
1. Game Client → Game API (HTTP)
2. Game API → Chat API (HTTP)
3. Chat API → Database (save message)
4. Chat API → Chat Client (WebSocket)
5. Chat Client → Game Client (WebSocket)
```

**Total latency**: Sum of all network round-trips (minimum 3-4 hops)

### EVOID architecture

```
1. Game Client → EVOID Runtime (HTTP)
2. EVOID Runtime → ChatService (direct function call)
3. ChatService → Database (save message)
4. ChatService → Chat Client (WebSocket)
```

**Total latency**: One HTTP round-trip for the initial request. Everything else is in-process (typically < 1ms).

## Comparison Table

| Feature | Traditional (FastAPI + HTTP) | EVOID (IOP Runtime) |
|---------|----------------------------|---------------------|
| **Inter-service communication** | HTTP/gRPC (network overhead) | Direct function call (no overhead) |
| **Cache management** | Separate library per service (e.g., `redis-py`) | Shared engine, configured once |
| **Validation & serialization** | Pydantic/Marshmallow installed per service | Shared engines, pluggable |
| **Logging & monitoring** | Separate tools (e.g., `prometheus`) | Unified pipeline inspection |
| **Dependency management** | Each service has its own `requirements.txt` | Single core for all services |
| **Latency (combined scenarios)** | High (multiple HTTP round-trips) | Very low (in-process communication) |
| **Scaling** | Horizontal with network management challenges | Vertical within runtime, horizontal with distributed architecture |

## Key Insight

EVOID doesn't replace FastAPI — it complements it. Use FastAPI as the HTTP gateway for external clients. Use EVOID's runtime for internal service communication.

```python
# External: FastAPI handles HTTP
from fastapi import FastAPI
from evoid.core.service import call

app = FastAPI()

@app.post("/game/send-message")
async def send_message(player: str, message: str):
    # FastAPI receives the HTTP request
    # EVOID handles internal communication
    intent = Intent(name="send_message", metadata={"player": player, "message": message})
    result = await call(chat_service, intent)
    return result
```

This gives you:
- **FastAPI speed** for external HTTP endpoints
- **EVOID runtime speed** for internal service communication
- **Unified engines** for validation, serialization, caching
- **Pipeline inspection** for observability across all services

!!! tip "IOP principle"
    Services communicate through Intents, not HTTP. The runtime handles routing, the adapter handles transport. You focus on business logic.
