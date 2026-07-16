---
title: 'Response Status Code'
description: 'Control HTTP response status codes in your EVOID services.'
---

# Response Status Code

Control HTTP response status codes in your EVOID services.

## Default Behavior

All responses return **200 OK** by default:

```python
from evoid.web.route import Service, get

app = Service("api")

@get("/users/{user_id}")
async def get_user(user_id: int) -> dict:
    return {"id": user_id, "name": "Alice"}
```

## @route Style

Use the `status` parameter to return different codes:

```python
from evoid.web.route import Service, get, post, delete

app = Service("api")

@post("/users", status=201)
async def create_user(name: str, email: str) -> dict:
    return {"status": "created", "name": name, "email": email}

@get("/users/{user_id}")
async def get_user(user_id: int) -> dict:
    if user_id > 100:
        return {"detail": "User not found"}  # still 200
    return {"id": user_id, "name": "Alice"}

@delete("/users/{user_id}", status=204)
async def delete_user(user_id: int) -> dict:
    return {"status": "deleted"}
```

!!! info "Status codes you can use"
    Common codes: `200` (OK), `201` (Created), `204` (No Content), `400` (Bad Request), `404` (Not Found), `500` (Server Error).

## Returning Errors

To return error status codes, raise an exception in your handler:

```python
from evoid.web.route import Service, get

app = Service("api")

@get("/users/{user_id}")
async def get_user(user_id: int) -> dict:
    if user_id > 100:
        raise Exception("User not found")  # returns 500
    return {"id": user_id, "name": "Alice"}
```

!!! tip "Structured errors"
    For clean error responses, raise exceptions with status information — see [Handling Errors](/docs/tutorial/handling-errors) for details.

## @controller Style

Status codes work the same way with controllers:

```python
from evoid.web.controller import Service, Controller, GET, POST, DELETE

app = Service("api")

@Controller("/users")
class UserController:
    @POST("/", status=201)
    async def create_user(self, name: str, email: str) -> dict:
        return {"status": "created", "name": name}

    @GET("/{user_id}")
    async def get_user(self, user_id: int) -> dict:
        return {"id": user_id, "name": "Alice"}

    @DELETE("/{user_id}", status=204)
    async def delete_user(self, user_id: int) -> dict:
        return {"status": "deleted"}
```

## Native Style

With native IOP, set the status in the handler's return dict using the `status_code` key:

```python
from evoid import Intent, Level, add_intent

CREATE_USER = Intent(
    name="create_user",
    level=Level.STANDARD,
    metadata={"method": "POST", "path": "/users"},
)

async def handle_create_user(intent: Intent) -> dict:
    body = intent.metadata.get("body", {})
    name = body.get("name")
    return {
        "status": "created",
        "name": name,
        "status_code": 201,
    }

add_intent(CREATE_USER, handle_create_user)
```

## Summary

| Style | Status Code | Mechanism |
|-------|-------------|-----------|
| `@route` | `200` (default) | `status` parameter on decorator |
| `@route` | `201`, `204`, `4xx`, `5xx` | `status=XXX` parameter |
| `@controller` | Same as `@route` | `status` parameter on method decorator |
| Native | `200` (default) | Return `{"status_code": XXX}` in result |
