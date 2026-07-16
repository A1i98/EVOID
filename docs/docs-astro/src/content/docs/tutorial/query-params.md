---
title: 'Query Parameters'
description: 'Handle URL query string parameters in your EVOID services.'
---

# Query Parameters

Handle URL query string parameters — the key-value pairs after `?` in a URL.

## Basic Usage

Query parameters are function parameters that are NOT part of the path:

```python
from evoid.web.route import Service, get

app = Service("api")

fake_items_db = [{"item_name": "Foo"}, {"item_name": "Bar"}, {"item_name": "Baz"}]

@app.get("/items/")
async def read_items(skip: int = 0, limit: int = 10):
    return fake_items_db[skip : skip + limit]
```

When you visit `/items/?skip=0&limit=10`, the handler receives `skip=0` and `limit=10`.

## Defaults

Query parameters are optional by default — they use the default value when not provided:

```python
@app.get("/items/")
async def read_items(skip: int = 0, limit: int = 10):
    # /items/         → skip=0, limit=10
    # /items/?skip=20 → skip=20, limit=10
    return fake_items_db[skip : skip + limit]
```

## Optional Parameters

Set default to `None` to make a parameter truly optional:

```python
@app.get("/items/{item_id}")
async def read_item(item_id: str, q: str | None = None):
    if q:
        return {"item_id": item_id, "q": q}
    return {"item_id": item_id}
```

EVOID automatically detects which parameters are path parameters (from the URL pattern) and which are query parameters.

## Type Conversion

EVOID converts query parameters to the annotated type:

```python
@app.get("/items/{item_id}")
async def read_item(item_id: str, q: str | None = None, short: bool = False):
    item = {"item_id": item_id}
    if q:
        item.update({"q": q})
    if not short:
        item.update({"description": "This is an amazing item"})
    return item
```

Boolean conversion accepts: `true`, `1`, `yes`, `on` (case-insensitive) as `True`.

## Multiple Path and Query Parameters

You can combine path and query parameters in any order — EVOID detects them by name:

```python
@app.get("/users/{user_id}/items/{item_id}")
async def read_user_item(
    user_id: int, item_id: str, q: str | None = None, short: bool = False
):
    item = {"item_id": item_id, "owner_id": user_id}
    if q:
        item.update({"q": q})
    if not short:
        item.update({"description": "This is an amazing item"})
    return item
```

## Required Query Parameters

Omit the default value to make a query parameter required:

```python
@app.get("/items/{item_id}")
async def read_user_item(item_id: str, needy: str):
    item = {"item_id": item_id, "needy": needy}
    return item
```

If `needy` is not provided, EVOID returns a validation error:

```json
{
    "detail": [
        {
            "type": "missing",
            "loc": ["query", "needy"],
            "msg": "Field required",
            "input": null
        }
    ]
}
```

## In Native Style

With native IOP, query parameters come from intent metadata:

```python
from evoid.native import create_service, on
from evoid import Intent, Level

app = create_service("api")

GET_ITEMS = Intent(
    name="GET:/items",
    level=Level.STANDARD,
    metadata={"method": "GET", "path": "/items"},
)

async def handle_get_items(intent: Intent) -> list:
    params = intent.metadata.get("params", {})
    skip = int(params.get("skip", 0))
    limit = int(params.get("limit", 10))
    return fake_items_db[skip : skip + limit]

on(app, GET_ITEMS, handle_get_items)
```

## In @controller Style

```python
from evoid.web.controller import Service, Controller, GET

app = Service("api")

@Controller("/items")
class ItemController:
    @GET("/")
    async def read_items(self, skip: int = 0, limit: int = 10):
        return fake_items_db[skip : skip + limit]
```
