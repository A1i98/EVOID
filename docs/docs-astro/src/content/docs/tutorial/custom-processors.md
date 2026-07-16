---
title: 'Custom Processors'
description: 'Write your own processors and inject them into any pipeline.'
---

# Custom Processors

Write your own processors and inject them into any pipeline.

## What Is a Processor?

A processor is an async function that receives a `Context` and returns a result:

```python
from evoid.core import Context

async def my_processor(ctx: Context) -> dict:
    # Read from state
    user_id = ctx.state.get("user_id")

    # Do something
    result = await some_operation(user_id)

    # Write back to state
    ctx.state["result"] = result

    return {"processed": True}
```

## Registering a Processor

```python
from evoid import register_processor

async def timing(ctx: Context) -> dict:
    import time
    ctx.state["start_time"] = time.monotonic()
    return {"timing_started": True}

register_processor("timing", timing)
```

Now `"timing"` is available in any pipeline.

## Using in Pipelines

```python
from evoid.core.extend import before

# Add timing to any route
before("GET:/users/{id}", "timing")

# Or replace the entire pipeline
from evoid.core.extend import replace_pipeline
replace_pipeline("GET:/users/{id}", ["timing", "validate", "fetch"])
```

## Practical Examples

### Request Logger

```python
async def log_request(ctx: Context) -> dict:
    intent = ctx.intent
    print(f"[{intent.name}] started at {ctx.created_at}")
    ctx.state["request_logged"] = True
    return {"logged": True}

register_processor("log_request", log_request)
```

### Data Enricher

```python
async def enrich_data(ctx: Context) -> dict:
    user_id = ctx.state.get("user_id")
    if user_id:
        user = await db.get_user(user_id)
        ctx.state["user"] = user
        ctx.state["user_role"] = user.get("role", "viewer")
    return {"enriched": True}

register_processor("enrich_data", enrich_data)
```

### Rate Limiter

```python
from collections import defaultdict
from time import time

_calls: dict[str, list[float]] = defaultdict(list)

async def rate_limit(ctx: Context) -> dict:
    intent_name = ctx.intent.name
    now = time()
    window = 60  # 1 minute
    max_calls = 100

    # Clean old entries
    _calls[intent_name] = [t for t in _calls[intent_name] if now - t < window]

    if len(_calls[intent_name]) >= max_calls:
        raise Exception(f"Rate limit exceeded for {intent_name}")

    _calls[intent_name].append(now)
    return {"rate_limited": False}

register_processor("rate_limit", rate_limit)
```

### Circuit Breaker

```python
from time import time

_failures: dict[str, int] = {}
_last_failure: dict[str, float] = {}
_THRESHOLD = 3
_RESET_TIME = 30  # seconds

async def circuit_breaker(ctx: Context) -> dict:
    name = ctx.intent.name
    now = time()

    # Check if circuit is open
    if name in _failures and _failures[name] >= _THRESHOLD:
        if now - _last_failure.get(name, 0) < _RESET_TIME:
            raise Exception(f"Circuit breaker open for {name}")
        # Reset after cooldown
        _failures[name] = 0

    return {"circuit_closed": True}

register_processor("circuit_breaker", circuit_breaker)
```

## Error Handling in Processors

Non-critical errors can be collected instead of failing the pipeline:

```python
async def validate_optional(ctx: Context) -> dict:
    try:
        validate(ctx.state.get("data"))
    except ValidationError as e:
        ctx.errors.append(e)
        # Pipeline continues

    return {"validated": True, "warnings": len(ctx.errors)}
```
