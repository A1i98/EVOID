---
title: 'Request Body'
description: 'Handle POST, PUT, and PATCH request data.'
---

# Request Body

Handle POST, PUT, and PATCH request data.

## Basic Usage

```python
from evoid.web.route import Service, post, put, delete

app = Service("api")

@post("/users")
async def create_user(name: str, email: str) -> dict:
    return {"status": "created", "name": name, "email": email}

@put("/users/{user_id}")
async def update_user(user_id: int, name: str, email: str) -> dict:
    return {"id": user_id, "name": name, "email": email}

@delete("/users/{user_id}")
async def delete_user(user_id: int) -> dict:
    return {"status": "deleted"}
```

## How It Works

!!! info "Request flow"
    When a POST request arrives:

1. EVOID parses the JSON body
2. Matches keys to your function parameters
3. Calls your function with the parsed data

```bash
curl -X POST http://localhost:8000/users \
  -H "Content-Type: application/json" \
  -d '{"name": "Alice", "email": "alice@example.com"}'

# {"status": "created", "name": "Alice", "email": "alice@example.com"}
```

## Combining Path and Body

```python
@put("/users/{user_id}")
async def update_user(user_id: int, name: str, email: str) -> dict:
    # user_id comes from the URL path
    # name and email come from the request body
    return {"id": user_id, "name": name, "email": email}
```

```bash
curl -X PUT http://localhost:8000/users/42 \
  -H "Content-Type: application/json" \
  -d '{"name": "Bob", "email": "bob@example.com"}'
```

## In @controller Style

```python
from evoid.web.controller import Service, Controller, POST, PUT

app = Service("api")

@Controller("/users")
class UserController:
    @POST("/")
    async def create_user(self, name: str, email: str) -> dict:
        return {"status": "created", "name": name}

    @PUT("/{user_id}")
    async def update_user(self, user_id: int, name: str) -> dict:
        return {"id": user_id, "name": name}
```

## In Native Style

Body data comes from intent metadata:

```python
from evoid import Intent, Level, add_intent

CREATE_USER = Intent(
    name="create_user",
    level=Level.STANDARD,
    metadata={"method": "POST", "path": "/users"},
)

async def handle_create(intent: Intent) -> dict:
    body = intent.metadata.get("body", {})
    name = body.get("name")
    email = body.get("email")
    return {"status": "created", "name": name}

add_intent(CREATE_USER, handle_create)
```

## Default Values

!!! tip "Optional parameters"
    Parameters with defaults become optional:

```python
@post("/users")
async def create_user(
    name: str,
    email: str,
    role: str = "viewer",
) -> dict:
    return {"name": name, "email": email, "role": role}
```
