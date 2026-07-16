---
title: 'Body Multiple Parameters'
description: 'Handle multiple body fields, and combine them with path and query parameters.'
---

# Body Multiple Parameters

Handle multiple body fields, and combine them with path and query parameters.

## @route Style

Body fields are matched to function parameters by name:

```python
from evoid.web.route import Service, post

app = Service("api")

@app.post("/users")
async def create_user(name: str, email: str, age: int, role: str = "viewer") -> dict:
    return {
        "status": "created",
        "name": name,
        "email": email,
        "age": age,
        "role": role,
    }
```

```bash
curl -X POST http://localhost:8000/users \
  -H "Content-Type: application/json" \
  -d '{"name": "Alice", "email": "alice@example.com", "age": 30}'

# {"status": "created", "name": "Alice", "email": "alice@example.com", "age": 30, "role": "viewer"}
```

## Combining Path + Body

Path parameters and body fields are matched separately — EVOID detects them by source:

```python
@app.put("/users/{user_id}")
async def update_user(user_id: int, name: str, email: str, bio: str | None = None) -> dict:
    # user_id comes from the URL path
    # name, email, bio come from the request body
    result = {"id": user_id, "name": name, "email": email}
    if bio:
        result["bio"] = bio
    return result
```

```bash
curl -X PUT http://localhost:8000/users/42 \
  -H "Content-Type: application/json" \
  -d '{"name": "Bob", "email": "bob@example.com", "bio": "Developer"}'
```

## Combining Path + Query + Body

All three sources work together:

```python
@app.post("/users/{org_id}/invite")
async def invite_user(
    org_id: int,          # path parameter
    role: str = "viewer", # query parameter
    name: str = "",       # body field
    email: str = "",      # body field
) -> dict:
    return {
        "org_id": org_id,
        "name": name,
        "email": email,
        "role": role,
    }
```

```bash
curl -X POST "http://localhost:8000/users/5/invite?role=admin" \
  -H "Content-Type: application/json" \
  -d '{"name": "Eve", "email": "eve@example.com"}'
```

## @controller Style

Same pattern in controllers:

```python
from evoid.web.controller import Service, Controller, POST

app = Service("api")

@Controller("/orders")
class OrderController:
    @POST("/items/{item_id}")
    async def add_item(
        self, item_id: int, quantity: int, color: str = "white"
    ) -> dict:
        return {
            "item_id": item_id,
            "quantity": quantity,
            "color": color,
        }
```

## Native Style

With native IOP, body data comes from `intent.metadata['body']`. Access multiple fields from the dict:

```python
from evoid import Intent, Level, add_intent

CREATE_USER = Intent(
    name="create_user",
    level=Level.STANDARD,
    metadata={"method": "POST", "path": "/users/{org_id}"},
)

async def handle_create_user(intent: Intent) -> dict:
    org_id = intent.metadata.get("org_id")
    body = intent.metadata.get("body", {})

    name = body.get("name")
    email = body.get("email")
    role = body.get("role", "viewer")

    return {
        "org_id": org_id,
        "name": name,
        "email": email,
        "role": role,
    }

add_intent(CREATE_USER, handle_create_user)
```

!!! tip "Accessing body data"
    In native style, body data is always a dict. Use `.get()` with defaults to handle missing fields gracefully.

## Typed Body (Pydantic Models)

For complex bodies, define a Pydantic model:

```python
from pydantic import BaseModel
from evoid.web.route import Service, post

class UserCreate(BaseModel):
    name: str
    email: str
    age: int
    role: str = "viewer"

app = Service("api")

@app.post("/users")
async def create_user(user: UserCreate) -> dict:
    return {
        "status": "created",
        "name": user.name,
        "email": user.email,
        "age": user.age,
        "role": user.role,
    }
```

This validates the full body structure and provides type hints and IDE autocompletion.
