# EVOID

**Intent-Oriented Programming Runtime**

[![Python 3.13+](https://img.shields.io/badge/python-3.13+-blue.svg)](https://www.python.org/downloads/)
[![License](https://img.shields.io/badge/license-Apache%202.0-green.svg)](LICENSE)
[![Version](https://img.shields.io/badge/version-2.0.0--alpha-orange.svg)](https://github.com/EvolveBeyond/EVOID)

EVOID is the reference runtime for Intent-Oriented Programming (IOP). Your data declares what it needs. The runtime handles how.

```python
from evoid.web.route import Service, get, post

app = Service("my-api")

@get("/users/{user_id}")
async def get_user(user_id: int) -> dict:
    return {"id": user_id, "name": "Alice"}

@post("/payments", level="critical")
async def process_payment(amount: float) -> dict:
    return {"status": "paid", "amount": amount}
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

Requires Python 3.13+.

---

## Create and Run

```bash
evo init my-api
cd my-api
evo service new api
evo service run api
```

Server starts at `http://0.0.0.0:8000`.

---

## What Is IOP?

Every time you write an endpoint, you decide which database, how to cache, whether to encrypt, what priority. IOP removes that burden.

```python
# Traditional: you tell the system HOW
def save_user(user):
    encrypted = encrypt(user.email)
    cache.set(f"user:{user.id}", encrypted, ttl=300)
    db.insert("users", encrypted)
    audit_log("user_created", user)

# IOP: you tell the system WHAT
class User(BaseModel):
    name: standard(str)      # Normal processing
    email: critical(str)     # Auto-encrypt, audit, replicate
    session: ephemeral(str)  # Memory only, auto-expire
```

Three intent levels control infrastructure behavior:

| Level | Use Case | Pipeline |
|-------|----------|----------|
| `ephemeral` | Cache, sessions, temp data | `validate` |
| `standard` | User profiles, posts, comments | `validate`, `authorize` |
| `critical` | Payments, medical records, legal | `validate`, `authorize`, `audit`, `protect` |

---

## Three Syntax Styles

All styles are IOP underneath.

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
| Intent-Aware Caching | Three tiers: ephemeral, standard, critical |
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

Two sources, depending on your goal:

**Using EVOID?** Read the user documentation:

[https://evolvebeyond.github.io/EVOID/](https://evolvebeyond.github.io/EVOID/)

Tutorials, API reference, syntax guides, and examples.

**Contributing to EVOID?** Read the architecture documentation:

[https://deepwiki.com/EvolveBeyond/EVOID](https://deepwiki.com/EvolveBeyond/EVOID)

Deep technical walkthrough of the codebase, design decisions, and internals.

---

## Contributing

EVOID is open source and accepts contributions.

1. Read the [architecture docs](https://deepwiki.com/EvolveBeyond/EVOID) to understand the codebase
2. Fork the repository
3. Create a feature branch (`git checkout -b feature/my-change`)
4. Commit your changes
5. Push and open a Pull Request

---

## License

Apache 2.0
