---
title: 'Body Nested Models'
description: 'Validate complex nested JSON structures in request bodies.'
---

# Body Nested Models

Validate complex nested JSON structures in request bodies.

## Basic Nested Models

Use Pydantic models to validate nested JSON structures:

```python
from pydantic import BaseModel, Field
from evoid.web.route import Service, post

class Address(BaseModel):
    street: str
    city: str
    state: str
    zip_code: str
    country: str = "US"

class User(BaseModel):
    name: str
    email: str
    address: Address
    phone: str | None = None

app = Service("api")

@app.post("/users/")
async def create_user(user: User):
    return {
        "status": "created",
        "user": {
            "name": user.name,
            "email": user.email,
            "city": user.address.city
        }
    }
```

!!! info "Nested validation"
    EVOID validates the entire nested structure. If `address` is missing fields, the request fails.

## Lists of Nested Models

Handle arrays of complex objects:

```python
from pydantic import BaseModel, Field
from evoid.web.route import Service, post

class Item(BaseModel):
    name: str
    quantity: int = Field(ge=1)
    price: float = Field(gt=0)

class Order(BaseModel):
    customer_id: str
    items: list[Item] = Field(min_length=1)
    notes: str = ""

app = Service("api")

@app.post("/orders/")
async def create_order(order: Order):
    total = sum(item.quantity * item.price for item in order.items)
    return {
        "status": "created",
        "customer_id": order.customer_id,
        "item_count": len(order.items),
        "total": total
    }
```

## Native IOP Style

In native IOP, manually validate nested structures:

```python
from evoid.native import create_service, on
from evoid import Intent, Level, Context

app = create_service("api")

# 1. Processor validates nested structure
async def validate_order_body(ctx: Context) -> dict:
    body = ctx.metadata.get("body", {})
    if "customer_id" not in body:
        raise ValueError("customer_id is required")
    items = body.get("items", [])
    if not isinstance(items, list) or len(items) == 0:
        raise ValueError("items must be a non-empty list")
    for item in items:
        if "name" not in item or "quantity" not in item:
            raise ValueError("Each item needs name and quantity")
    return {"validated": True}

# 2. Intent with validator in pipeline
CREATE_ORDER = Intent(
    name="POST:/orders",
    level=Level.STANDARD,
    metadata={
        "method": "POST",
        "path": "/orders",
        "processors": ("validate_order_body",),
    },
)

# 3. Handler — only business logic
async def handle_create_order(intent: Intent) -> dict:
    body = intent.metadata["body"]  # already validated
    return {"status": "created", "customer_id": body["customer_id"]}

on(app, CREATE_ORDER, handle_create_order)
```

## @controller Style

```python
from evoid.web.controller import Service, Controller, POST
from pydantic import BaseModel, Field

class Item(BaseModel):
    name: str
    quantity: int = Field(ge=1)

class OrderRequest(BaseModel):
    customer_id: str
    items: list[Item] = Field(min_length=1)

app = Service("api")

@Controller("/orders")
class OrderController:
    @POST("/")
    async def create_order(self, order: OrderRequest):
        return {
            "status": "created",
            "customer_id": order.customer_id,
            "item_count": len(order.items)
        }
```

## Summary

| Pattern | Example |
|---------|---------|
| Simple nested | `address: Address` |
| List of models | `items: list[Item]` |
| Optional nested | `profile: Profile \| None` |
| Manual validation | Processor or native IOP handler |