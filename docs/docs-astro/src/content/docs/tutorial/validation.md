---
title: 'Validation'
description: 'Validate requests with Pydantic, schema engines, and custom processors.'
---

# Validation

Validate requests with Pydantic, schema engines, and custom processors.

## Pydantic Validation

The simplest approach — Pydantic validates automatically:

```python
from pydantic import BaseModel, Field, field_validator

class CreateOrder(BaseModel):
    sandwich: str = Field(min_length=1)
    quantity: int = Field(ge=1, le=100)
    customer_name: str = Field(min_length=2, max_length=100)

    @field_validator("sandwich")
    @classmethod
    def validate_sandwich(cls, v):
        allowed = ["BLT", "Club", "Veggie", "Reuben", "Philly"]
        if v not in allowed:
            raise ValueError(f"Must be one of: {', '.join(allowed)}")
        return v

@post("/orders")
async def create_order(order: CreateOrder) -> dict:
    return {"status": "created", "order": order.model_dump()}
```

```bash
curl -X POST http://localhost:8000/orders \
  -H "Content-Type: application/json" \
  -d '{"sandwich": "INVALID", "quantity": 0}'
# {"detail": "Must be one of: BLT, Club, Veggie, Reuben, Philly"}
```

## Custom Validation Processors

For validation that depends on external data, use processors:

```python
from evoid import register_processor
from evoid.core import Context

async def validate_inventory(intent: Intent, ctx: Context) -> dict:
    """Check if sandwich is in stock."""
    body = ctx.metadata.get("body", {})
    sandwich = body.get("sandwich")
    qty = body.get("quantity", 1)

    # Check inventory (simplified)
    in_stock = sandwich in ["BLT", "Club", "Veggie"]
    if not in_stock:
        raise ValueError(f"'{sandwich}' is not available")

    ctx.state["validated"] = True
    return {"validated": True}

register_processor("validate_inventory", validate_inventory)
```

Wire it to the order endpoint:

```python
from evoid.core.extend import before

before("POST:/orders", "validate_inventory")
```

## Validation as a Pipeline Step

Add validation to the Intent's pipeline:

```python
from evoid import Intent, Level
from evoid.core.extend import add_intent_with_pipeline

CREATE_ORDER = Intent(name="create_order", level=Level.STANDARD)

async def handle_create_order(intent: Intent) -> dict:
    body = intent.metadata.get("body", {})
    return {"status": "created", "order": body}

add_intent_with_pipeline(
    CREATE_ORDER,
    processors=["validate_inventory", "create_order"],
    handler=handle_create_order,
)
```

## Schema Engine

EVOID can auto-generate JSON Schema from your Intents:

```python
from evoid import export_json_schemas

schemas = export_json_schemas()
# {"create_order": {"type": "object", "properties": {...}, ...}}
```

Use this for API documentation, OpenAPI specs, or AI agent discovery.

## Response Validation

Validate responses too — catch bugs before they reach clients:

```python
from pydantic import BaseModel

class OrderResponse(BaseModel):
    id: int
    status: str
    total: float

async def validate_response(intent: Intent, ctx: Context) -> dict:
    """Validate the handler's output."""
    result = ctx.state.get("handler_result", {})
    OrderResponse(**result)  # Raises if invalid
    return {"response_valid": True}

register_processor("validate_response", validate_response)

after("POST:/orders", "validate_response")
```

## What You Learned

| Concept | What It Is |
|---------|-----------|
| Pydantic validation | Automatic from type hints and Field constraints |
| Custom validators | `@field_validator` for complex rules |
| Validation processors | Pipeline steps that check external data |
| Schema export | JSON Schema from Intents for docs/AI |
| Response validation | Validate output, not just input |

## Next: Error Handling

Let's handle errors properly — [Error Handling](error-handling.md).
