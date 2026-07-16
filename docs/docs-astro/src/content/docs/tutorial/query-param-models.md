---
title: 'Query Parameter Models'
description: 'Validate query parameters using schemas and type hints.'
---

# Query Parameter Models

Validate query parameters using schemas and type hints for robust input handling.

## Basic Type Hints

EVOID automatically validates query parameters against their type hints:

```python
from evoid.web.route import Service, get

app = Service("api")

@app.get("/items/")
async def read_items(skip: int = 0, limit: int = 10):
    return {"skip": skip, "limit": limit}
```

!!! info "Validation"
    If `skip` is not an integer, EVOID returns a validation error with the expected type.

## Pydantic Models for Query Params

Use Pydantic models to validate complex query parameters:

```python
from pydantic import BaseModel, Field
from evoid.web.route import Service, get

class ItemQuery(BaseModel):
    skip: int = Field(0, ge=0)
    limit: int = Field(10, ge=1, le=100)
    q: str | None = None
    category: str | None = None

app = Service("api")

@app.get("/items/")
async def read_items(query: ItemQuery):
    return {
        "skip": query.skip,
        "limit": query.limit,
        "q": query.q,
        "category": query.category
    }
```

!!! tip "Field constraints"
    Use `ge`, `le`, `min_length`, `max_length` in `Field()` to add constraints.

## Processor-Based Validation

For custom validation logic, use a processor in the pipeline:

```python
from evoid.web.route import Service, get, before
from evoid.core import Context

async def validate_item_query(ctx: Context) -> dict:
    params = ctx.metadata.get("params", {})
    
    # Custom validation
    if "category" in params and params["category"] not in ["electronics", "books"]:
        raise ValueError(f"Invalid category: {params['category']}")
    
    # Transform params
    ctx.metadata["params"]["skip"] = max(0, int(params.get("skip", 0)))
    ctx.metadata["params"]["limit"] = min(100, int(params.get("limit", 10)))
    
    return {"validated": True}

app = Service("api")

@app.get("/items/")
async def read_items(skip: int = 0, limit: int = 10):
    return {"skip": skip, "limit": limit}

before("GET:/items", "validate_item_query")
```

## Native IOP Style

In IOP, validation belongs in a **processor** — not the handler. The handler only does business logic:

```python
from evoid.native import create_service, on
from evoid import Intent, Level, Context

app = create_service("api")

# 1. Define a validator processor
async def validate_pagination(ctx: Context) -> dict:
    params = ctx.metadata.get("params", {})
    ctx.metadata["params"] = {
        "skip": max(0, int(params.get("skip", 0))),
        "limit": min(100, int(params.get("limit", 10))),
    }
    return {"validated": True}

# 2. Intent with custom pipeline (validator first)
GET_ITEMS = Intent(
    name="GET:/items",
    level=Level.STANDARD,
    metadata={
        "method": "GET",
        "path": "/items",
        "processors": ("validate_pagination",),  # validator runs first
    },
)

# 3. Handler — only business logic, no validation
async def handle_get_items(intent: Intent) -> dict:
    params = intent.metadata["params"]  # already validated
    return {"skip": params["skip"], "limit": params["limit"]}

on(app, GET_ITEMS, handle_get_items)
```

!!! tip "IOP principle"
    Processors handle cross-cutting concerns (validation, auth, logging). Handlers handle business logic. This separation is the core of IOP.

## @controller Style

```python
from evoid.web.controller import Service, Controller, GET
from pydantic import BaseModel, Field

class PaginationQuery(BaseModel):
    page: int = Field(1, ge=1)
    per_page: int = Field(10, ge=1, le=50)

app = Service("api")

@Controller("/items")
class ItemController:
    @GET("/")
    async def list_items(self, query: PaginationQuery):
        return {
            "page": query.page,
            "per_page": query.per_page,
            "items": []
        }
```

## Summary

| Approach | Use Case |
|----------|----------|
| Type hints | Simple parameters with basic validation |
| Pydantic models | Complex parameters with constraints |
| Processor | Custom validation logic in pipeline (IOP way) |
| Native IOP | Intent + processor pipeline for full control |