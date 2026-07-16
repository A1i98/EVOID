---
title: 'Intent Levels'
description: 'Every Intent has a level that determines its protection and processing pipeline.'
---

# Intent Levels

Every Intent has a level that determines its protection and processing pipeline.

## Three Levels

| Level | Description | Pipeline | Timeout |
|-------|-------------|----------|---------|
| `ephemeral` | Temporary, can be lost | `validate` | 5s |
| `standard` | Normal business data | `validate`, `authorize` | 10s |
| `critical` | Must never be lost | `validate`, `authorize`, `audit`, `protect` | 30s |

## Usage

```python
from evoid.web.route import Service, get, post

app = Service("api")

@get("/cache-data", level="ephemeral")
async def cache_data() -> dict:
    return {"cached": True}

@get("/users/{id}", level="standard")
async def get_user(id: int) -> dict:
    return {"id": id}

@post("/payments", level="critical")
async def process_payment(amount: float) -> dict:
    return {"status": "paid", "amount": amount}
```

## What Each Level Means

!!! warning "Choosing the right level"
    Pick the level that matches your data's criticality. Overusing `critical` adds unnecessary overhead.

### Ephemeral

- Fast path, minimal processing
- Memory-only caching, aggressive TTL
- No audit, no encryption
- Use for: cache checks, temporary data, session lookups

### Standard

- Balanced processing
- Authorization check
- Memory + disk caching
- Use for: user profiles, posts, comments, general CRUD

### Critical

- Full protection pipeline
- Authorization + audit + protection
- Strong consistency, encryption, replication
- Use for: payments, medical records, legal documents, authentication

## Custom Pipelines Per Level

Override the default pipeline for any level:

```python
from evoid import Intent, Level
from evoid.core.extend import add_intent_with_pipeline

# Custom critical pipeline
PAYMENT = Intent(name="process_payment", level=Level.CRITICAL)

async def handle_payment(intent: Intent) -> dict:
    return {"status": "paid"}

add_intent_with_pipeline(
    PAYMENT,
    processors=["validate", "check_fraud", "charge", "audit", "notify"],
    handler=handle_payment,
)
```

## Runtime Behavior

The level affects how the runtime treats the Intent:

```python
from evoid import Intent, Level

# Create intents with different levels
ephemeral = Intent(name="cache_check", level=Level.EPHEMERAL)
standard = Intent(name="get_user", level=Level.STANDARD)
critical = Intent(name="process_payment", level=Level.CRITICAL)

# Each gets a different default pipeline and timeout
```
