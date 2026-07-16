---
title: 'Inter-Service Communication'
description: 'Services communicate through the message bus using Intents, not HTTP.'
---

# Inter-Service Communication

Services communicate through the message bus using Intents, not HTTP.

## The Problem

!!! info "Why not HTTP?"
    Service A needs to notify Service B when something happens. Using HTTP adds network overhead, serialization cost, and failure points.

## The Solution

The message bus routes Intents directly between services on the same system.

## Publishing and Subscribing

```python
from evoid import Intent, Level, subscribe, publish

# Service A subscribes to "order_created"
async def on_order_created(intent: Intent) -> None:
    order_id = intent.metadata.get("order_id")
    print(f"Processing order {order_id}")

subscribe("order_created", on_order_created)

# Service B publishes an event
order_intent = Intent(
    name="order_created",
    level=Level.STANDARD,
    metadata={"order_id": 42, "total": 99.99},
)

results = await publish(order_intent, source="checkout-service")
```

## Topic Matching

The bus matches by intent name, level, or wildcard:

```python
# Exact match
subscribe("process_payment", handler)

# Level match — receives all CRITICAL intents
subscribe("critical", handler)

# Wildcard — receives everything
subscribe("*", handler)
```

## Multiple Subscribers

Multiple handlers can subscribe to the same topic:

```python
async def send_email(intent: Intent) -> None:
    print("Sending email...")

async def update_inventory(intent: Intent) -> None:
    print("Updating inventory...")

subscribe("order_created", send_email)
subscribe("order_created", update_inventory)

# Both run concurrently when "order_created" is published
```

## Service Model

Group related handlers into a Service:

```python
from evoid.web.iop_style import create_service, on, run
from evoid import Intent, Level

service = create_service("order-service")

ORDER_INTENT = Intent(name="create_order", level=Level.CRITICAL)

async def handle_order(intent: Intent) -> dict:
    # Process order...
    return {"status": "created", "order_id": 123}

on(service, ORDER_INTENT, handle_order)

await run(service, port=8001)
```

## Calling Other Services

```python
from evoid import Intent, Level
from evoid.core.service import call, emit

# Synchronous call (waits for response)
result = await call(service, Intent(
    name="get_user",
    level=Level.STANDARD,
    metadata={"user_id": 42},
))

# Fire-and-forget (async, no waiting)
await emit(service, Intent(
    name="send_notification",
    level=Level.EPHEMERAL,
    metadata={"message": "Order shipped"},
))
```

## Message History

!!! tip "Debugging"
    Use `get_history()` to trace message flow between services:

```python
from evoid.core.message_bus import get_history

history = get_history()
for msg in history:
    print(f"{msg.source} → {msg.intent.name}")
```
