---
title: 'Metadata and Configuration'
description: 'How EVOID services expose metadata and configuration.'
---

# Metadata and Configuration

How EVOID services expose metadata and configuration.

## Service Metadata

Every EVOID service has metadata accessible at runtime:

```python
from evoid.web.route import Service, get

app = Service("my-api")

@get("/health")
async def health() -> dict:
    return {"status": "healthy"}
```

## Intent Registry

Inspect all registered Intents:

```python
from evoid import all_intents

# After registering routes...
intents = all_intents()

for name, intent in intents.items():
    print(f"{name}: level={intent.level}, metadata={intent.metadata}")
```

Output:

```
GET:/health: level=ephemeral, metadata={'method': 'GET', 'path': '/health'}
POST:/users: level=standard, metadata={'method': 'POST', 'path': '/users'}
```

## Inspecting Pipelines

Check which processors run for any Intent:

```python
from evoid import resolve
from evoid.core.extend import get_pipeline_config

intent = resolve("GET:/users/{id}")
if intent:
    config = get_pipeline_config(intent)
    print(f"Pipeline: {config.processors}")
    print(f"Timeout: {config.timeout}")
```

## List Pipeline Overrides

See all custom pipeline configurations:

```python
from evoid.core.extend import list_overrides

overrides = list_overrides()
for intent_name, processors in overrides.items():
    print(f"{intent_name}: {processors}")
```

## Processor Registry

Check all registered processors:

```python
from evoid import all_processors

processors = all_processors()
for name in processors:
    print(f"Processor: {name}")
```

## @route Style Metadata

Routes automatically create Intents with method and path metadata:

```python
from evoid.web.route import Service, get, post

app = Service("api")

@get("/users/{user_id}")
async def get_user(user_id: int) -> dict:
    return {"id": user_id}

@post("/users", level="critical")
async def create_user(name: str) -> dict:
    return {"status": "created"}
```

The Intents are:

```
GET:/users/{user_id}  → level=standard, metadata={method: "GET", path: "/users/{user_id}"}
POST:/users           → level=critical, metadata={method: "POST", path: "/users"}
```

## @controller Style Metadata

Controllers group routes under a prefix:

```python
from evoid.web.controller import Service, Controller, GET, POST

app = Service("api")

@Controller("/users", level="standard")
class UserController:
    @GET("/")
    async def list_users(self) -> dict:
        return {"users": []}

    @POST("/", level="critical")
    async def create_user(self, name: str) -> dict:
        return {"status": "created"}
```

All routes under `UserController` are prefixed with `/users`.

## Native Style Metadata

Native IOP gives full control over Intent metadata:

```python
from evoid import Intent, Level, add_intent

PAYMENT = Intent(
    name="process_payment",
    level=Level.CRITICAL,
    metadata={
        "method": "POST",
        "path": "/payments",
        "timeout": 15.0,
        "priority": 10,
        "description": "Process a payment",
    },
)

async def handle_payment(intent: Intent) -> dict:
    print(f"Intent name: {intent.name}")
    print(f"Intent level: {intent.level}")
    print(f"Intent metadata: {intent.metadata}")
    return {"status": "paid"}

add_intent(PAYMENT, handle_payment)
```

## Runtime Configuration

Configure the runtime with a `Config` object:

```python
from evoid.core.runtime import Config

config = Config(
    name="my-service",
    adapter="asgi",
    engines={
        "schema": "native",
        "storage": "sqlite",
        "cache": "memory",
        "logger": "loguru",
    },
)
```

## Project Configuration

The `evoid.toml` file configures the project and services:

```toml
[project]
name = "my-api"
version = "0.1.0"

[runtime]
adapter = "asgi"
host = "0.0.0.0"
port = 8000

[engines]
schema = "native"
storage = "memory"
cache = "memory"
logger = "loguru"

[pipeline]
processors = ["validate", "authorize"]
timeout = 10.0
```

## Introspection Summary

| What | How |
|------|-----|
| All Intents | `all_intents()` |
| Resolve by name | `resolve("intent_name")` |
| Pipeline config | `get_pipeline_config(intent)` |
| Pipeline overrides | `list_overrides()` |
| All processors | `all_processors()` |
| Register processor | `register_processor("name", func)` |
| Clear overrides | `clear_overrides()` |
