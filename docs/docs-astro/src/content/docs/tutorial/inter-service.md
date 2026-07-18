---
title: 'Inter-Service'
description: 'Services communicate via Message Bus — no HTTP, no serialization overhead.'
---

# Inter-Service

Services communicate via Message Bus — no HTTP, no serialization overhead.

## The Problem

Traditional microservices communicate over HTTP:

```
Order Service → HTTP → Inventory Service → HTTP → Analytics Service
```

Every call means: network latency, serialization, connection management.

## The EVOID Way

EVOID services communicate through the runtime — zero overhead:

```
Order Service → Message Bus → Inventory Service
                  (in-process, no network)
```

## Message Bus

```python
from evoid.core.message_bus import publish, subscribe, Message
from evoid import Intent, Level

# Service A: Orders — publishes when order is placed
async def handle_create_order(intent: Intent) -> dict:
    body = intent.metadata.get("body", {})

    # Publish to inventory service
    await publish(
        Intent(
            name="stock_updated",
            level=Level.STANDARD,
            metadata={"sandwich": body.get("sandwich"), "qty": -1},
        ),
        source="orders",
    )

    return {"status": "created"}

# Service B: Inventory — subscribes to stock updates
async def handle_stock_update(intent: Intent) -> dict:
    sandwich = intent.metadata.get("sandwich")
    qty_change = intent.metadata.get("qty", 0)
    # Update inventory
    return {"updated": True, "sandwich": sandwich}

subscribe("stock_updated", handle_stock_update)
```

## Topic Matching

Subscribe by intent name, level, or wildcard:

```python
# Exact match
subscribe("order_placed", handler)

# Level-based
subscribe("critical", handler)  # All critical intents

# Wildcard
subscribe("*", handler)  # All intents
```

## Request-Reply Pattern

For synchronous communication:

```python
from evoid.core.message_bus import publish

# Send and wait for response
result = await publish(
    Intent(name="check_inventory", level=Level.STANDARD),
    source="orders",
    target="inventory",
)
# result contains responses from subscribers
```

## Message History

Debug inter-service communication:

```python
from evoid.core.message_bus import get_history

history = get_history()
for msg in history:
    print(f"{msg.source} → {msg.intent.name}: {msg.metadata}")
```

## What You Learned

| Concept | What It Is |
|---------|-----------|
| Message Bus | In-process inter-service communication |
| `publish()` | Send Intents to subscribers |
| `subscribe()` | Listen for specific Intents |
| Topic matching | Exact, level-based, wildcard |
| Message history | Debug communication flow |

## Next: Inventory Service

Let's build the inventory service — [Inventory Service](inventory-service.md).
