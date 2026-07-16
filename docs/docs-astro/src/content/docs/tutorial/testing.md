---
title: 'Testing'
description: 'Unit test handlers, intents, and pipelines in your EVOID services.'
---

# Testing

Unit test handlers, intents, and pipelines in your EVOID services.

## Testing Handlers Directly

Handlers are plain async functions — test them like any Python function:

```python
import asyncio
from evoid import Intent, Level, Context

async def get_user(intent: Intent) -> dict:
    user_id = intent.metadata.get("id", 1)
    return {"id": user_id, "name": f"User {user_id}"}

# Create an Intent and call the handler directly
intent = Intent(name="get_user", level=Level.STANDARD, metadata={"id": 42})
result = asyncio.run(get_user(intent))
assert result == {"id": 42, "name": "User 42"}
```

## Testing with execute()

Use `execute()` to run an Intent through its full pipeline:

```python
import asyncio
from evoid import Intent, Level, Context, execute
from evoid.core.extend import add_intent_with_pipeline

# Setup
GET_USER = Intent(name="get_user", level=Level.STANDARD)

async def handle_get_user(ctx: Context) -> dict:
    user_id = ctx.intent.metadata.get("id", 1)
    return {"id": user_id, "name": f"User {user_id}"}

add_intent_with_pipeline(
    GET_USER,
    processors=["validate", "get_user"],
    handler=handle_get_user,
)

# Test
intent = Intent(name="get_user", level=Level.STANDARD, metadata={"id": 42})
result = asyncio.run(execute(intent))

assert result.success is True
assert result.value == {"id": 42, "name": "User 42"}
```

## Testing Pipelines

Test that processors run in order and handle errors:

```python
import asyncio
from evoid import Intent, Level, Context, Result
from evoid.core.pipeline import execute as execute_pipeline
from evoid.core.processor import register as register_proc

async def validator(ctx: Context) -> dict:
    return {"validated": True}

async def processor(ctx: Context) -> dict:
    return {"processed": True}

# Register processors
register_proc("validator", validator)
register_proc("processor", processor)

# Create context
intent = Intent(name="test", level=Level.STANDARD)
ctx = Context(intent=intent)

# Run pipeline
result = asyncio.run(
    execute_pipeline(
        pipeline=("validator", "processor"),
        context=ctx,
        registry={"validator": validator, "processor": processor},
    )
)

assert result.success is True
assert "validator" in result.processors
assert "processor" in result.processors
```

## Testing Error Cases

Test that errors are caught and Result reflects the failure:

```python
import asyncio
from evoid import Intent, Level, Context
from evoid.core.pipeline import execute as execute_pipeline

async def failing_processor(ctx: Context) -> dict:
    raise ValueError("Something went wrong")

intent = Intent(name="test", level=Level.STANDARD)
ctx = Context(intent=intent)

result = asyncio.run(
    execute_pipeline(
        pipeline=("failing_processor",),
        context=ctx,
        registry={"failing_processor": failing_processor},
    )
)

assert result.success is False
assert isinstance(result.error, ValueError)
assert str(result.error) == "Something went wrong"
```

## @route Style Testing

Test routes by creating the Service and accessing its Intent registry:

```python
import asyncio
from evoid.web.route import Service, get
from evoid import resolve

app = Service("api")

@app.get("/users/{user_id}")
async def get_user(user_id: int) -> dict:
    return {"id": user_id, "name": f"User {user_id}"}

# Verify the Intent was registered
intent = resolve("GET:/users/{user_id}")
assert intent is not None
assert intent.level.value == "standard"
```

## Testing with execute_service()

Test native services by executing intents by name:

```python
import asyncio
from evoid.native import create_service, on, execute_service
from evoid import Intent, Level

app = create_service("test-service")

GET_USER = Intent(name="get_user", level=Level.STANDARD)

async def handle_get_user(intent: Intent) -> dict:
    return {"id": 1, "name": "Alice"}

on(app, GET_USER, handle_get_user)

# Test
result = asyncio.run(execute_service(app, "get_user"))
assert result.success is True
assert result.value == {"id": 1, "name": "Alice"}
```

## Testing Pipeline Extensions

Test that `before` and `after` processors are injected correctly:

```python
from evoid.core.extend import before, after, get_pipeline_config, clear_overrides
from evoid import Intent, Level

clear_overrides()

intent = Intent(name="get_user", level=Level.STANDARD)

before("get_user", "rate_limit")
after("get_user", "audit_log")

config = get_pipeline_config(intent)
assert "rate_limit" in config.processors
assert "audit_log" in config.processors
```

## Testing Parallel Execution

Test parallel Intent execution:

```python
import asyncio
from evoid import Intent, Level, execute
from evoid.core.parallel import gather
from evoid.core.extend import add_intent

INTENT_A = Intent(name="task_a", level=Level.STANDARD)
INTENT_B = Intent(name="task_b", level=Level.STANDARD)

async def handle_a(ctx: Context) -> dict:
    return {"task": "a"}

async def handle_b(ctx: Context) -> dict:
    return {"task": "b"}

add_intent(INTENT_A, handle_a)
add_intent(INTENT_B, handle_b)

# Run in parallel
results = asyncio.run(gather(INTENT_A, INTENT_B))
assert len(results) == 2
assert all(r.success for r in results)
```

## Using pytest

For cleaner tests, use pytest with asyncio:

```python
import pytest
from evoid import Intent, Level, Context, execute
from evoid.core.extend import add_intent_with_pipeline

@pytest.fixture(autouse=True)
def setup():
    from evoid import clear_registry
    from evoid.core.extend import clear_overrides
    clear_registry()
    clear_overrides()
    yield
    clear_registry()
    clear_overrides()

@pytest.mark.asyncio
async def test_get_user():
    GET_USER = Intent(name="get_user", level=Level.STANDARD)

    async def handle(ctx: Context) -> dict:
        return {"id": 1, "name": "Alice"}

    add_intent_with_pipeline(GET_USER, processors=["get_user"], handler=handle)

    intent = Intent(name="get_user", level=Level.STANDARD)
    result = await execute(intent)

    assert result.success is True
    assert result.value == {"id": 1, "name": "Alice"}
```

## Testing Checklist

| What | How |
|------|-----|
| Handler logic | Call handler function directly |
| Full pipeline | Use `execute(intent)` and check `Result` |
| Error cases | Assert `result.success is False` |
| Intent registration | Use `resolve("name")` |
| Pipeline overrides | Use `get_pipeline_config(intent)` |
| Parallel execution | Use `gather(intent1, intent2)` |
