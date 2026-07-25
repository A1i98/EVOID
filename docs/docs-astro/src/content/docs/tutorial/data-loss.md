---
title: 'Data Loss'
description: "Sandy's orders disappear when the program restarts. Why persistence matters."
---

# Data Loss

Sandy's orders disappear when the program restarts. Why persistence matters.

## The Problem

Sandy's sandwich shop runs on a Python script. Orders work perfectly. Then:

```bash
# Sandy takes 15 orders
python orders.py
# → Order 1: BLT x2
# → Order 2: Club x1
# → ... 13 more orders

# Server restarts (power outage, deploy, crash)
python orders.py
# → All 15 orders: gone
```

The orders live in a dict. Dicts live in memory. Memory is volatile. When the process stops, everything vanishes.

## Why This Happens

```python
# This is Sandy's current code
orders = []  # ← lives in memory, dies with the process

async def handle_order(intent):
    orders.append(intent.metadata)  # ← stored in RAM
    return {"status": "confirmed"}
```

The `orders` list is a Python variable. It exists only while the program runs. No disk, no database, no backup. One restart and Sandy loses every order.

## The Real Cost

For a sandwich shop, losing orders means:
- Customers paid but got no sandwich
- Sandy doesn't know what to prepare
- Inventory counts are wrong
- End-of-day sales report is empty

For a real business, this is a disaster.

## The Solution: Storage Plugin

EVOID's storage plugin gives you persistent storage with one line of config:

```bash
evo install sqlite
```

```toml
# evoid.toml
[engines]
storage = "sqlite"
```

Now when Sandy's code writes an order, it goes to a SQLite database on disk. Restart the program? Orders are still there.

```python
from evoid import Intent, Level, execute

SAVE_ORDER = Intent(
    name="save_order",
    level=Level.STANDARD,
    metadata={"sandwich": "BLT", "qty": 2, "total": 17.98},
)

# This now persists to SQLite automatically
result = await execute(SAVE_ORDER)
```

## What Changed

| Before | After |
|--------|-------|
| Orders in `[]` (memory) | Orders in SQLite (disk) |
| Lost on restart | Survives restart |
| One process only | Multiple processes can read |
| No backup | `.db` file can be copied |

## The IOP Pattern

Sandy didn't change her business logic. She changed the **infrastructure**. The Intent stayed the same. The pipeline now includes a storage processor. That's IOP: the Intent declares what, the pipeline decides how.

## Next: Who is Ordering?

Sandy's orders are safe. But there's a new problem: anyone can place orders, cancel orders, or change the menu. Next: [Who is Ordering?](who-is-ordering.md)
