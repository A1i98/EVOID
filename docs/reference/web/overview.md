# EVOID Web Overview

## What is EVOID?

EVOID is the reference runtime for Intent-Oriented Programming (IOP). Your data tells the system what it wants. The runtime handles how to execute it.

## Key Features

| Feature | Description |
|---------|-------------|
| **Intent-Driven** | Data declares intent, runtime decides execution |
| **Async-Native** | Full async/await support |
| **Plugin-Based** | Every engine is replaceable |
| **Pipeline Composition** | Processors are pure functions composed together |
| **Multi-Adapter** | ASGI, CLI, Telegram, Robyn, WebSocket |
| **Zero Overhead** | IOP executes with no extra cost |

## Install

```bash
uv add evoid
```

Or with pip:

```bash
pip install evoid
```

Requires: Python 3.12+

## Basic Example

### @route (Function-based)

```python
from evoid.web.route import Service, get, post

app = Service("my-api")

@get("/")
async def home() -> dict:
    return {"message": "Hello from EVOID!"}

@get("/users/{user_id}")
async def get_user(user_id: int) -> dict:
    return {"id": user_id, "name": f"User {user_id}"}

@post("/users")
async def create_user(name: str, email: str) -> dict:
    return {"status": "created", "name": name}
```

### @controller (Class-based)

```python
from evoid.web.controller import Service, Controller, GET, POST

app = Service("my-api")

@Controller("/users")
class UserController:
    @GET("/{user_id}")
    async def get_user(self, user_id: int) -> dict:
        return {"id": user_id}

    @POST("/")
    async def create_user(self, name: str, email: str) -> dict:
        return {"status": "created"}
```

### Native (Full Control)

```python
from evoid.native import create_service, on
from evoid import Intent, Level

app = create_service("my-api")

GET_USER = Intent(name="get_user", level=Level.STANDARD)

async def get_user(intent: Intent) -> dict:
    return {"id": 1, "name": "Alice"}

on(app, GET_USER, get_user)
```

## Running

```bash
evo init my-api
cd my-api
evo service new api
evo service run api
```

Server starts at `http://0.0.0.0:8000`.

## What You Get From One Declaration

With a single type declaration:
- **Editor support** — completion, type checks
- **Validation** — automatic validation with clear errors
- **Input conversion** — JSON, path params, query params, cookies, headers
- **Output conversion** — Python types → JSON
- **Pipeline execution** — processors run in sequence

## Intent Levels

| Level | Pipeline | Timeout | Use Case |
|-------|----------|---------|----------|
| `ephemeral` | `validate` | 5s | Cache, sessions, temporary data |
| `standard` | `validate`, `authorize` | 10s | User profile, posts, comments |
| `critical` | `validate`, `authorize`, `audit`, `protect` | 30s | Payments, medical, legal |

## EVOID vs FastAPI

| Aspect | FastAPI | EVOID |
|--------|---------|-------|
| Paradigm | OOP + FP | IOP |
| Data Flow | Request → Response | Intent → Pipeline → Result |
| Extension | Middleware | Pipeline Extension (before/after) |
| Communication | HTTP | Intent-based (Message Bus) |
| State | Request-scoped | Context (mutable databag) |
| Validation | Pydantic model | Schema Engine (pluggable) |
