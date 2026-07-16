---
title: 'Body Updates'
description: 'PATCH-style partial updates for request bodies.'
---

# Body Updates

PATCH-style partial updates for request bodies.

## Basic Partial Updates

Receive partial body data and merge with existing data:

```python
from pydantic import BaseModel, Field
from evoid.web.route import Service, patch

class UserUpdate(BaseModel):
    name: str | None = None
    email: str | None = None
    age: int | None = Field(default=None, ge=0, le=150)

# In-memory database
users_db = {
    1: {"id": 1, "name": "Alice", "email": "alice@example.com", "age": 30}
}

app = Service("api")

@app.patch("/users/{user_id}")
async def update_user(user_id: int, updates: UserUpdate):
    if user_id not in users_db:
        raise ValueError("User not found")
    
    # Merge updates with existing data
    existing = users_db[user_id]
    update_data = updates.model_dump(exclude_unset=True)
    existing.update(update_data)
    
    return {"status": "updated", "user": existing}
```

!!! info "exclude_unset"
    Use `model_dump(exclude_unset=True)` to only include fields that were explicitly set.

## Required vs Optional Fields

Mix required and optional fields in updates:

```python
from pydantic import BaseModel, Field
from evoid.web.route import Service, patch

class ProductUpdate(BaseModel):
    # Required field
    version: str
    
    # Optional fields
    name: str | None = None
    price: float | None = Field(default=None, gt=0)

app = Service("api")

@app.patch("/products/{product_id}")
async def update_product(product_id: int, updates: ProductUpdate):
    # version is always required, others are optional
    return {
        "status": "updated",
        "product_id": product_id,
        "version": updates.version,
        "changes": updates.model_dump(exclude_unset=True)
    }
```

## Native IOP Style

In IOP, validation and data merging belong in **processors**:

```python
from evoid.native import create_service, on
from evoid import Intent, Level, Context

app = create_service("api")

# Simulated database
users_db = {
    1: {"id": 1, "name": "Alice", "email": "alice@example.com", "age": 30}
}

# 1. Processor: validate user exists
async def validate_user_exists(ctx: Context) -> dict:
    user_id = int(ctx.metadata.get("path_params", {}).get("user_id", 0))
    if user_id not in users_db:
        raise ValueError("User not found")
    ctx.state["existing_user"] = users_db[user_id].copy()
    return {"validated": True}

# 2. Intent with validator in pipeline
UPDATE_USER = Intent(
    name="PATCH:/users",
    level=Level.STANDARD,
    metadata={
        "method": "PATCH",
        "path": "/users/{user_id}",
        "processors": ("validate_user_exists",),
    },
)

# 3. Handler — only merge and business logic
async def handle_update_user(intent: Intent) -> dict:
    body = intent.metadata.get("body", {})
    existing = intent.state["existing_user"]  # from processor

    # Merge non-None values
    for key, value in body.items():
        if value is not None:
            existing[key] = value

    users_db[int(intent.metadata["path_params"]["user_id"])] = existing
    return {"status": "updated", "user": existing}

on(app, UPDATE_USER, handle_update_user)
```

## @controller Style

```python
from pydantic import BaseModel, Field
from evoid.web.controller import Service, Controller, PATCH

class SettingsUpdate(BaseModel):
    theme: str | None = None
    language: str | None = None
    notifications: bool | None = None

# Simulated settings
settings_db = {"theme": "light", "language": "en", "notifications": True}

app = Service("api")

@Controller("/settings")
class SettingsController:
    @PATCH("/")
    async def update_settings(self, updates: SettingsUpdate):
        # Merge updates
        update_data = updates.model_dump(exclude_unset=True)
        settings_db.update(update_data)
        
        return {"status": "updated", "settings": settings_db}
```

## Summary

| Pattern | Use Case |
|---------|----------|
| `exclude_unset=True` | Only include explicitly provided fields |
| `None` defaults | Make fields optional in updates |
| Processor merge | Centralized merge logic |
| Deep merge | Nested object updates |