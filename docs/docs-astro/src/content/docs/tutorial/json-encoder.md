---
title: 'JSON Encoder'
description: 'Custom serialization for Pydantic models, dataclasses, and custom types.'
---

# JSON Encoder

Custom serialization for Pydantic models, dataclasses, and custom types.

## Default Serialization

EVOID automatically serializes common types to JSON:

```python
from datetime import datetime
from uuid import UUID
from pydantic import BaseModel
from evoid.web.route import Service, get

class User(BaseModel):
    id: UUID
    name: str
    created_at: datetime

app = Service("api")

@app.get("/users/{user_id}")
async def get_user(user_id: UUID):
    return {
        "id": user_id,
        "name": "Alice",
        "created_at": datetime.now()
    }
```

!!! info "Automatic conversion"
    UUIDs become strings, datetimes become ISO format strings, and Pydantic models become dicts.

## Pydantic Model Serialization

Control serialization with Pydantic's `model_dump`:

```python
from pydantic import BaseModel, Field
from evoid.web.route import Service, get

class Product(BaseModel):
    name: str
    price: float
    tags: list[str] = []
    internal_id: int = Field(exclude=True)

app = Service("api")

@app.get("/products/{product_id}")
async def get_product(product_id: int):
    product = Product(name="Widget", price=9.99, tags=["sale"], internal_id=123)
    return product.model_dump()  # Excludes internal_id

@app.get("/products/{product_id}/raw")
async def get_product_raw(product_id: int):
    product = Product(name="Widget", price=9.99, tags=["sale"], internal_id=123)
    return product.model_dump(mode="json")  # JSON-serializable format
```

## Dataclass Serialization

Serialize Python dataclasses:

```python
from dataclasses import dataclass, asdict
from evoid.web.route import Service, get

@dataclass
class Config:
    debug: bool = False
    version: str = "1.0.0"
    max_connections: int = 100

app = Service("api")

@app.get("/config/")
async def get_config():
    config = Config(debug=True, version="2.0.0")
    return asdict(config)
```

## Custom Type Serialization

Register custom serializers for special types:

```python
from evoid.core import register_serializer
from datetime import datetime
from typing import Any

def serialize_datetime(obj: datetime) -> str:
    return obj.strftime("%Y-%m-%d %H:%M:%S")

register_serializer(datetime, serialize_datetime)

# Now datetime objects serialize with custom format
```

## Native IOP Style

In native IOP, manually serialize response data:

```python
from uuid import UUID
from datetime import datetime
from evoid.native import create_service, on
from evoid import Intent, Level

app = create_service("api")

GET_USER = Intent(
    name="GET:/users",
    level=Level.STANDARD,
    metadata={"method": "GET", "path": "/users"},
)

async def handle_get_user(intent: Intent) -> dict:
    # Manual serialization
    user_id = UUID("123e4567-e89b-12d3-a456-426614174000")
    created_at = datetime.now()
    
    return {
        "id": str(user_id),  # Convert UUID to string
        "name": "Alice",
        "created_at": created_at.isoformat()  # Convert datetime to string
    }

on(app, GET_USER, handle_get_user)
```

## Summary

| Type | Default Serialization | Custom Approach |
|------|----------------------|-----------------|
| Pydantic models | Dict with `model_dump()` | `model_dump(mode="json")` |
| Dataclasses | Dict with `asdict()` | Manual conversion |
| datetime | ISO format string | Custom format function |
| UUID | String | `str(uuid)` |
| Custom types | TypeError | Register serializer |