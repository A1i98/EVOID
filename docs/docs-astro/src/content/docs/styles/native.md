---
title: 'Native IOP Style'
description: 'Direct Intent system. No sugar. Full control over the IOP model.'
---

# Native IOP Style

Direct Intent system. No sugar. Full control over the IOP model.

This is the purest form of EVOID. You create Intents explicitly, register handlers, and compose pipelines.

## Basic Usage

```python
from evoid import Intent, Level, add_intent

# Define an Intent
GET_USER = Intent(
    name="get_user",
    level=Level.STANDARD,
    metadata={"method": "GET", "path": "/users/{id}"},
)

# Write the handler
async def handle_get_user(intent: Intent) -> dict:
    user_id = intent.metadata.get("id", 1)
    return {"id": user_id, "name": "Alice"}

# Register
add_intent(GET_USER, handle_get_user)
```

## Service Model

Group related Intents into a Service:

```python
from evoid.native import create_service, on, run

# Create service
service = create_service("user-service")

# Define Intents
GET_USER = Intent(name="get_user", level=Level.STANDARD)
CREATE_USER = Intent(name="create_user", level=Level.STANDARD)
DELETE_USER = Intent(name="delete_user", level=Level.CRITICAL)

# Register handlers
async def handle_get(intent: Intent) -> dict:
    return {"id": 1, "name": "Alice"}

async def handle_create(intent: Intent) -> dict:
    return {"status": "created"}

async def handle_delete(intent: Intent) -> dict:
    return {"status": "deleted"}

on(service, GET_USER, handle_get)
on(service, CREATE_USER, handle_create)
on(service, DELETE_USER, handle_delete)

# Run
await run(service, host="0.0.0.0", port=8000)
```

## Custom Pipelines

Define exactly which processors run for each Intent:

```python
from evoid import Intent, Level
from evoid.core.extend import add_intent_with_pipeline

PAYMENT = Intent(name="process_payment", level=Level.CRITICAL)

async def handle_payment(intent: Intent) -> dict:
    amount = intent.metadata.get("amount", 0)
    return {"status": "paid", "amount": amount}

add_intent_with_pipeline(
    PAYMENT,
    processors=["validate", "check_fraud", "charge", "audit", "notify"],
    handler=handle_payment,
)
```

## Inter-Service Communication

Services communicate through Intents, not HTTP:

```python
from evoid import Intent, Level
from evoid.core.message_bus import subscribe, publish

# Service A subscribes
async def on_payment(intent: Intent) -> dict:
    print(f"Payment received: {intent.metadata}")
    return {"processed": True}

subscribe("process_payment", on_payment)

# Service B publishes
payment_intent = Intent(
    name="process_payment",
    level=Level.CRITICAL,
    metadata={"amount": 99.99, "currency": "USD"},
)

results = await publish(payment_intent, source="checkout-service")
```

## Intent Levels and Behavior

```python
from evoid import Intent, Level

# EPHEMERAL — fast, no persistence
CACHE_CHECK = Intent(name="cache_check", level=Level.EPHEMERAL)

# STANDARD — balanced
GET_USER = Intent(name="get_user", level=Level.STANDARD)

# CRITICAL — full protection
PROCESS_PAYMENT = Intent(name="process_payment", level=Level.CRITICAL)
```

The level determines the default pipeline:

| Level | Pipeline | Timeout |
|-------|----------|---------|
| `ephemeral` | `validate` | 5s |
| `standard` | `validate`, `authorize` | 10s |
| `critical` | `validate`, `authorize`, `audit`, `protect` | 30s |

## Executing by Name

```python
from evoid import execute_by_name

# Execute a registered intent by name
result = await execute_by_name("get_user", id=42)

if result.success:
    print(result.value)
```

## When to Use

- Full control over Intent lifecycle
- Complex inter-service communication
- Custom processor chains
- Systems where the IOP model is the primary design driver
