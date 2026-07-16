---
title: 'Native IOP'
description: 'Full control with explicit Intent management. No sugar — just the IOP model.'
---

# Native IOP

Full control with explicit Intent management. No sugar — just the IOP model.

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

Group related Intents:

```python
from evoid.web.iop_style import create_service, on, run

service = create_service("user-service")

GET_USER = Intent(name="get_user", level=Level.STANDARD)
CREATE_USER = Intent(name="create_user", level=Level.STANDARD)

async def handle_get(intent: Intent) -> dict:
    return {"id": 1}

async def handle_create(intent: Intent) -> dict:
    return {"status": "created"}

on(service, GET_USER, handle_get)
on(service, CREATE_USER, handle_create)

await run(service, port=8000)
```

## Custom Pipelines

Define exactly which processors run:

```python
from evoid import Intent, Level
from evoid.core.extend import add_intent_with_pipeline

PAYMENT = Intent(name="process_payment", level=Level.CRITICAL)

async def handle_payment(intent: Intent) -> dict:
    return {"status": "paid"}

add_intent_with_pipeline(
    PAYMENT,
    processors=["validate", "check_fraud", "charge", "audit"],
    handler=handle_payment,
)
```

## Inter-Service Communication

```python
from evoid import Intent, Level, subscribe, publish

# Subscribe
async def on_payment(intent: Intent) -> dict:
    return {"processed": True}

subscribe("process_payment", on_payment)

# Publish
intent = Intent(
    name="process_payment",
    level=Level.CRITICAL,
    metadata={"amount": 99.99},
)
results = await publish(intent)
```

## Execute by Name

```python
from evoid import execute_by_name

result = await execute_by_name("get_user", id=42)
print(result.value)
```

## When to Use Native IOP

- Complex inter-service communication
- Custom processor chains
- Systems where the IOP model is the primary design
- Full control over Intent lifecycle

## Comparison

| Feature | @route | @controller | Native |
|---------|--------|-------------|--------|
| Syntax sugar | Most | Medium | None |
| Intent control | Implicit | Implicit | Explicit |
| Pipeline control | Via extend | Via extend | Direct |
| Best for | Small APIs | Large APIs | Complex systems |
