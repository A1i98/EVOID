---
title: 'Who is Ordering?'
description: "Anyone can do anything in Sandy's shop. Why authorization matters."
---

# Who is Ordering?

Anyone can do anything in Sandy's shop. Why authorization matters.

## The Problem

Sandy's online shop is live. Orders work. Database works. Then:

- A customer cancels someone else's order
- A stranger changes the menu prices
- A random visitor deletes all orders
- An employee accidentally fires the payment processor

Everyone has the same access. There's no concept of "who is doing this."

## Why This Happens

```python
@post("/orders")
async def create_order(sandwich: str, qty: int) -> dict:
    # No check: who is this person?
    # No check: are they allowed to order?
    return {"status": "confirmed"}

@delete("/orders/{order_id}")
async def cancel_order(order_id: int) -> dict:
    # No check: is this THEIR order?
    # No check: are they an admin?
    return {"status": "cancelled"}
```

Every endpoint trusts every request. No identity, no roles, no permissions.

## The Real Cost

For Sandy's shop:
- Customers can modify other customers' orders
- Anyone can change prices
- No audit trail of who did what

For a real business:
- Legal liability (GDPR, PCI-DSS)
- Financial fraud
- Data breaches
- Loss of customer trust

## The Solution: Auth Plugin

EVOID's auth plugin adds authorization to the pipeline:

```bash
evo install auth
```

```python
from evoid_auth import register_provider

async def my_auth(token: str) -> dict:
    user = await db.find_by_token(token)
    return {"user": user.name, "role": user.role}

register_provider("my_auth", my_auth)
```

Now Sandy's Intents run through an authorization pipeline:

```python
# EPHEMERAL: no auth needed (view menu)
VIEW_MENU = Intent(name="view_menu", level=Level.EPHEMERAL)

# STANDARD: auth required (place order)
CREATE_ORDER = Intent(name="create_order", level=Level.STANDARD)

# CRITICAL: full audit (cancel order, change prices)
CANCEL_ORDER = Intent(name="cancel_order", level=Level.CRITICAL)
```

The pipeline automatically checks roles:
- `viewer` can browse the menu
- `customer` can place orders
- `admin` can manage the menu and cancel orders

## What Changed

| Before | After |
|--------|-------|
| Anyone can do anything | Roles control access |
| No identity | Token-based identity |
| No audit trail | Every action logged |
| No distinction between customer and admin | Clear role hierarchy |

## The IOP Pattern

Sandy didn't add `if user.role == "admin"` to every endpoint. She changed the **Intent level**. EPHEMERAL = no auth. STANDARD = auth. CRITICAL = auth + audit. The pipeline enforces security. Sandy's business logic stays clean.

## Next: Growing Pains

Sandy has persistent storage and proper authorization. But the shop is growing, and new problems are emerging. Next: [Growing Pains](growing-pains.md)
