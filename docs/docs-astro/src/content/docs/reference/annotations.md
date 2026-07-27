---
title: 'Annotations'
description: 'Declare intent metadata, dependencies, validation, and rate limits on handlers.'
---

# Annotations

Annotations attach metadata to handlers. The runtime reads it. No magic, no metaclasses.

## Available Annotations

| Annotation | Purpose |
|-----------|---------|
| `@intent` | Set pipeline, timeout, priority |
| `@requires` | Declare required dependencies |
| `@validates` | Input validation schema |
| `@rate_limit` | Rate limiting config |
| `@body` | Request body declaration |
| `@params` | Path/query parameter declaration |
| `@headers` | Header requirements |

## @intent

Declare pipeline, timeout, and priority on a handler.

```python
from evoid.core.annotations import intent

@intent(pipeline=("validate", "authorize", "GET:/pay"), timeout=30)
@get("/pay")
async def process_payment(ctx):
    return {"paid": True}
```

**Critical rule**: the last element in `pipeline` must be the **intent name** (e.g. `"GET:/pay"`), not the Python function name. When you use `@get`, `@post`, etc., the handler registers under the intent name, not `fn.__name__`.

```python
# CORRECT: intent name in pipeline
@intent(pipeline=("validate", "GET:/users"))
@get("/users")
async def list_users(ctx): ...

# WRONG: function name in pipeline (handler won't run)
@intent(pipeline=("validate", "list_users"))
@get("/users")
async def list_users(ctx): ...
```

### Without Route Decorators

When using native IOP (no `@get`/`@post`), the pipeline uses the Intent name directly:

```python
from evoid import Intent, Level, add_intent

@intent(pipeline=("validate", "pay"))
async def pay(ctx): ...

PAY = Intent(name="pay", level=Level.CRITICAL)
add_intent(PAY, pay)
```

## @requires

Declare required dependencies. Checked at registration time.

```python
from evoid.core.annotations import requires

@requires("auth_engine", "db_connection")
async def get_user(ctx):
    auth = ctx.deps["auth_engine"]
    db = ctx.deps["db_connection"]
    return await db.read("user:1")
```

## @validates

Declare input validation schema.

```python
from evoid.core.annotations import validates

@validates({"amount": {"type": "number", "required": True}})
async def process_payment(ctx):
    amount = ctx.metadata["body"]["amount"]
    return {"paid": amount}
```

## @rate_limit

Declare rate limiting.

```python
from evoid.core.annotations import rate_limit

@rate_limit(max_calls=100, period=60)
async def api_call(ctx):
    return {"ok": True}
```

## @body and @params

Declare input expectations for route handlers.

```python
from evoid.core.annotations import body, params

@body(fields={"name": {"type": "string", "required": True}})
@post("/users")
async def create_user(ctx): ...

@params(fields=["id"])
@get("/users/{id}")
async def get_user(ctx): ...
```

## How Annotations Flow

1. Decorator attaches metadata to the function (`fn._evoid_intent`, etc.)
2. Route decorator (`@get`, `@post`) calls `apply_annotations()` to read metadata
3. `validate_annotations()` checks for errors (e.g. intent name missing from pipeline)
4. Metadata is used to configure the Intent and pipeline

## Related

- [Intent](../learn/intent.md): the data that annotations configure
- [Pipeline](../learn/pipeline.md): how annotations affect execution
- [IOP Levels](../learn/iop-levels.md): level determines default pipeline
