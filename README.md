# EVOID

**Reference Runtime for Intent-Oriented Programming**

[![Python 3.12+](https://img.shields.io/badge/python-3.12+-blue.svg)](https://www.python.org/downloads/)
[![License](https://img.shields.io/badge/license-Apache%202.0-green.svg)](LICENSE)
[![Version](https://img.shields.io/badge/version-0.4.1-orange.svg)](https://github.com/EvolveBeyond/EVOID)
[![Zero Dependencies](https://img.shields.io/badge/core%20deps-zero-brightgreen.svg)](https://github.com/EvolveBeyond/EVOID)

---

## What Is IOP?

Every time you write an endpoint, you decide which database, how to cache, whether to encrypt, what priority. IOP removes that burden. Your data declares what it needs. The runtime handles how.

```python
from evoid.web.route import Service, get, post

app = Service("my-api")

@app.get("/users/{user_id}")
async def get_user(user_id: int) -> dict:
    return {"id": user_id, "name": "Alice"}

@app.post("/payments", level="critical")
async def process_payment(amount: float) -> dict:
    return {"status": "paid", "amount": amount}
```

---

## Architecture

```
┌─────────────────────────────────────────────────┐
│                  User Code                       │
│  @get / @post / @controller / native on()       │
└──────────────────────┬──────────────────────────┘
                       │ creates Intent
                       ▼
┌─────────────────────────────────────────────────┐
│               Intent Registry                    │
│  Intent(dataclass) → frozen, immutable           │
└──────────────────────┬──────────────────────────┘
                       │ resolve
                       ▼
┌─────────────────────────────────────────────────┐
│            Pipeline Resolver                     │
│  Level → default processors + timeout            │
│  Extend system overrides (before/after/replace)  │
└──────────────────────┬──────────────────────────┘
                       │ tuple[ProcessorName]
                       ▼
┌─────────────────────────────────────────────────┐
│            Pipeline Executor                     │
│  Fast path / Timeout path / Inspect path         │
│  Each processor: Context → Result                │
└──────────────────────┬──────────────────────────┘
                       │
                       ▼
┌─────────────────────────────────────────────────┐
│                  Result                          │
│  success, value, error, duration, steps          │
└─────────────────────────────────────────────────┘
```

---

## Install

```bash
uv add evoid
```

Or with pip:

```bash
pip install evoid
```

Requires Python 3.12+. Zero core dependencies — add only what you need:

```bash
evo install sqlite     # SQLite storage
evo install redis      # Redis cache
evo install full       # Everything
```

---

## Quick Start

```bash
evo init my-api
cd my-api
evo service new api
evo service run api
```

Server starts at `http://0.0.0.0:8000`.

### Minimal Example

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

---

## Three Syntax Styles

All styles are IOP underneath. Pick the one that fits your team.

### @route (Function-based)

```python
from evoid.web.route import Service, get, post

app = Service("my-api")

@get("/users/{user_id}")
async def get_user(user_id: int) -> dict:
    return {"id": user_id}

@post("/users")
async def create_user(name: str, email: str) -> dict:
    return {"status": "created"}
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
from evoid import Intent, Level, add_intent

MY_INTENT = Intent(name="get_user", level=Level.STANDARD)

async def handler(intent: Intent) -> dict:
    return {"id": 1, "name": "Alice"}

add_intent(MY_INTENT, handler)
```

---

## Intent Levels

| Level | Pipeline | Timeout | Use Case |
|-------|----------|---------|----------|
| `ephemeral` | `validate` | 5s | Cache, sessions, temp data |
| `standard` | `validate`, `authorize` | 10s | User profiles, posts, comments |
| `critical` | `validate`, `authorize`, `audit`, `protect` | 30s | Payments, medical, legal |

---

## Features

| Feature | Description |
|---------|-------------|
| Intent-Driven | Data declares what, runtime decides how |
| Async-Native | Full async/await support |
| Plugin-Based | Every engine is replaceable |
| Parallel Execution | Run multiple intents concurrently |
| Microservices | Project + Service structure |
| Multi-Adapter | ASGI, CLI, Telegram, Robyn, WebSocket |
| Pipeline Extensions | Inject processors before/after routes |
| Message Bus | Inter-service communication via Intents |

---

## CLI

```bash
evo init <name>           # Create project
evo service new <name>    # Add service
evo service list          # List services
evo service run <name>    # Run service
evo sync                  # Sync dependencies
evo run                   # Run all services
evo serve                 # Quick serve
evo list-intents          # List registered intents
evo exec <intent>         # Execute intent
evo version               # Show version
```

---

## Project Structure

```
my-api/
  evoid.toml            # Project config
  shared/               # Shared code between services
  services/
    api/
      evoid.toml        # Service config
      main.py           # Service code
```

---

## Documentation

**User docs:** [https://evolvebeyond.github.io/EVOID/](https://evolvebeyond.github.io/EVOID/)

**Architecture docs:** [https://deepwiki.com/EvolveBeyond/EVOID](https://deepwiki.com/EvolveBeyond/EVOID)

---

## Contributing

See [CONTRIBUTING.md](CONTRIBUTING.md) for guidelines.

1. Fork the repository
2. Create a feature branch (`git checkout -b feature/my-change`)
3. Commit your changes
4. Push and open a Pull Request

---

## License

Apache 2.0 — see [LICENSE](LICENSE)
