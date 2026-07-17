---
title: 'Serialization'
description: 'Use any serialization library with EVOID — Pydantic, msgspec, or your own.'
---

# Serialization

EVOID provides the interface. You bring your own library.

## The Principle

IOP is about Intent + Pipeline. Serialization is HOW you move data in/out — that's your choice, not EVOID's.

EVOID defines one protocol:

```python
class Serializer(Protocol):
    def encode(self, data: Any) -> bytes: ...
    def decode(self, data: bytes, schema: type | None = None) -> Any: ...
```

Two methods. That's the entire contract.

## Default: stdlib json

No dependencies needed:

```python
from evoid.engines.serializer import get_serializer

serializer = get_serializer()  # auto-detects best available

# Encode
body = serializer.encode({"name": "Alice", "age": 30})

# Decode with schema
from pydantic import BaseModel

class User(BaseModel):
    name: str
    age: int

user = serializer.decode(body, schema=User)
```

## With Pydantic

If Pydantic is installed, EVOID uses it automatically:

```python
from pydantic import BaseModel, Field

class CreateUser(BaseModel):
    name: str = Field(min_length=1)
    email: str
    age: int = Field(ge=0, le=150)

# Decode + validate in one step
body = b'{"name": "Alice", "email": "alice@example.com", "age": 30}'
user = serializer.decode(body, schema=CreateUser)
# user is a validated Pydantic model
```

## With msgspec

For maximum performance:

```python
import msgspec

class User(msgspec.Struct):
    name: str
    age: int

# Fastest JSON encoding in Python
body = serializer.encode(User(name="Alice", age=30))
user = serializer.decode(body, schema=User)
```

## Custom Serializer

Implement the protocol with your preferred library:

```python
from evoid.engines.serializer import set_serializer

class MyCustomSerializer:
    def encode(self, data):
        # Your encoding logic
        ...

    def decode(self, data, schema=None):
        # Your decoding logic
        ...

set_serializer(MyCustomSerializer())
```

## Auto-Detection Priority

When you call `get_serializer()`, EVOID picks the best available:

1. **msgspec** — fastest (if installed)
2. **orjson** — very fast (if installed)
3. **pydantic** — with validation (if installed)
4. **stdlib json** — always available (fallback)

## Native IOP Style

In native IOP, serialization is a processor concern:

```python
from evoid.native import create_service, on
from evoid import Intent, Level, Context
from evoid.engines.serializer import get_serializer

app = create_service("api")
serializer = get_serializer()

# Processor: decode request body
async def decode_body(ctx: Context) -> dict:
    raw = ctx.metadata.get("body_raw", b"")
    ctx.metadata["body"] = serializer.decode(raw)
    return {"decoded": True}

# Intent with decoder in pipeline
CREATE_USER = Intent(
    name="POST:/users",
    level=Level.STANDARD,
    metadata={
        "method": "POST",
        "path": "/users",
        "processors": ("decode_body",),
    },
)

# Handler — receives decoded data
async def handle_create_user(intent: Intent) -> dict:
    body = intent.metadata["body"]
    return {"status": "created", "name": body["name"]}

on(app, CREATE_USER, handle_create_user)
```

## In Adapter

Adapters use the serializer to encode responses:

```python
from evoid.engines.serializer import get_serializer

serializer = get_serializer()

async def send_response(result):
    body = serializer.encode(result.value)
    return Response(content=body, media_type="application/json")
```

## Extra Data Types

Handle UUID, datetime, Decimal in handlers:

```python
from uuid import UUID
from datetime import datetime
from decimal import Decimal
from pydantic import BaseModel, Field

class Payment(BaseModel):
    amount: Decimal = Field(ge=Decimal("0.01"), max_digits=10, decimal_places=2)
    currency: str = "USD"
    created_at: datetime

class User(BaseModel):
    id: UUID
    name: str
    created_at: datetime
```

!!! tip "String conversion"
    UUIDs are automatically converted from string format in URLs and JSON.

## Native IOP Type Conversion

In IOP, type conversion belongs in a **processor**:

```python
from uuid import UUID
from datetime import datetime
from decimal import Decimal
from evoid.native import create_service, on
from evoid import Intent, Level, Context

app = create_service("api")

async def convert_payment_types(ctx: Context) -> dict:
    body = ctx.metadata.get("body", {})
    ctx.metadata["body"] = {
        "amount": Decimal(str(body.get("amount", "0.00"))),
        "payment_id": UUID(body.get("payment_id", "")),
        "created_at": datetime.fromisoformat(body.get("created_at", "")),
    }
    return {"converted": True}

CREATE_PAYMENT = Intent(
    name="POST:/payments",
    level=Level.STANDARD,
    metadata={
        "method": "POST",
        "path": "/payments",
        "processors": ("convert_payment_types",),
    },
)

async def handle_create_payment(intent: Intent) -> dict:
    body = intent.metadata["body"]
    return {"status": "processed", "amount": str(body["amount"])}

on(app, CREATE_PAYMENT, handle_create_payment)
```

## Summary

| Library | Install | Speed | Validation |
|---------|---------|-------|------------|
| stdlib json | built-in | baseline | no |
| pydantic | `pip install pydantic` | good | yes |
| msgspec | `pip install msgspec` | fastest | yes |
| orjson | `pip install orjson` | very fast | no |

!!! tip "IOP principle"
    EVOID doesn't care which library you use. Just implement the protocol and register it. The pipeline runs the same way regardless.
