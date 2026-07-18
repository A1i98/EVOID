---
title: 'Shipping Online'
description: 'Deploy Sandy online shop. What we built, what comes next.'
---

# Shipping Online

Deploy Sandy's online shop. What we built, what comes next.

## What We Built

Sandy's online shop has:

- **Menu API** — CRUD for menu items
- **Order API** — Complex orders with nested models
- **Validation** — Pydantic + custom processors
- **Error Handling** — Structured errors with Result
- **DI** — Database, cache, auth via pipeline
- **Middleware** — Rate limiting, logging, timing
- **Testing** — Direct pipeline testing

## Running in Production

```bash
# Install EVOID
pip install evoid

# Run with production settings
evo service run sandy-api --host 0.0.0.0 --port 8000
```

## What's Next

Sandy's shop is successful. But:

- 3 more locations are opening
- Each location needs its own inventory
- Orders need to sync between locations
- Sandy wants AI-powered analytics

This is Phase 3 — the franchise.

## Phase 3 Preview

```python
# Native IOP style — full control
from evoid.native import create_service, on

orders_service = create_service("orders")
inventory_service = create_service("inventory")

# Inter-service communication via Message Bus
from evoid.core.message_bus import publish, subscribe

# Orders service publishes to inventory
await publish(
    Intent(name="order_placed", level=Level.STANDARD),
    source="orders",
)

# Inventory service subscribes
subscribe("order_placed", handle_stock_update)
```

## Next: Multi-Location

Let's scale Sandy to a franchise — [Multi-Location](multi-location.md).
