---
title: 'Inventory Service'
description: '@controller for grouping — inventory management across locations.'
---

# Inventory Service

@controller for grouping — inventory management across locations.

## @controller Syntax

Group related routes under a prefix:

```python
from evoid.web.controller import Service, Controller, GET, POST, PUT
from evoid import Intent, Level

app = Service("inventory-service")

@Controller("/inventory")
class InventoryController:
    @GET("/")
    async def list_inventory(self, location: str = "all") -> dict:
        return {"location": location, "items": []}

    @GET("/{item_id}")
    async def get_item(self, item_id: int) -> dict:
        return {"id": item_id, "name": "BLT Kit", "stock": 50}

    @POST("/restock")
    async def restock(self, item_id: int, qty: int = 0) -> dict:
        return {"status": "restocked", "item_id": item_id, "added": qty}

    @PUT("/{item_id}")
    async def update_stock(self, item_id: int, stock: int = 0) -> dict:
        return {"status": "updated", "item_id": item_id, "stock": stock}
```

## What @controller Does Under the Hood

```python
# @controller("/inventory") + @GET("/") creates:
INVENTORY_LIST = Intent(
    name="GET:/inventory/",
    level=Level.STANDARD,
    metadata={"method": "GET", "path": "/inventory/"},
)
```

Same as @route — Intents are auto-created. @controller just adds a prefix.

## @route vs @controller

| | @route | @controller |
|---|--------|-------------|
| Grouping | None | Prefix-based |
| Best for | Small APIs | Large APIs, domain grouping |
| Syntax | `@get("/path")` | `@Controller("/prefix")` class with `@GET`/`@POST` |

## Middleware on Controllers

```python
from evoid.web.controller import before, after

before("GET:/inventory/", "rate_limit")
after("GET:/inventory/", "log_response")
```

## What You Learned

| Concept | What It Is |
|---------|-----------|
| @controller | Group routes under a prefix |
| Prefix routing | Automatic path composition |
| Controller middleware | Apply to all routes in a controller |

## Next: Real-time Updates

Let's add live order tracking — [Real-time Updates](real-time.md).
