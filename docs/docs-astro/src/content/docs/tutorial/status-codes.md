---
title: 'Status Codes'
description: 'HTTP status codes — success, created, deleted, errors.'
---

# Status Codes

HTTP status codes — success, created, deleted, errors.

## Default Behavior

Handlers return 200 by default:

```python
@get("/menu/{item_id}")
async def get_item(item_id: int) -> dict:
    return {"id": item_id, "name": "BLT"}  # 200 OK
```

## Setting Status Codes

Use the `status` parameter on decorators:

```python
@post("/orders", status=201)
async def create_order(sandwich: str, qty: int = 1) -> dict:
    return {"status": "created", "sandwich": sandwich}

@delete("/orders/{order_id}", status=204)
async def delete_order(order_id: int) -> dict:
    return {}  # 204 No Content
```

## Native Style

In native IOP, return `status_code` in the result dict:

```python
from evoid import Intent, Level, add_intent

CREATE_ORDER = Intent(
    name="create_order",
    level=Level.STANDARD,
)

async def handle_create_order(intent: Intent) -> dict:
    body = intent.metadata.get("body", {})
    return {
        "status": "created",
        "order_id": 123,
        "status_code": 201,
    }

add_intent(CREATE_ORDER, handle_create_order)
```

## Error Status Codes

```python
@get("/orders/{order_id}")
async def get_order(order_id: int) -> dict:
    order = next((o for o in ORDERS if o["id"] == order_id), None)
    if not order:
        return {"error": "Not found", "status_code": 404}
    return order

@post("/orders")
async def create_order(sandwich: str, qty: int = 1) -> dict:
    if qty <= 0:
        return {"error": "Quantity must be positive", "status_code": 400}
    return {"status": "created", "status_code": 201}
```

## Status Code Summary

| Code | Meaning | When to Use |
|------|---------|-------------|
| 200 | OK | Successful GET, PUT |
| 201 | Created | Successful POST |
| 204 | No Content | Successful DELETE |
| 400 | Bad Request | Invalid input |
| 404 | Not Found | Resource doesn't exist |
| 500 | Server Error | Unexpected failure |

## Next: Configuration

Let's configure Sandy's app — [Configuration](configuration.md).
