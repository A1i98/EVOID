---
title: 'Path Parameters'
description: 'Extract dynamic values from URL paths.'
---

# Path Parameters

Extract dynamic values from URL paths.

## Basic Usage

Define path parameters with curly braces:

```python
from evoid.web.route import Service, get

app = Service("api")

@get("/users/{user_id}")
async def get_user(user_id: int) -> dict:
    return {"id": user_id, "name": f"User {user_id}"}

@get("/posts/{post_id}/comments/{comment_id}")
async def get_comment(post_id: int, comment_id: int) -> dict:
    return {"post": post_id, "comment": comment_id}
```

!!! info "Automatic handling"
    EVOID automatically:

1. Parses the URL path
2. Converts parameters to the annotated types
3. Passes them to your function

## Type Conversion

EVOID converts path parameters to the annotated type:

```python
@get("/items/{item_id}")
async def get_item(item_id: int) -> dict:
    # item_id is an int, not a string
    return {"id": item_id}

@get("/files/{path:path}")
async def get_file(path: str) -> dict:
    # path is a string (supports slashes)
    return {"path": path}
```

## Multiple Parameters

```python
@get("/users/{user_id}/posts/{post_id}")
async def get_user_post(user_id: int, post_id: int) -> dict:
    return {"user": user_id, "post": post_id}
```

## In Native Style

With native IOP, parameters come from intent metadata:

```python
from evoid import Intent, Level, add_intent

GET_USER = Intent(
    name="get_user",
    level=Level.STANDARD,
    metadata={"method": "GET", "path": "/users/{id}"},
)

async def handle_get_user(intent: Intent) -> dict:
    user_id = intent.metadata.get("id")
    return {"id": user_id}

add_intent(GET_USER, handle_get_user)
```

## In @controller Style

```python
from evoid.web.controller import Service, Controller, GET

app = Service("api")

@Controller("/users")
class UserController:
    @GET("/{user_id}")
    async def get_user(self, user_id: int) -> dict:
        return {"id": user_id}
```

## Combining with Query Parameters

!!! tip "Required vs optional"
    Path parameters are required. Query parameters are optional:

```python
@get("/users/{user_id}")
async def get_user(user_id: int, format: str = "json") -> dict:
    return {"id": user_id, "format": format}
```
