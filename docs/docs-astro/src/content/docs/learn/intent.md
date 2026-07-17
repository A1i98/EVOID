---
title: 'Intent'
description: 'An Intent is a frozen dataclass that declares what you want to achieve. It is pure data — the runtime reads it and decides what to do.'
---

# Intent

An **Intent** is a frozen dataclass that declares what you want to achieve. It is pure data — the runtime reads it and decides what to do.

!!! info "Key concept"
    Intents are immutable. Once created, they cannot be changed. This guarantees thread safety and predictable pipeline behavior.

## Structure

```python
from evoid import Intent, Level

MY_INTENT = Intent(
    name="get_user",
    level=Level.STANDARD,
    metadata={"method": "GET", "path": "/users/{id}"},
    timeout=10.0,
    priority=0,
)
```

| Field | Type | Default | Purpose |
|-------|------|---------|---------|
| `name` | `str` | required | Unique identifier |
| `level` | `Level` | `STANDARD` | Protection level |
| `metadata` | `dict` | `{}` | Arbitrary data for processors |
| `timeout` | `float \| None` | `None` | Max seconds before timeout |
| `priority` | `int` | `0` | Execution order (higher first) |

## Intent Levels

| Level | Pipeline | Timeout | Use Case |
|-------|----------|---------|----------|
| `ephemeral` | `validate` | 5s | Cache, sessions, temp data |
| `standard` | `validate`, `authorize` | 10s | User profiles, posts, comments |
| `critical` | `validate`, `authorize`, `audit`, `protect` | 30s | Payments, medical, legal |

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

## Creating Intents

### Explicit (Native Style)

```python
from evoid import Intent, Level, add_intent

PAYMENT = Intent(
    name="process_payment",
    level=Level.CRITICAL,
    metadata={"currency": "USD"},
)

async def handle_payment(intent: Intent) -> dict:
    return {"status": "processed"}

add_intent(PAYMENT, handle_payment)
```

### Implicit (@route Style)

```python
from evoid.web.route import Service, get

app = Service("my-api")

@get("/users/{user_id}", level="critical")
async def get_user(user_id: int) -> dict:
    return {"id": user_id}
```

The decorator creates:

- `name`: `GET:/users/{user_id}`
- `level`: `Level.CRITICAL`
- `metadata`: `{"method": "GET", "path": "/users/{user_id}"}`

### Implicit (@controller Style)

```python
from evoid.web.controller import Service, Controller, GET

app = Service("my-api")

@Controller("/users")
class UserController:
    @GET("/{user_id}", level="critical")
    async def get_user(self, user_id: int) -> dict:
        return {"id": user_id}
```

## Intent Metadata

Metadata passes data to processors:

```python
INTENT = Intent(
    name="send_email",
    level=Level.STANDARD,
    metadata={
        "priority": "high",
        "retry": 3,
        "timeout": 30,
        "template": "welcome",
    },
)

async def handle(intent: Intent) -> dict:
    priority = intent.metadata.get("priority", "normal")
    retries = intent.metadata.get("retry", 1)
    return {"sent": True, "priority": priority}
```

## Lifecycle

```
Declaration (you create Intent)
    |
Registration (intent stored in registry)
    |
Resolution (runtime maps intent to PipelineConfig)
    |
Execution (pipeline runs processors in order)
    |
Result (success/failure with value and timing)
```

## Inspecting Registered Intents

```python
from evoid import all_intents

intents = all_intents()
for name, intent in intents.items():
    print(f"{name} [{intent.level.value}]")
```

## Best Practices

- **Use meaningful names** — `get_user` over `handler1`
- **Choose appropriate levels** — Marking everything `critical` defeats the purpose
- **Include useful metadata** — Processors use it for decisions
- **Keep Intents focused** — One intent, one responsibility
- **Set timeouts** — Prevent runaway processors

## Related

- [Pipeline](pipeline.md) — How intents become pipelines
- [Processors](processors.md) — Functions that handle intents
