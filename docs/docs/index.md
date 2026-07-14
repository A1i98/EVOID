# EVOID

<div class="hero" markdown>

**Intent-Oriented Programming Runtime**

:sparkles: A new paradigm where your data model IS your infrastructure policy.

[:material-github: GitHub](https://github.com/EvolveBeyond/EVOID){ .md-button .md-button--primary }
[:material-book: Get Started](getting-started/installation.md){ .md-button }

</div>

---

## What is IOP?

**Intent-Oriented Programming** is a paradigm where developers declare **WHAT they want**, and the runtime decides **HOW to achieve it**.

=== "Traditional"

    ```python
    def save_user(user):
        encrypted = encrypt(user.email)
        cache.set(f"user:{user.id}", encrypted, ttl=300)
        db.insert("users", encrypted)
        audit_log("user_created", user)
    ```

=== "EVOID (IOP)"

    ```python
    class User(BaseModel):
        name: standard(str)
        email: critical(str)     # Auto-encrypt, audit
        session: ephemeral(str)  # Memory only, auto-expire
    ```

!!! info "The Kitchen Analogy"
    A chef shouldn't have to build the kitchen, buy the groceries, and clean up — every single time they cook a meal. With IOP, your data tells the system what it needs.

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
| :dart: **Intent-Driven** | Declare what, framework decides how |
| :zap: **Async-Native** | Full async/await support |
| :puzzle_piece: **Plugin-Based** | Everything is replaceable |
| :arrows_counterclockwise: **Parallel Execution** | Run multiple intents simultaneously |
| :building_construction: **Microservices Ready** | Project + Service structure |
| :electric_plug: **Multi-Adapter** | ASGI, CLI, Telegram, Robyn, WebSocket |
