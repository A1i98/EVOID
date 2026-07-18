---
title: 'Troubleshooting'
description: 'Common errors and how to fix them. When you are stuck, start here.'
---

# Troubleshooting

Common errors and how to fix them. When you are stuck, start here.

## Import Errors

### `cannot import name 'X' from 'evoid'`

Wrong import path. EVOID has multiple modules:

```python
# ❌ Wrong
from evoid import Service

# ✅ Correct — web route syntax
from evoid.web.route import Service

# ✅ Correct — native syntax
from evoid.native import create_service

# ✅ Correct — core components
from evoid import Intent, Level, execute
from evoid.core import Context
```

### `No module named 'evoid'`

EVOID is not installed:

```bash
pip install evoid
# or
uv add evoid
```

## Handler Not Called

### My handler never runs

The Intent is not registered or the processor is not wired:

```python
from evoid import Intent, Level, register, register_processor, execute

# 1. Define Intent
GET_USER = Intent(name="get_user", level=Level.STANDARD)

# 2. Define handler
async def handle_get_user(intent: Intent) -> dict:
    return {"id": 1}

# 3. Register BOTH — Intent AND processor
register(GET_USER)  # ← Don't forget this
register_processor("get_user", handle_get_user)  # ← Don't forget this

# 4. Execute
result = await execute(GET_USER)
```

### @route handler not called

Check the URL pattern matches:

```python
@get("/users/{user_id}")
async def get_user(user_id: int) -> dict:
    return {"id": user_id}
```

```bash
# ✅ Correct
curl http://localhost:8000/users/42

# ❌ Wrong — missing /users/
curl http://localhost:8000/42

# ❌ Wrong — trailing slash
curl http://localhost:8000/users/42/
```

## Pipeline Errors

### `Processor 'X' not found`

The processor is not registered:

```python
from evoid import register_processor

async def my_processor(ctx: Context) -> dict:
    return {"ok": True}

# Register BEFORE using in pipeline
register_processor("my_processor", my_processor)
```

### Pipeline runs but handler result is `None`

The last processor's return value becomes `Result.value`. Make sure your handler returns something:

```python
# ❌ Returns None
async def handle_order(intent: Intent) -> None:
    print("order processed")

# ✅ Returns data
async def handle_order(intent: Intent) -> dict:
    print("order processed")
    return {"status": "confirmed"}
```

## Validation Errors

### Pydantic validation fails silently

Check if the adapter is configured for schema validation:

```python
from evoid.core.runtime import Config

config = Config(
    name="my-api",
    engines={"schema": "native"},  # Enable validation
)
```

### Body parameters not extracted

For `@post`, parameters come from the request body, not the URL:

```python
# ❌ Wrong — sandwich is not in the URL
@post("/orders")
async def create_order(sandwich: str) -> dict:
    return {"sandwich": sandwich}

# Request: POST /orders  (no sandwich in URL)
# sandwich will be None

# ✅ Correct — send as JSON body
# curl -X POST http://localhost:8000/orders \
#   -H "Content-Type: application/json" \
#   -d '{"sandwich": "BLT"}'
```

## Context Issues

### `ctx` is not available in @route handler

`@route` handlers don't receive `ctx`. The framework extracts params automatically:

```python
# @route style — no ctx, params extracted
@get("/users/{user_id}")
async def get_user(user_id: int) -> dict:
    # user_id is extracted from URL
    return {"id": user_id}

# Native style — full control with ctx
async def handle_get_user(intent: Intent, ctx: Context) -> dict:
    user_id = intent.metadata.get("user_id")
    return {"id": user_id}
```

### `ctx.deps` is empty

Dependencies are injected by processors. Make sure a processor writes to `ctx.deps`:

```python
async def inject_db(ctx: Context) -> dict:
    ctx.deps["db"] = create_session()
    return {"db_ready": True}

# Wire it to the pipeline
from evoid.core.extend import before
before("GET:/users/{id}", "inject_db")
```

## Async Issues

### `object dict can't be used in 'await' expression`

Your handler is not async:

```python
# ❌ Wrong — sync function
def handle_order(intent: Intent) -> dict:
    return {"status": "ok"}

# ✅ Correct — async function
async def handle_order(intent: Intent) -> dict:
    return {"status": "ok"}
```

### `RuntimeWarning: coroutine was never awaited`

You called an async function without `await`:

```python
# ❌ Wrong
result = execute(intent)

# ✅ Correct
result = await execute(intent)
```

## Still Stuck?

1. Check the [FAQ](faq.md) for common questions
2. Read the [Error Handling](../tutorial/error-handling.md) tutorial
3. Open an issue on [GitHub](https://github.com/EvolveBeyond/EVOID/issues)
