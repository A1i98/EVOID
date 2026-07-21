---
title: 'Middleware'
description: 'Rate limiting, logging, timing — cross-cutting concerns as pipeline processors.'
---

# Middleware

Rate limiting, logging, timing — cross-cutting concerns as pipeline processors.

## The Problem

Every endpoint needs logging, rate limiting, timing. Copy-pasting into each handler violates DRY.

## The Solution: Pipeline Processors

```python
from evoid import register_processor
from evoid.core import Context
from evoid.core.extend import before, after

# Rate limiter
_calls: dict[str, list] = {}

async def rate_limit(intent: Intent, ctx: Context) -> dict:
    name = intent.name
    import time
    now = time.time()
    window = 60
    max_calls = 100

    _calls.setdefault(name, [])
    _calls[name] = [t for t in _calls[name] if now - t < window]

    if len(_calls[name]) >= max_calls:
        raise Exception(f"Rate limit exceeded for {name}")

    _calls[name].append(now)
    return {"rate_limited": False}

# Logger
async def log_request(intent: Intent, ctx: Context) -> dict:
    print(f"[{intent.name}] started")
    ctx.state["log_start"] = __import__("time").monotonic()
    return {"logged": True}

async def log_response(intent: Intent, ctx: Context) -> dict:
    start = ctx.state.get("log_start", 0)
    elapsed = __import__("time").monotonic() - start
    print(f"[{intent.name}] completed in {elapsed:.3f}s")
    return {"elapsed": elapsed}

register_processor("rate_limit", rate_limit)
register_processor("log_request", log_request)
register_processor("log_response", log_response)
```

## Attach to Routes

```python
# Apply to specific routes
before("GET:/menu", "rate_limit")
before("POST:/orders", "rate_limit")
after("GET:/menu", "log_response")
after("POST:/orders", "log_response")

# Apply to all routes with a pattern
for route in ["GET:/menu", "POST:/orders", "GET:/orders"]:
    before(route, "log_request")
```

## Apply Globally

```python
from evoid.core.extend import before

# Apply to specific intents
before("GET:/menu", "rate_limit")
before("POST:/orders", "rate_limit")
before("GET:/menu", "log_request")
before("POST:/orders", "log_request")
```

## Insert Relative to Processors

```python
from evoid.core.extend import before_processor, after_processor

# Add auth check before validation
before_processor("POST:/orders", "validate", "check_auth")

# Add audit after authorization
after_processor("POST:/orders", "authorize", "audit_log")
```

## Replace Entire Pipeline

```python
from evoid.core.extend import replace_pipeline

# For health checks — skip everything
replace_pipeline("GET:/health", ["handle_health"])
```

## What You Learned

| Concept | What It Is |
|---------|-----------|
| `before()` / `after()` | Inject at pipeline start/end |
| `before_processor()` / `after_processor()` | Insert relative to specific steps |
| `replace_pipeline()` | Swap the entire chain |
| Cross-cutting concerns | Logging, rate limiting, timing as processors |

## Next: Status Codes

Let's handle HTTP status codes — [Status Codes](status-codes.md).
