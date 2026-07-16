---
title: 'Bigger Applications'
description: 'Structure larger EVOID projects with multiple services and modules.'
---

# Bigger Applications

Structure larger EVOID projects with multiple services and modules.

## Project Structure

Create a project with the CLI:

```bash
evo init my-api
cd my-api
```

This creates:

```
my-api/
  evoid.toml          # Project config
  shared/             # Shared models and utilities
  services/
    api/              # Your first service
      evoid.toml
      main.py
```

## Adding Services

```bash
evo service new users
evo service new payments
```

Each service gets its own directory:

```
my-api/
  evoid.toml
  shared/
  services/
    users/
      evoid.toml
      main.py
    payments/
      evoid.toml
      main.py
```

## Multi-File Service

Split a service into multiple modules:

```
services/users/
  main.py           # Entry point
  handlers.py       # Route handlers
  models.py         # Data models
  processors.py     # Custom processors
```

### models.py

```python
from pydantic import BaseModel

class UserCreate(BaseModel):
    name: str
    email: str
    age: int

class UserUpdate(BaseModel):
    name: str | None = None
    email: str | None = None
```

### handlers.py

```python
from evoid.web.route import Service, get, post, put, delete
from .models import UserCreate, UserUpdate

app = Service("users")

@app.get("/users")
async def list_users() -> dict:
    return {"users": []}

@app.post("/users", status=201)
async def create_user(user: UserCreate) -> dict:
    return {"status": "created", "name": user.name}

@app.put("/users/{user_id}")
async def update_user(user_id: int, user: UserUpdate) -> dict:
    return {"id": user_id, "name": user.name}

@app.delete("/users/{user_id}", status=204)
async def delete_user(user_id: int) -> dict:
    return {"status": "deleted"}
```

### main.py

```python
from .handlers import app

if __name__ == "__main__":
    from evoid.web.route import run
    run(app, port=8001)
```

## Service Communication

Services communicate through the message bus — no HTTP between them:

```python
from evoid import Intent, Level, subscribe, publish

# In payment-service:
async def handle_payment(intent: Intent) -> dict:
    body = intent.metadata.get("body", {})

    # Call user-service to verify the user
    user_intent = Intent(
        name="verify_user",
        level=Level.STANDARD,
        metadata={"user_id": body.get("user_id")},
    )
    results = await publish(user_intent)
    user = results[0] if results else None

    return {"status": "paid", "user": user}

subscribe("process_payment", handle_payment)
```

## Running Multiple Services

Start each service on a different port:

```bash
evo service run users --port 8001
evo service run payments --port 8002
```

Or run all services at once:

```bash
evo service run --all
```

## Shared Code

Put shared models, utilities, and processors in `shared/`:

```python
# shared/models.py
from pydantic import BaseModel

class ErrorResponse(BaseModel):
    error: str
    status: str = "error"

class PaginationParams(BaseModel):
    skip: int = 0
    limit: int = 10
```

Import in any service:

```python
from shared.models import ErrorResponse, PaginationParams
```

## @controller Style for Large APIs

Group related routes into controllers:

```python
from evoid.web.controller import Service, Controller, GET, POST, PUT, DELETE

app = Service("api")

@Controller("/users")
class UserController:
    @GET("/")
    async def list_users(self) -> dict:
        return {"users": []}

    @POST("/", status=201)
    async def create_user(self, name: str, email: str) -> dict:
        return {"status": "created", "name": name}

    @GET("/{user_id}")
    async def get_user(self, user_id: int) -> dict:
        return {"id": user_id, "name": "Alice"}

@Controller("/orders")
class OrderController:
    @GET("/")
    async def list_orders(self) -> dict:
        return {"orders": []}

    @POST("/", status=201)
    async def create_order(self, item_id: int, quantity: int) -> dict:
        return {"status": "created", "item_id": item_id}
```

## Native Style for Large Systems

For complex systems with inter-service communication, use native IOP:

```python
from evoid.native import create_service, on
from evoid import Intent, Level

service = create_service("order-service")

CREATE_ORDER = Intent(name="create_order", level=Level.STANDARD)
VERIFY_USER = Intent(name="verify_user", level=Level.STANDARD)
PROCESS_PAYMENT = Intent(name="process_payment", level=Level.CRITICAL)

async def handle_create_order(intent: Intent) -> dict:
    body = intent.metadata.get("body", {})
    return {"status": "created", "item_id": body.get("item_id")}

async def handle_verify_user(intent: Intent) -> dict:
    user_id = intent.metadata.get("user_id")
    return {"verified": True, "user_id": user_id}

async def handle_payment(intent: Intent) -> dict:
    body = intent.metadata.get("body", {})
    return {"status": "paid", "amount": body.get("amount")}

on(service, CREATE_ORDER, handle_create_order)
on(service, VERIFY_USER, handle_verify_user)
on(service, PROCESS_PAYMENT, handle_payment)
```

## Project Config

Configure engines and runtime in `evoid.toml`:

```toml
[project]
name = "my-api"
version = "0.1.0"

[runtime]
adapter = "asgi"
host = "0.0.0.0"

[engines]
schema = "native"
storage = "sqlite"
cache = "memory"
logger = "loguru"
```
