---
title: 'Extra Data Types'
description: 'Handle UUID, datetime, date, time, timedelta, bytes, Decimal in handlers.'
---

# Extra Data Types

Handle UUID, datetime, date, time, timedelta, bytes, Decimal in handlers.

## UUID Fields

Use UUID for unique identifiers:

```python
from uuid import UUID
from pydantic import BaseModel
from evoid.web.route import Service, get, post

class User(BaseModel):
    id: UUID
    name: str
    email: str

app = Service("api")

@app.get("/users/{user_id}")
async def get_user(user_id: UUID):
    return {"user_id": str(user_id), "name": "Alice"}

@app.post("/users/")
async def create_user(user: User):
    return {"status": "created", "user_id": str(user.id)}
```

!!! tip "String conversion"
    UUIDs are automatically converted from string format in URLs and JSON.

## DateTime Fields

Handle datetime objects for timestamps:

```python
from datetime import datetime, timezone
from pydantic import BaseModel, Field
from evoid.web.route import Service, post

class Event(BaseModel):
    name: str
    start_time: datetime
    end_time: datetime | None = None
    timezone: str = "UTC"

app = Service("api")

@app.post("/events/")
async def create_event(event: Event):
    # Validate that end_time is after start_time
    if event.end_time and event.end_time <= event.start_time:
        raise ValueError("end_time must be after start_time")
    
    return {
        "status": "created",
        "event": event.name,
        "start": event.start_time.isoformat()
    }
```

## Decimal Fields

Use Decimal for precise numeric calculations:

```python
from decimal import Decimal
from pydantic import BaseModel, Field
from evoid.web.route import Service, post

class Payment(BaseModel):
    amount: Decimal = Field(ge=Decimal("0.01"), max_digits=10, decimal_places=2)
    currency: str = "USD"
    tax_rate: Decimal = Field(default=Decimal("0.0"), ge=Decimal("0"), le=Decimal("1"))

app = Service("api")

@app.post("/payments/")
async def process_payment(payment: Payment):
    tax = payment.amount * payment.tax_rate
    total = payment.amount + tax
    return {
        "status": "processed",
        "amount": str(payment.amount),
        "tax": str(tax),
        "total": str(total)
    }
```

## Native IOP Style

In IOP, type conversion belongs in a **processor** — handlers receive already-typed data:

```python
from uuid import UUID
from datetime import datetime
from decimal import Decimal
from evoid.native import create_service, on
from evoid import Intent, Level, Context

app = create_service("api")

# 1. Processor converts types automatically
async def convert_payment_types(ctx: Context) -> dict:
    body = ctx.metadata.get("body", {})
    ctx.metadata["body"] = {
        "amount": Decimal(str(body.get("amount", "0.00"))),
        "payment_id": UUID(body.get("payment_id", "")),
        "created_at": datetime.fromisoformat(body.get("created_at", "")),
    }
    return {"converted": True}

# 2. Intent with type converter in pipeline
CREATE_PAYMENT = Intent(
    name="POST:/payments",
    level=Level.STANDARD,
    metadata={
        "method": "POST",
        "path": "/payments",
        "processors": ("convert_payment_types",),
    },
)

# 3. Handler — receives already-typed data
async def handle_create_payment(intent: Intent) -> dict:
    body = intent.metadata["body"]  # already typed
    return {
        "status": "processed",
        "payment_id": str(body["payment_id"]),
        "amount": str(body["amount"]),
    }

on(app, CREATE_PAYMENT, handle_create_payment)
```

## Summary

| Type | Use Case | Example |
|------|----------|---------|
| `UUID` | Unique identifiers | `user_id: UUID` |
| `datetime` | Timestamps | `created_at: datetime` |
| `date` | Calendar dates | `birth_date: date` |
| `time` | Time of day | `start_time: time` |
| `timedelta` | Durations | `duration: timedelta` |
| `bytes` | Binary data | `content: bytes` |
| `Decimal` | Precise decimals | `amount: Decimal` |