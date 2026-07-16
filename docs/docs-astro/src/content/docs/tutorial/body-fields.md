---
title: 'Body Fields'
description: 'Field-level validation, aliases, default values, and constraints for request bodies.'
---

# Body Fields

Field-level validation, aliases, default values, and constraints for request bodies.

## Basic Field Validation

EVOID validates body fields using type hints and Pydantic models:

```python
from pydantic import BaseModel, Field
from evoid.web.route import Service, post

class UserCreate(BaseModel):
    name: str
    email: str
    age: int = Field(ge=0, le=150)
    is_active: bool = True

app = Service("api")

@app.post("/users/")
async def create_user(user: UserCreate):
    return {"status": "created", "user": user.model_dump()}
```

!!! info "Required vs optional"
    Fields without default values are required. Fields with defaults are optional.

## Field Constraints

Use `Field()` to add constraints to individual fields:

```python
from pydantic import BaseModel, Field

class Product(BaseModel):
    name: str = Field(min_length=1, max_length=100)
    price: float = Field(gt=0, le=10000)
    sku: str = Field(pattern=r"^[A-Z]{3}-\d{4}$")
```

!!! tip "Common constraints"
    - `ge`, `le`: Greater/less than or equal
    - `gt`, `lt`: Greater/less than
    - `min_length`, `max_length`: String length
    - `pattern`: Regex pattern for strings

## Field Aliases

Map different field names for input and output:

```python
from pydantic import BaseModel, Field
from evoid.web.route import Service, post

class UserInput(BaseModel):
    model_config = {"populate_by_name": True}
    
    name: str = Field(alias="user_name")
    email_address: str = Field(alias="email")

app = Service("api")

@app.post("/users/")
async def create_user(user: UserInput):
    return {
        "name": user.name,
        "email": user.email_address
    }
```

## Native IOP Style

In IOP, body validation belongs in a **processor**. The handler only does business logic:

```python
from evoid.native import create_service, on
from evoid import Intent, Level, Context

app = create_service("api")

# 1. Validator processor — validates body fields
async def validate_user_body(ctx: Context) -> dict:
    body = ctx.metadata.get("body", {})
    required = ["name", "email"]
    missing = [f for f in required if f not in body]
    if missing:
        raise ValueError(f"Missing fields: {', '.join(missing)}")
    return {"validated": True}

# 2. Intent with custom pipeline
CREATE_USER = Intent(
    name="POST:/users",
    level=Level.STANDARD,
    metadata={
        "method": "POST",
        "path": "/users",
        "processors": ("validate_user_body",),
    },
)

# 3. Handler — only business logic
async def handle_create_user(intent: Intent) -> dict:
    body = intent.metadata["body"]  # already validated
    return {"status": "created", "name": body["name"], "email": body["email"]}

on(app, CREATE_USER, handle_create_user)
```

!!! tip "IOP principle"
    The processor ensures data is valid BEFORE the handler runs. Handlers never deal with invalid data.

## @controller Style

```python
from evoid.web.controller import Service, Controller, POST
from pydantic import BaseModel, Field

class OrderInput(BaseModel):
    product_id: str = Field(min_length=1)
    quantity: int = Field(ge=1, le=100)

app = Service("api")

@Controller("/orders")
class OrderController:
    @POST("/")
    async def create_order(self, order: OrderInput):
        return {
            "status": "created",
            "product_id": order.product_id,
            "quantity": order.quantity
        }
```

## Summary

| Feature | Example |
|---------|---------|
| Required field | `name: str` |
| Optional with default | `age: int = 0` |
| Constrained field | `price: float = Field(gt=0)` |
| Field alias | `email: str = Field(alias="email_address")` |
| Custom validation | Processor in pipeline |