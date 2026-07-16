---
title: "@controller Style"
description: "Class-based syntax. Familiar if you have used NestJS or Django REST Framework."
---

# @controller Style

Class-based syntax. Familiar if you've used NestJS or Django REST Framework. Groups related routes under a controller with a URL prefix.

## Basic Usage

```python
from evoid.web.controller import Service, Controller, GET, POST, PUT, DELETE

app = Service("my-api")

@Controller("/users")
class UserController:
    @GET("/")
    async def list_users(self) -> dict:
        return {"users": []}

    @GET("/{user_id}")
    async def get_user(self, user_id: int) -> dict:
        return {"id": user_id, "name": "Alice"}

    @POST("/")
    async def create_user(self, name: str, email: str) -> dict:
        return {"status": "created", "name": name}

    @PUT("/{user_id}")
    async def update_user(self, user_id: int, name: str) -> dict:
        return {"id": user_id, "name": name}

    @DELETE("/{user_id}")
    async def delete_user(self, user_id: int) -> dict:
        return {"status": "deleted"}
```

## URL Prefix

The `@Controller` prefix is prepended to all routes:

```python
@Controller("/api/v1")
class ApiController:
    @GET("/users")
    async def list_users(self) -> dict:
        return {"users": []}
    # Route becomes: GET /api/v1/users
```

## Multiple Methods per Route

A single method can handle multiple HTTP methods:

```python
@Controller("/resources")
class ResourceController:
    @GET("/{id}")
    @POST("/")
    async def handle(self, id: int = None, **kwargs) -> dict:
        if id:
            return {"id": id}
        return {"status": "created"}
```

## Intent Levels

Set level per method or per controller:

```python
@Controller("/admin", level="critical")
class AdminController:
    @GET("/dashboard")
    async def dashboard(self) -> dict:
        return {"stats": {}}

    @GET("/logs", level="standard")
    async def logs(self) -> dict:
        return {"logs": []}
```

## Pipeline Extensions

Same API as `@route`:

```python
from evoid.web.controller import before, after, replace_pipeline

before("GET:/users/{user_id}", "rate_limit")
after("GET:/users/{user_id}", "audit_log")
replace_pipeline("GET:/users/{user_id}", ["cache", "fetch", "serialize"])
```

## Running

```python
from evoid.web.controller import run

await run(app, host="0.0.0.0", port=8000)
```

## When to Use

- Large APIs with many related endpoints
- Teams familiar with NestJS/Django REST
- Projects where grouping by resource matters
- Services with clear domain boundaries
