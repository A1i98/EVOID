---
title: 'Handling Errors'
description: 'Handle errors in handlers, pipelines, and cross-cutting concerns.'
---

# Handling Errors

Handle errors in handlers, pipelines, and cross-cutting concerns.

## Raising Exceptions in Handlers

Any exception in a handler stops the pipeline and returns an error response:

```python
from evoid.web.route import Service, get

app = Service("api")

@get("/users/{user_id}")
async def get_user(user_id: int) -> dict:
    if user_id > 100:
        raise Exception("User not found")
    return {"id": user_id, "name": "Alice"}
```

The pipeline short-circuits — remaining processors do not run.

## Returning Error Dicts

For structured errors, return a dict with an error field:

```python
@get("/users/{user_id}")
async def get_user(user_id: int) -> dict:
    if user_id > 100:
        return {"error": "User not found", "status": "error"}
    return {"id": user_id, "name": "Alice"}
```

!!! info "Error response format"
    The default error response wraps exceptions in `{"detail": "<message>"}`.

## The Result Object

Pipeline execution returns a `Result` with success/error fields:

```python
from evoid.core import Intent, Level, Context, Result, execute

async def my_handler(ctx: Context) -> dict:
    return {"status": "ok"}

intent = Intent(name="test", level=Level.STANDARD)
result = await execute(intent)

# Check result
if result.success:
    print(f"Value: {result.value}")
else:
    print(f"Error: {result.error}")
    print(f"Ran processors: {result.processors}")
    print(f"Duration: {result.duration:.3f}s")
```

| Field | Description |
|-------|-------------|
| `success` | `True` if pipeline completed without exceptions |
| `value` | Return value of the last processor |
| `error` | The exception if pipeline failed |
| `processors` | Tuple of processor names that ran |
| `duration` | Total execution time in seconds |

## Pipeline Error Handling

Errors in processors short-circuit the pipeline. The `Result` captures the failure:

```python
from evoid.core import Intent, Level, Context, Result, register, register_processor, execute

async def validator(ctx: Context) -> dict:
    data = ctx.state.get("data")
    if not data:
        raise ValueError("Missing required data")
    return {"validated": True}

async def fetcher(ctx: Context) -> dict:
    # This never runs if validator fails
    return {"fetched": True}

intent = Intent(name="validate_and_fetch", level=Level.STANDARD)
register(intent)
register_processor("validate_and_fetch", validator)
register_processor("validate_and_fetch", fetcher)

result = await execute(intent)
# result.success = False, result.error = ValueError("Missing required data")
# Only validator ran
```

## Collecting Non-Critical Errors

Use `ctx.errors` to collect warnings without stopping the pipeline:

```python
from evoid.core import Context

async def optional_validator(ctx: Context) -> dict:
    try:
        validate(ctx.state.get("data"))
    except ValidationError as e:
        ctx.errors.append(e)
        # Pipeline continues

    return {"validated": True, "warnings": len(ctx.errors)}

register_processor("optional_validator", optional_validator)
```

!!! tip "Non-blocking errors"
    Appending to `ctx.errors` lets the pipeline continue. The errors are available to downstream processors.

## @route Style Error Handling

```python
from evoid.web.route import Service, post, before, after

app = Service("api")

async def validate_body(ctx: Context) -> dict:
    body = ctx.metadata.get("body", {})
    if "email" not in body:
        raise ValueError("Email is required")
    return {"validated": True}

async def audit_log(ctx: Context) -> dict:
    errors = ctx.errors
    if errors:
        print(f"Warnings during request: {errors}")
    return {"audited": True}

register_processor("validate_body", validate_body)
register_processor("audit_log", audit_log)

@app.post("/users")
async def create_user(name: str, email: str) -> dict:
    return {"status": "created", "name": name}

before("POST:/users", "validate_body")
after("POST:/users", "audit_log")
```

## @controller Style

Same error handling patterns work with controllers:

```python
from evoid.web.controller import Service, Controller, POST

app = Service("api")

@Controller("/orders")
class OrderController:
    @POST("/")
    async def create_order(self, item_id: int, quantity: int) -> dict:
        if quantity <= 0:
            raise ValueError("Quantity must be positive")
        return {"status": "created", "item_id": item_id, "quantity": quantity}
```

## Native Style

With native IOP, raise exceptions directly in handlers:

```python
from evoid import Intent, Level, add_intent

CREATE_ORDER = Intent(
    name="create_order",
    level=Level.STANDARD,
    metadata={"method": "POST", "path": "/orders"},
)

async def handle_create_order(intent: Intent) -> dict:
    body = intent.metadata.get("body", {})
    quantity = body.get("quantity", 0)

    if quantity <= 0:
        raise ValueError("Quantity must be positive")

    return {"status": "created", "quantity": quantity}

add_intent(CREATE_ORDER, handle_create_order)
```

## Error Handling Summary

| Scenario | Approach |
|----------|----------|
| Fatal error | `raise Exception("message")` — pipeline stops |
| Structured error | Return `{"error": "message", "status": "error"}` |
| Non-critical warning | `ctx.errors.append(e)` — pipeline continues |
| Check result | `result.success`, `result.error` |
