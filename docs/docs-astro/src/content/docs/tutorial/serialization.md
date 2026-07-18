---
title: 'Serialization'
description: 'JSON encoding, custom serializers, schema export for AI agents.'
---

# Serialization

JSON encoding, custom serializers, schema export for AI agents.

## Default JSON Serialization

EVOID returns dicts — the adapter handles JSON encoding:

```python
@get("/menu")
async def list_menu() -> dict:
    return {"menu": MENU}  # Automatically serialized to JSON
```

## What Happens Under the Hood

Serialization happens at two levels:

1. **Pipeline level**: Your handler returns a Python dict
2. **Adapter level**: The ASGI adapter converts dict → JSON response

```python
# Your handler returns:
return {"menu": [{"name": "BLT", "price": 8.99}]}

# The adapter does:
import json
response_body = json.dumps({"menu": [{"name": "BLT", "price": 8.99}]})
# Sets Content-Type: application/json
```

The runtime doesn't serialize — it passes your dict to the adapter. The adapter decides the format (JSON,_msgpack, etc.).

## Pydantic Models

Use Pydantic for structured serialization:

```python
from pydantic import BaseModel
from datetime import datetime

class OrderResponse(BaseModel):
    id: int
    sandwich: str
    quantity: int
    total: float
    created_at: datetime = datetime.now()

@get("/orders/{order_id}")
async def get_order(order_id: int) -> dict:
    order = find_order(order_id)
    return OrderResponse(**order).model_dump()
```

## Custom Serializers

For complex types, register a custom serializer:

```python
from evoid.engines.serializer import register_serializer

class Money:
    def __init__(self, amount: float, currency: str = "USD"):
        self.amount = amount
        self.currency = currency

def serialize_money(obj):
    if isinstance(obj, Money):
        return {"amount": obj.amount, "currency": obj.currency}
    return None

register_serializer("money", serialize_money)
```

## Schema Export

Export Intent schemas for documentation or AI agents:

```python
from evoid import export_schemas, export_json_schemas

# Python objects
schemas = export_schemas()
for name, schema in schemas.items():
    print(f"{name}: level={schema.level}, fields={schema.metadata_fields}")

# JSON Schema (for OpenAPI, MCP, etc.)
json_schemas = export_json_schemas()
# {"create_order": {"type": "object", "properties": {...}}}
```

## Debugging Serialization

When JSON encoding fails:

```python
import json

@get("/debug")
async def debug_endpoint() -> dict:
    data = {"menu": MENU}
    try:
        json.dumps(data)
    except TypeError as e:
        print(f"Serialization error: {e}")
        # Fix: convert non-serializable types
    return data
```

## What You Learned

| Concept | What It Is |
|---------|-----------|
| Default JSON | Dicts auto-serialize to JSON |
| Pydantic models | Structured serialization with validation |
| Custom serializers | Handle complex types |
| Schema export | JSON Schema for docs/AI |
| Debugging | Find and fix serialization issues |

## Next: Shipping Online

Let's deploy Sandy's online shop — [Shipping Online](shipping-online.md).
