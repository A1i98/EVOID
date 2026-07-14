# EVOID

[![Python 3.13+](https://img.shields.io/badge/Python-3.13+-3776AB?style=flat-square&logo=python&logoColor=white)](https://www.python.org/downloads/)
[![License](https://img.shields.io/badge/License-Apache%202.0-green?style=flat-square)](LICENSE)
[![Version](https://img.shields.io/badge/Version-0.3.0-purple?style=flat-square)](https://github.com/EvolveBeyond/EVOID)
[![IOP](https://img.shields.io/badge/Paradigm-IOP-6366f1?style=flat-square)](https://github.com/EvolveBeyond/EVOID)

> **Reference Runtime for Intent-Oriented Programming (IOP)**

EVOID is not a framework. It's a **runtime specification** for Intent-Oriented Programming (IOP) — a new paradigm where your data model IS your infrastructure policy.

> **Intent is permanent. Infrastructure is temporary.**

---

## What is IOP?

**Intent-Oriented Programming** is a paradigm where developers declare **WHAT they want**, and the runtime decides **HOW to achieve it**.

```python
# Traditional: You tell the system HOW
def save_user(user):
    encrypted = encrypt(user.email)
    cache.set(f"user:{user.id}", encrypted, ttl=300)
    db.insert("users", encrypted)
    audit_log("user_created", user)

# IOP: You tell the system WHAT
class User(BaseModel):
    name: standard(str)      # Normal processing
    email: critical(str)     # Auto-encrypt, audit, replicate
    session: ephemeral(str)  # Memory only, auto-expire
```

**The kitchen analogy:** A chef shouldn't have to build the kitchen, buy the groceries, and clean up — every single time they cook a meal. With IOP, your data tells the system what it needs.

---

## Quick Start

```bash
# Install
uv add evoid

# Create project
evo init my-api
cd my-api

# Add service
evo service new api

# Run
evo service run api
```

---

## Three Syntax Styles

All styles are IOP underneath — just different sugar.

### @route (Function-based)

```python
from evoid.web.route import Service, get, post

app = Service("my-api")

@get("/users/{id}")
async def get_user(id: int) -> dict:
    return {"id": id}

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
    @GET("/{id}")
    async def get_user(self, id: int) -> dict:
        return {"id": id}

    @POST("/")
    async def create_user(self, name: str, email: str) -> dict:
        return {"status": "created"}
```

### Native (Full Control)

```python
from evoid import Intent, Level, add_intent

MY_INTENT = Intent(name="my_intent", level=Level.CRITICAL)

async def handle(intent: Intent) -> dict:
    return {"status": "ok"}

add_intent(MY_INTENT, handle)
```

---

## Features

| Feature | Description |
|---------|-------------|
| 🎯 **Intent-Driven** | Declare what, framework decides how |
| ⚡ **Async-Native** | Full async/await support |
| 🧩 **Plugin-Based** | Everything is replaceable |
| 🔄 **Parallel Execution** | Run multiple intents simultaneously |
| 🏗️ **Microservices Ready** | Project + Service structure |
| 🔌 **Multi-Adapter** | ASGI, CLI, Telegram, Robyn, WebSocket |
| 📊 **Three Syntax Styles** | @route, @controller, native |
| 🔐 **Security Built-in** | Encryption, auth, audit trails |
| 💾 **Intent-Aware Caching** | EPHEMERAL, STANDARD, CRITICAL tiers |

---

## Links

- [GitHub](https://github.com/EvolveBeyond/EVOID)
- [PyPI](https://pypi.org/project/evoid/)
- [Tutorial](tutorial/)
- [API Reference](api/)
