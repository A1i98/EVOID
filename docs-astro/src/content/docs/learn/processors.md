---
title: 'Processors'
description: 'A processor is a function that receives a `Context` and returns a result. Processors are independent Lego blocks — each one does one thing, and the pipeline ...'
---

# Processors

A processor is a function that receives a `Context` and returns a result. Processors are independent Lego blocks — each one does one thing, and the pipeline composes them.

!!! note "Single responsibility"
    Each processor should do exactly one thing. If you need multiple operations, chain them in the pipeline — don't put them in one processor.

## What Is a Processor?

```python
from evoid.core import Context

async def my_processor(ctx: Context) -> dict:
    # Read what you need from context
    data = ctx.state.get("data")

    # Do your work
    result = transform(data)

    # Write results back
    ctx.state["output"] = result

    return {"status": "ok"}
```

That's it. A processor is a function with type `Callable[[Context], Awaitable[Any]]`. No class, no protocol, no inheritance.

## Registering Processors

### Manual Registration

```python
from evoid import register_processor

async def log_request(ctx: Context) -> dict:
    print(f"[{ctx.intent.name}] started")
    return {"logged": True}

register_processor("log_request", log_request)
```

### Auto-Registration via Decorators

The `@get`, `@post`, `@Controller`, and native `on()` all register processors automatically:

```python
# @route style — processor registered as "GET:/users/{id}"
@get("/users/{id}")
async def get_user(id: int) -> dict:
    return {"id": id}

# Native style — processor registered as "my_intent"
on(service, MY_INTENT, handler)
```

### Built-in Processors

EVOID ships with several processors in `evoid/processors/`:

| Processor | Purpose |
|-----------|---------|
| `intent_extractor` | Extracts intent metadata into `ctx.state` |
| `schema_validator` | Validates data against a schema (if engine configured) |
| `auth_checker` | Checks authorization (if auth engine configured) |
| `rate_limiter` | Rate limits by intent priority |
| `circuit_breaker` | Circuit breaker pattern for failing services |
| `logger_processor` | Logs intent execution |

## Writing Processors

### Pattern: Read-Process-Write

```python
async def enrich_data(ctx: Context) -> dict:
    # READ from state
    user_id = ctx.state.get("user_id")

    # PROCESS (fetch from database)
    user = await db.get_user(user_id)

    # WRITE back to state
    ctx.state["user"] = user

    return {"enriched": True}
```

### Pattern: Conditional Logic

Processors can branch based on Intent level:

```python
async def adaptive_processor(ctx: Context) -> dict:
    if ctx.intent.level == Level.CRITICAL:
        # Strong consistency, full audit
        ctx.state["consistency"] = "strong"
        ctx.state["audit"] = True
    elif ctx.intent.level == Level.EPHEMERAL:
        # Fast path, skip extras
        ctx.state["cache_only"] = True
    else:
        # Balanced
        ctx.state["consistency"] = "eventual"

    return {"adapted": True}
```

### Pattern: Error Accumulation

Non-critical errors can be collected instead of failing the pipeline:

```python
async def validate_optional(ctx: Context) -> dict:
    try:
        validate(ctx.state.get("data"))
    except ValidationError as e:
        ctx.errors.append(e)
        # Don't raise — pipeline continues

    return {"validated": True, "warnings": len(ctx.errors)}
```

## Processor Composition

Processors are composed by the pipeline. Each processor runs in order, and the next processor sees the state the previous one wrote.

```
validate → authorize → enrich → save → notify
   ↓           ↓          ↓        ↓        ↓
ctx.state accumulates results across all steps
```

The last processor's return value becomes `Result.value`.

## Best Practices

- **One responsibility** — Each processor does one thing
- **Pure functions** — Avoid side effects outside `ctx`
- **No hard dependencies** — Check `ctx.deps` before using engines
- **Meaningful names** — `validate_input`, not `step1`
- **Idempotent when possible** — Re-running should not corrupt state
