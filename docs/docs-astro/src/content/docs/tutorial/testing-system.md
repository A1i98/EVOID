---
title: 'Testing Your API'
description: 'Write tests for EVOID Intents using pytest and the tc() helper.'
---

# Testing Your API

Write tests for EVOID Intents. The testing system uses pytest — the Python standard.

## First Test

Create `tests/test_api.py`:

```python
from evoid.testing import tc
from evoid import Intent, Level, register, add_intent_with_pipeline
from evoid.core import Context

# Setup
GET_USER = Intent(name="get_user", level=Level.STANDARD)

async def handle_get_user(ctx: Context) -> dict:
    user_id = ctx.intent.metadata.get("user_id", 1)
    return {"id": user_id, "name": f"User {user_id}"}

add_intent_with_pipeline(GET_USER, processors=["get_user"], handler=handle_get_user)

# Test
def test_get_user():
    return tc(GET_USER, expect={"id": 1, "name": "User 1"})
```

Run:

```bash
pytest tests/ -v
# tests/test_api.py::test_get_user PASSED
```

## What Just Happened

1. `tc(GET_USER, expect=...)` creates a `TestCase`
2. pytest collects `test_get_user` function
3. Plugin executes `GET_USER` through the pipeline
4. Result is compared with `expect`
5. If match → PASS, if not → FAIL

## Testing @route APIs

```python
from evoid.testing import tc
from evoid.web.route import Service, get, post

app = Service("test-api")

@get("/users/{user_id}")
async def get_user(user_id: int) -> dict:
    return {"id": user_id, "name": f"User {user_id}"}

@post("/users")
async def create_user(name: str, email: str) -> dict:
    return {"status": "created", "name": name}

# Tests
def test_get_user():
    from evoid.core import all_intents
    intent = all_intents()["GET:/users/{user_id}"]
    return tc(intent, expect={"id": 1, "name": "User 1"})

def test_create_user():
    from evoid.core import all_intents
    intent = all_intents()["POST:/users"]
    return tc(intent, expect={"status": "created", "name": "test"})
```

## Testing Native IOP Services

```python
from evoid.testing import tc
from evoid.native import create_service, on
from evoid import Intent, Level

app = create_service("user-service")

GET_USER = Intent(name="get_user", level=Level.STANDARD)
CREATE_USER = Intent(name="create_user", level=Level.STANDARD)

async def handle_get(intent: Intent) -> dict:
    return {"id": 1, "name": "Alice"}

async def handle_create(intent: Intent) -> dict:
    return {"status": "created"}

on(app, GET_USER, handle_get)
on(app, CREATE_USER, handle_create)

# Tests
def test_get_user():
    return tc(GET_USER, expect={"id": 1, "name": "Alice"})

def test_create_user():
    return tc(CREATE_USER, expect={"status": "created"})
```

## Testing Errors

```python
from evoid.testing import tc
from evoid import Intent, Level

FAIL_INTENT = Intent(name="fail", level=Level.STANDARD)

def test_error_handling():
    return tc(FAIL_INTENT, expect_error=ValueError)
```

## Testing with Metadata

Pass different metadata to test different scenarios:

```python
from evoid.testing import tc
from evoid import Intent, Level

GET_USER = Intent(name="get_user", level=Level.STANDARD)

def test_existing_user():
    intent = Intent(name="get_user", level=Level.STANDARD, metadata={"user_id": 1})
    return tc(intent, expect={"id": 1, "name": "Alice"})

def test_nonexistent_user():
    intent = Intent(name="get_user", level=Level.STANDARD, metadata={"user_id": 999})
    return tc(intent, expect={"error": "not found"})
```

## Running Tests

```bash
# All tests
pytest tests/ -v

# Specific file
pytest tests/test_api.py -v

# Filter by name
pytest tests/ -k "user"

# Stop on first failure
pytest tests/ -x

# Show print output
pytest tests/ -s

# With WebUI dashboard
pytest tests/ --evoid-webui
```

## WebUI Dashboard

After tests run, the dashboard shows:

- Total / Passed / Failed / Duration
- Progress bar
- Per-test results with timing
- Dark theme, Docker-style

```bash
pytest tests/ --evoid-webui
# Dashboard at http://localhost:8001
```

## Best Practices

```python
# Good: one assertion per test
def test_get_user():
    return tc(GET_USER, expect={"id": 1})

def test_get_user_not_found():
    return tc(GET_USER_404, expect_error=ValueError)

# Bad: testing multiple things in one test
def test_everything():
    return tc(GET_USER, expect=...)  # too much
```

## Related

- [Testing Reference](../learn/testing.md) — Full API reference
- [Handling Errors](handling-errors.md) — Error handling patterns
- [Pipeline](../learn/pipeline.md) — How execution works
