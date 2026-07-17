---
title: 'Architecture'
description: 'How EVOID works under the hood — Intent, Pipeline, Processor, Context.'
---

# Architecture

How EVOID works under the hood.

## The Flow

Every request follows this path:

```
User Code (@route / @controller / native)
        |
        v
   Intent (frozen dataclass)
        |
        v
   Resolver (Intent -> PipelineConfig)
        |
        v
   Pipeline (tuple of processor names)
        |
        v
   Processor 1 -> Processor 2 -> ... -> Processor N
        |
        v
   Result (success, value, error, duration)
```

## Core Components

### Intent

A frozen dataclass that declares **what** you want to achieve.

```python
from evoid import Intent, Level

intent = Intent(
    name="get_user",
    level=Level.STANDARD,
    metadata={"user_id": 42},
)
```

Intent is **pure data**. It never decides anything. The runtime reads it and decides what to do.

### Pipeline

A tuple of processor names executed in order.

```python
# Default pipelines by level
ephemeral -> ("validate",)
standard  -> ("validate", "authorize")
critical  -> ("validate", "authorize", "audit", "protect")
```

Pipelines are resolved at execution time, not definition time. This means you can change infrastructure without changing business logic.

### Processor

A function that receives a `Context` and returns a result.

```python
async def validate(ctx: Context) -> dict:
    data = ctx.state.get("data")
    if not data:
        raise ValueError("No data")
    ctx.state["validated"] = True
    return {"valid": True}
```

Processors are **independent Lego blocks**. Each one does one thing. The pipeline composes them.

### Context

A mutable databag that flows through the pipeline.

```python
@dataclass
class Context:
    intent: Intent          # What we're doing
    state: dict             # Shared state between processors
    deps: dict              # Injected dependencies
    metadata: dict          # Request metadata
    errors: list            # Accumulated errors
    id: str                 # Unique ID
```

Context is the **only shared state** between processors. Processors communicate through `ctx.state`.

## Extension Points

### Pipeline Extension

Inject processors without modifying handlers:

```python
from evoid.core.extend import before, after

before("GET:/users/{id}", "rate_limit")
after("GET:/users/{id}", "audit_log")
```

### Message Bus

Services communicate through Intents, not HTTP:

```python
from evoid import subscribe, publish

subscribe("order_created", handle_order)
await publish(order_intent)
```

### Pluggable Engines

Every engine is replaceable:

```python
from evoid.engines.serializer import set_serializer
from evoid.engines.schema import set_validator

set_serializer(MySerializer())
set_validator(MyValidator())
```

## Design Principles

1. **Data carries intent** — Intent is a frozen dataclass, not a class with methods
2. **Pipeline is composition** — Processors are pure functions composed together
3. **No stateful objects** — Registries are dicts, not singleton classes
4. **Extensibility without inheritance** — Use `before/after/replace` to modify pipelines
5. **Zero overhead IOP** — Fast path skips inspection and timeout when not needed

## Related

- [Intent](../learn/intent.md) — Deep dive into Intents
- [Pipeline](../learn/pipeline.md) — How execution works
- [Processors](../learn/processors.md) — Functions that handle intents
