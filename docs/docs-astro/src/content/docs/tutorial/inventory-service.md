---
title: 'Inventory Service'
description: '@controller for grouping — inventory management across locations.'
---

# Inventory Service

@controller for grouping — inventory management across locations.

## @controller Syntax

Group related routes under a prefix:

```python
from evoid.web.controller import Controller
from evoid import Intent, Level

inventory = Controller("/inventory")

@inventory.get("/")
async def list_inventory(intent):
    location = intent.metadata.get("location", "all")
    return {"location": location, "items": []}

@inventory.get("/{item_id}")
async def get_item(intent):
    item_id = intent.metadata.get("item_id")
    return {"id": item_id, "name": "BLT Kit", "stock": 50}

@inventory.post("/restock")
async def restock(intent):
    body = intent.metadata.get("body", {})
    item_id = body.get("item_id")
    qty = body.get("qty", 0)
    return {"status": "restocked", "item_id": item_id, "added": qty}

@inventory.put("/{item_id}")
async def update_stock(intent):
    item_id = intent.metadata.get("item_id")
    body = intent.metadata.get("body", {})
    new_stock = body.get("stock", 0)
    return {"status": "updated", "item_id": item_id, "stock": new_stock}
```

## What @controller Does Under the Hood

```python
# @controller("/inventory") + @get("/") creates:
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
| Syntax | `@get("/path")` | `Controller("/prefix")` + `@.get("/path")` |

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
