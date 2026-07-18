---
title: 'Multi-Location'
description: 'Sandy opens 3 more locations. Native IOP style for complex systems.'
---

# Multi-Location

Sandy opens 3 more locations. Native IOP style for complex systems.

## The Challenge

Sandy now has 4 locations. Each needs:
- Its own menu (local specials differ)
- Shared inventory tracking
- Cross-location order routing
- Centralized analytics

## Native IOP Style

For complex systems, use the native syntax — full control over Intents:

```python
from evoid.native import create_service, on, run
from evoid import Intent, Level

# Create separate services
orders = create_service("orders")
inventory = create_service("inventory")
analytics = create_service("analytics")

# Define Intents explicitly
CREATE_ORDER = Intent(
    name="create_order",
    level=Level.STANDARD,
    metadata={"description": "Create a new order at any location"},
)

GET_INVENTORY = Intent(
    name="get_inventory",
    level=Level.STANDARD,
    metadata={"description": "Check inventory across all locations"},
)

# Register handlers
async def handle_create_order(intent: Intent) -> dict:
    body = intent.metadata.get("body", {})
    location = body.get("location", "main")
    sandwich = body.get("sandwich")
    return {"status": "created", "location": location, "sandwich": sandwich}

async def handle_get_inventory(intent: Intent) -> dict:
    location = intent.metadata.get("location", "all")
    return {"location": location, "items": [], "total": 0}

on(orders, CREATE_ORDER, handle_create_order)
on(inventory, GET_INVENTORY, handle_get_inventory)

# Run services
await run(orders, host="0.0.0.0", port=8001)
await run(inventory, host="0.0.0.0", port=8002)
```

## Service Model

Each service is a data container — name + intents + handlers:

```python
from evoid.native import create_service, on

# Create service
app = create_service("sandy-franchise")

# Define all intents for this service
INTENTS = [
    Intent(name="create_order", level=Level.STANDARD),
    Intent(name="get_menu", level=Level.EPHEMERAL),
    Intent(name="update_inventory", level=Level.CRITICAL),
]

# Register handlers
on(app, INTENTS[0], handle_create_order)
on(app, INTENTS[1], handle_get_menu)
on(app, INTENTS[2], handle_update_inventory)
```

## @controller for Grouping

For web APIs, @controller groups related routes:

```python
from evoid.web.controller import Controller

# Group location endpoints
locations = Controller("/locations")

@locations.get("/")
async def list_locations(intent):
    return {"locations": ["downtown", "mall", "airport", "university"]}

@locations.get("/{location_id}")
async def get_location(intent):
    location_id = intent.metadata.get("location_id")
    return {"id": location_id, "name": f"Location {location_id}"}

# Group order endpoints
orders = Controller("/orders")

@orders.get("/")
async def list_orders(intent):
    return {"orders": []}

@orders.post("/")
async def create_order(intent):
    return {"status": "created"}
```

## What You Learned

| Concept | What It Is |
|---------|-----------|
| Native IOP | Explicit Intent creation, full control |
| Service model | Group Intents into named services |
| @controller | Group routes by domain |
| Multiple services | Separate concerns into independent services |

## Next: Inter-Service

Let's connect the services — [Inter-Service](inter-service.md).
