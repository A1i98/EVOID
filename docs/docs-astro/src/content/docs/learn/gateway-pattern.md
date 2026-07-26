---
title: 'Gateway Pattern'
description: 'The gateway is your app entry point. Configure it, extend it, route through it.'
---

# Gateway Pattern

`evo init` creates a **gateway** service automatically. It's the entry point for all external requests. Every other service lives behind it.

## What Is the Gateway

The gateway is a regular EVOID service. Nothing special about its code. What makes it a "gateway" is its role: it receives HTTP requests and routes them to the right service via the message bus.

```
HTTP Request → Gateway → Message Bus → Service
                     ← Response ←
```

## Project Structure

```
my-project/
├── services/
│   └── gateway/
│       ├── evoid.toml      # port 8000, adapter asgi
│       └── main.py         # routes, middleware, auth
├── shared/
└── pyproject.toml
```

Gateway starts on port 8000. New services auto-increment: 8001, 8002, 8003.

## Default Gateway

`evo init` generates a gateway with health check only:

```python
from evoid.web.route import Service, get, post, run

app = Service("gateway")

@get("/health")
async def health() -> dict:
    return {"status": "healthy"}
```

The gateway doesn't contain business logic. It routes requests to services via the message bus. Each route converts HTTP to an Intent and publishes it.

## How Routing Works

The gateway converts HTTP requests to Intents:

```python
from evoid import Intent, Level, publish

@get("/users/{user_id}")
async def get_user(user_id: int) -> dict:
    result = await publish(Intent(
        name="get_user",          # ← Intent name
        level=Level.STANDARD,
        metadata={"user_id": user_id},
    ))
    return result.value
```

The service subscribes to "get_user" and handles it:

```python
from evoid import register, register_processor

register(Intent(name="get_user", level=Level.STANDARD))

async def handle_get_user(ctx) -> dict:
    user_id = ctx.intent.metadata.get("user_id")
    return {"id": user_id, "name": f"User {user_id}"}

register_processor("get_user", handle_get_user)
```

Gateway and service don't know about each other. They only share the Intent name.

## Configuring the Gateway

### evoid.toml

```toml
[service]
name = "gateway"

[runtime]
adapter = "asgi"
host = "0.0.0.0"
port = 8000

[pipeline]
processors = ["validate", "authorize"]
```

### Python Config

```python
from evoid.config import config

app = config(
    service={"name": "gateway"},
    runtime={"adapter": "asgi", "port": 8000},
    pipeline={"processors": ["validate", "authorize"]},
)
```

## Adding Routes

Each gateway route converts HTTP to an Intent. The route is thin — it just extracts parameters and publishes:

```python
from evoid import Intent, Level, publish
from evoid.web.route import get, post

@get("/api/menu")
async def list_menu() -> dict:
    result = await publish(Intent(
        name="list_menu",
        level=Level.EPHEMERAL,
    ))
    return result.value

@post("/api/orders")
async def create_order(sandwich: str, qty: int = 1) -> dict:
    result = await publish(Intent(
        name="create_order",
        level=Level.STANDARD,
        metadata={"sandwich": sandwich, "qty": qty},
    ))
    return result.value
```

Business logic lives in services. The gateway only routes.

## Adding Middleware

Add processors that run before every request:

```python
from evoid.web.route import before

# Rate limit all /api/ routes
before("GET:/api/*", "rate_limit")
before("POST:/api/*", "rate_limit")

# Log all requests
before("GET:/health", "log_request")
```

## Adding Authentication

Protect routes with auth processors:

```python
from evoid.web.route import before

# Require auth for all /api/ routes
before("GET:/api/*", "authorize")
before("POST:/api/*", "authorize")

# Health check stays open (no auth)
# /health has no before() — no auth needed
```

## Gateway vs Direct Service

| Approach | When to Use |
|----------|-------------|
| Gateway only | Small app, single service, prototyping |
| Gateway + services | Medium app, 2-5 services |
| Gateway + cluster | Large app, multiple machines |

## Scaling

### Add Services

```bash
evo service new api        # port 8001 (auto)
evo service new payments   # port 8002 (auto)
evo service new inventory  # port 8003 (auto)
```

### Run All

```bash
evo run                    # starts all services
```

### Run One

```bash
evo service run gateway    # just the gateway
evo service run api        # just the api service
```

## Customizing the Gateway

The gateway is just a service. You can:

- Add any route decorators (`@get`, `@post`, `@put`, `@delete`)
- Add middleware via `before()` / `after()`
- Change the pipeline in `evoid.toml`
- Add auth, rate limiting, logging
- Use it as a reverse proxy (forward to other services via message bus)
- Use it as an API aggregator (combine multiple service responses)

## Related

- [Message Bus](message-bus.md): how Intents flow between services
- [Configuration](configuration.md): full config reference
- [Tutorial: Going Online](../tutorial/going-online.md): first web endpoint
