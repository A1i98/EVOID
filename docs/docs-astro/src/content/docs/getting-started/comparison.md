---
title: 'EVOID vs Others'
description: 'How EVOID compares to FastAPI, Flask, and other frameworks.'
---

# EVOID vs Others

How EVOID compares to traditional frameworks.

## The Core Difference

| Framework | Paradigm | Data Flow |
|-----------|----------|-----------|
| **FastAPI** | OOP + FP | Request -> Response |
| **Flask** | FP | Request -> Response |
| **Django** | OOP | Request -> Response |
| **EVOID** | IOP | Intent -> Pipeline -> Result |

Traditional frameworks ask: **"How do I handle this request?"**

EVOID asks: **"What does this data want?"**

## Feature Comparison

| Feature | FastAPI | Flask | EVOID |
|---------|---------|-------|-------|
| Performance | High | Medium | High |
| Type Safety | Pydantic | None | Pluggable |
| Validation | Decorator-based | Manual | Pipeline-based |
| Middleware | ASGI middleware | WSGI middleware | Processor pipeline |
| Inter-service | HTTP/gRPC | HTTP | Direct function call |
| Infrastructure | Per-endpoint | Per-endpoint | Per-Intent level |
| Extensibility | Dependencies | Blueprints | Pipeline extension |
| Learning Curve | Medium | Low | Low-Medium |

## When to Use What

### Use FastAPI when

- Building a standard REST API
- You need auto-generated OpenAPI docs
- Team is familiar with Pydantic
- Simple request/response patterns

### Use Flask when

- Building a simple web app
- You need maximum flexibility
- Minimal overhead is critical
- Traditional WSGI deployment

### Use EVOID when

- Multiple services need to communicate
- Infrastructure varies by data criticality
- You want pipeline-based extensibility
- IOP paradigm fits your domain

## EVOID + FastAPI

EVOID complements FastAPI. Use both:

```python
# External: FastAPI handles HTTP
from fastapi import FastAPI
from evoid.core.service import call

app = FastAPI()

@app.post("/game/send-message")
async def send_message(player: str, message: str):
    # FastAPI receives HTTP
    # EVOID handles internal communication
    intent = Intent(name="send_message", metadata={"player": player, "message": message})
    result = await call(chat_service, intent)
    return result
```

This gives you:

- **FastAPI** for external HTTP endpoints
- **EVOID** for internal service communication
- **Unified engines** for validation, serialization, caching

## Performance

EVOID pipeline execution is optimized with three code paths:

1. **Fast path** — No inspection, no timeout (default)
2. **Timeout path** — Adds timeout checking
3. **Inspect path** — Full state snapshots

Benchmark: 10K ops/s on a 5-processor pipeline.

## Migration from FastAPI

### Step 1: Keep FastAPI for HTTP

```python
from fastapi import FastAPI
app = FastAPI()
```

### Step 2: Add EVOID for internal logic

```python
from evoid import Intent, Level, add_intent

PROCESS_ORDER = Intent(name="process_order", level=Level.CRITICAL)

async def handle_order(intent: Intent) -> dict:
    # Your business logic
    return {"status": "processed"}

add_intent(PROCESS_ORDER, handle_order)
```

### Step 3: Gradually move endpoints

```python
@app.post("/orders")
async def create_order(amount: float):
    intent = Intent(name="process_order", metadata={"amount": amount})
    result = await execute(intent)
    return result.value
```

## Related

- [What is IOP?](what-is-iop.md) — Understanding the paradigm
- [Why EVOID?](why-evoid.md) — The motivation
- [Architecture](architecture.md) — How it works
