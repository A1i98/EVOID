---
title: 'Controller Style'
description: 'Class-based routing for organizing large APIs.'
---

# Controller Style

Class-based routing for organizing large APIs.

## Basic Usage

```python
from evoid.web.controller import Service, Controller, GET, POST, PUT, DELETE

app = Service("api")

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
    # Route: GET /api/v1/users
```

## Multiple Controllers

```python
@Controller("/users")
class UserController:
    @GET("/")
    async def list(self) -> dict:
        return {"users": []}

@Controller("/orders")
class OrderController:
    @GET("/")
    async def list(self) -> dict:
        return {"orders": []}

@Controller("/products")
class ProductController:
    @GET("/")
    async def list(self) -> dict:
        return {"products": []}
```

## Intent Levels Per Controller

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

## When to Use @controller vs @route

| Scenario | Use |
|----------|-----|
| Small API (< 10 routes) | `@route` |
| Large API with many resources | `@controller` |
| Team familiar with NestJS | `@controller` |
| Quick prototyping | `@route` |
