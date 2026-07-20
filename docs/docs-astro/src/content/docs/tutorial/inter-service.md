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

!!! info "Message bus = kitchen passthrough"
    Instead of each station yelling across the kitchen (HTTP), they pass tickets through a window (Message Bus). Same kitchen, zero echo. The bus routes by Intent name — "stock_updated" goes to whoever's listening.

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

## Error Handling

When a subscriber fails, the error propagates to the publisher:

```python
async def handle_stock_update(intent: Intent) -> dict:
    sandwich = intent.metadata.get("sandwich")
    # If this raises, publish() gets the error
    result = await update_inventory(sandwich)
    return {"updated": True}

# Publisher checks for errors
try:
    await publish(intent, source="orders")
except Exception as e:
    # Subscriber failed — handle retry or dead letter
    print(f"Stock update failed: {e}")
```

### Catching Subscriber Errors

Use `asyncio.gather` to handle multiple subscribers independently:

```python
import asyncio

async def safe_publish(intent: Intent, source: str) -> list[dict]:
    """Publish and collect all subscriber results, even if some fail."""
    results = await publish(intent, source=source)
    # Results list may contain exceptions for failed subscribers
    return [r for r in results if not isinstance(r, Exception)]
```

## Debugging with Message History

The message bus keeps a history of all published Intents:

```python
from evoid.core.message_bus import get_history, clear_history

# See all messages
history = get_history()
for msg in history:
    print(f"{msg.source} → {msg.intent.name}")

# Clear history in tests
clear_history()
```

## What You Learned

| Concept | What It Is |
|---------|-----------|
| Message Bus | In-process inter-service communication |
| `publish()` | Send Intents to subscribers |
| `subscribe()` | Listen for specific Intents |
| Topic matching | Exact, level-based, wildcard |
| Message history | Debug communication flow |

## Plugins in the Message Bus

The `evoid-cluster` plugin extends the Message Bus across machines:

```python
# Without cluster: services communicate in-process (0ms)
# Order Service → Message Bus → Inventory Service (same process)

# With cluster: services communicate across nodes (via WebSocket)
# Order Service (Node 1) → ClusterBridge → Inventory Service (Node 2)
# Your code doesn't change. The plugin routes the Intent.
```

!!! example "Cluster: distributed Intents"
    ```python
    # Node 1 handles orders
    CREATE_ORDER = Intent(name="create_order", level=Level.STANDARD)
    
    # Node 2 handles inventory
    UPDATE_STOCK = Intent(name="update_stock", level=Level.STANDARD)
    
    # When Node 1 publishes "update_stock":
    # 1. Local bus checks for subscribers on Node 1 — none found
    # 2. ClusterBridge forwards to Node 2 via WebSocket
    # 3. Node 2's bus delivers to the inventory handler
    # 4. Result comes back to Node 1
    
    # Your code: await publish(update_intent, source="orders")
    # The cluster plugin handles routing. You don't know if it's local or remote.
    ```

## Next: Inventory Service

Let's build the inventory service — [Inventory Service](inventory-service.md).
