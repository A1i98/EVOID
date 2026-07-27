---
title: 'Quick Start'
description: 'Build a working EVOID API in 5 minutes.'
---

# Quick Start

Build a working EVOID API in 5 minutes.

## Prerequisites

- Python 3.12 or higher
- [uv](https://docs.astral.sh/uv/) (recommended) or pip

## Step 1: Install & Create

```bash
uv add evoid
evo init my-api
cd my-api
```

This creates:

```
my-api/
  pyproject.toml
  shared/
  services/
    gateway/        # ← your entry point (port 8000)
      evoid.toml
      main.py
```

## Step 2: Create a Service

Each service handles one domain. Services subscribe to Intents via the message bus.

```bash
evo service new users
```

Edit `services/users/main.py`:

```python
from evoid import Intent, Level, register, register_processor

register(Intent(name="get_user", level=Level.STANDARD))
register(Intent(name="create_user", level=Level.STANDARD))

async def handle_get_user(ctx) -> dict:
    user_id = ctx.intent.metadata.get("user_id", 0)
    return {"id": user_id, "name": f"User {user_id}"}

async def handle_create_user(ctx) -> dict:
    name = ctx.intent.metadata.get("name", "unknown")
    return {"status": "created", "name": name}

register_processor("get_user", handle_get_user)
register_processor("create_user", handle_create_user)
```

The service doesn't know about HTTP, URLs, or the gateway. It only knows Intents.

## Step 3: Connect Gateway to Service

The gateway receives HTTP and converts it to Intents. Edit `services/gateway/main.py`:

```python
from evoid.web.route import Service, get, post, run
from evoid import Intent, Level, publish

app = Service("gateway")

@get("/health")
async def health() -> dict:
    return {"status": "healthy"}

@get("/users/{user_id}")
async def get_user(user_id: int) -> dict:
    result = await publish(Intent(
        name="get_user",
        level=Level.STANDARD,
        metadata={"user_id": user_id},
    ))
    return result[0].value if result else {"error": "no handler"}

@post("/users")
async def create_user(name: str) -> dict:
    result = await publish(Intent(
        name="create_user",
        level=Level.STANDARD,
        metadata={"name": name},
    ))
    return result[0].value if result else {"error": "no handler"}
```

The gateway converts HTTP to Intent. The service handles the Intent. Neither knows about the other.

## Step 4: Run Everything

```bash
evo run
```

This starts both services. You should see:

```
Starting gateway on http://0.0.0.0:8000
Starting users on http://0.0.0.0:8001
```

## Step 5: Test It

```bash
# Get user — gateway routes to users service via message bus
curl http://localhost:8000/users/123
# {"id": 123, "name": "User 123"}

# Create user
curl -X POST http://localhost:8000/users?name=Ali
# {"status": "created", "name": "Ali"}
```

!!! info "What just happened?"
    The request flowed through three layers:

    1. **Gateway received HTTP** — `GET /users/123` hit the gateway on port 8000
    2. **Gateway created Intent** — Converted HTTP to `Intent(name="get_user", metadata={"user_id": 123})`
    3. **Message bus routed** — Intent went to the users service (subscribed to "get_user")
    4. **Service handled Intent** — `handle_get_user()` ran, returned `{"id": 123, "name": "User 123"}`
    5. **Gateway returned response** — Result sent back as HTTP JSON

    The gateway doesn't know what "get_user" does. The users service doesn't know about HTTP. They only share Intent names. That's IOP — data declares intent, the system routes it.

## Adding Protection Levels

Change the protection level per route:

```python
@get("/public/data", level="ephemeral")
async def public_data() -> dict:
    return {"data": "cache me"}

@get("/users/{id}", level="standard")
async def get_user(id: int) -> dict:
    return {"id": id}

@post("/payments", level="critical")
async def process_payment(amount: float) -> dict:
    return {"status": "paid"}
```

Each level maps to a different pipeline — `ephemeral` gets fast validation only, `critical` gets full audit and protection.

## Next

Build a real project step by step — [Tutorial: Your First Intent](/EVOID/docs/tutorial/first-intent/).
