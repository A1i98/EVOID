---
title: 'IOP Levels'
description: 'Three levels of IOP — from simple dicts to production systems. Start simple, upgrade when it hurts.'
---

# IOP Levels

IOP has two orthogonal concepts that people confuse:

1. **Code levels** (how you write Intents) — Dict, TypedDict, Dataclass
2. **Intent levels** (what the pipeline does) — Ephemeral, Standard, Critical

This page covers both. The code levels determine how much structure you get. The Intent levels determine how much infrastructure runs.

!!! tip "Golden Rule"
    > Start from Level 1. Upgrade only when it hurts. Never start at Level 3.

---

## Intent Levels: What the Pipeline Does

Before diving into code levels, understand the three Intent levels. These are the heart of IOP — they determine which processors run, how long you have, and what infrastructure backs you.

### Ephemeral — "I don't care if this disappears"

**Pipeline:** `validate` (that's it)
**Timeout:** 5 seconds
**Mindset:** Fast, disposable, no overhead

```python
# Cache lookup — result can vanish, nobody cares
GET_CACHE = Intent(name="cache_check", level=Level.EPHEMERAL)

# Session check — temporary by definition
CHECK_SESSION = Intent(name="check_session", level=Level.EPHEMERAL)

# Health check — pure liveness probe
HEALTH = Intent(name="health_check", level=Level.EPHEMERAL)

# Game state — position updates, frame-by-frame
PLAYER_MOVE = Intent(name="player_move", level=Level.EPHEMERAL)
```

**Real-world analogy:** Checking the weather. You look, you know, you move on. No paperwork, no authorization, no audit trail. If the data is wrong, you'll check again in 5 minutes.

**What runs:** Only `validate` — makes sure the data shape is correct. No auth, no audit, no protection. The runtime trusts this Intent is cheap.

**When to use:** Anything where losing the result is inconvenience, not damage. Cache hits, session lookups, temporary state, health checks, telemetry pings, game position updates.

### Standard — "Normal business data"

**Pipeline:** `validate` → `authorize`
**Timeout:** 10 seconds
**Mindset:** Balanced — check inputs, check permissions, done

```python
# User profile — someone's identity, worth protecting
GET_PROFILE = Intent(name="get_profile", level=Level.STANDARD)

# Blog post — public content, but author matters
CREATE_POST = Intent(name="create_post", level=Level.STANDARD)

# Order status — business data, needs auth
CHECK_ORDER = Intent(name="check_order", level=Level.STANDARD)

# Chat message — needs to know who's talking
SEND_MESSAGE = Intent(name="send_message", level=Level.STANDARD)
```

**Real-world analogy:** Showing your ID at a reception desk. They verify who you are (authorize), then let you in. No cameras, no guards, no paperwork — just a quick identity check.

**What runs:** `validate` (data shape) + `authorize` (permissions). The auth plugin checks if your role is sufficient. If you're a `viewer` trying to edit, you get rejected.

**When to use:** Most business operations. User profiles, posts, comments, settings, general CRUD. The bread and butter of any application.

### Critical — "This must never be lost"

**Pipeline:** `validate` → `authorize` → `audit` → `protect`
**Timeout:** 30 seconds
**Mindset:** Full protection — every step logged, every action audited

```python
# Payment — real money, real consequences
PROCESS_PAYMENT = Intent(name="process_payment", level=Level.CRITICAL)

# Medical record — legal requirements
SAVE_MEDICAL = Intent(name="save_medical_record", level=Level.CRITICAL)

# Legal document — must be immutable and auditable
SIGN_CONTRACT = Intent(name="sign_contract", level=Level.CRITICAL)

# Admin action — elevated privileges, full audit
DELETE_USER = Intent(name="delete_user", level=Level.CRITICAL)
```

**Real-world analogy:** Wire transferring a million dollars. You sign papers (authorize), a camera watches you (audit), a guard stands by (protect), and there's a paper trail that lasts forever.

**What runs:** The full pipeline. `validate` → `authorize` → `audit` (logs everything) → `protect` (rate limits, circuit breaker). Every step is recorded. Every action is traceable.

**When to use:** Anything where losing data or making an unauthorized change has real consequences. Payments, medical records, legal documents, authentication, admin operations, data deletion.

---

### How Levels Affect Plugins

The level you choose determines which plugins activate:

| Level | Auth | Audit | Rate Limit | Circuit Breaker | Storage |
|-------|------|-------|------------|-----------------|---------|
| Ephemeral | - | - | 100/min | - | Memory/Redis |
| Standard | Yes | - | 50/min | - | SQLite/Redis |
| Critical | Yes | Yes | 20/min | Yes | PostgreSQL |

```python
# Ephemeral: fast path, minimal infrastructure
CACHE_HIT = Intent(name="cache_hit", level=Level.EPHEMERAL)
# → validate → handler (5s timeout, memory cache)

# Standard: balanced, auth required
GET_USER = Intent(name="get_user", level=Level.STANDARD)
# → validate → authorize → handler (10s timeout, disk cache)

# Critical: full protection, everything logged
PROCESS_PAYMENT = Intent(name="process_payment", level=Level.CRITICAL)
# → validate → authorize → audit → protect → handler (30s timeout, PostgreSQL)
```

---

## Code Levels: How You Write Intents

Now that you understand Intent levels (what the pipeline does), let's look at code levels (how you structure your code).

### Level 1: Dict + Functions

**When:** Scripts, small tools, <10 commands, single file.

The simplest form of IOP. Data is a dict. Processors are functions. The pipeline is a list.

```python
from evoid import Intent, Level, execute
from evoid.core import Context

# Level 1: Data is just a dict
state = {"order_id": "ORD-001", "items": ["pizza", "salad"], "total": 25.99}

# Level 1: Processors are plain functions
async def validate_order(ctx: Context) -> dict:
    items = ctx.state.get("items", [])
    if not items:
        raise ValueError("Empty order")
    return {"valid": True}

async def calculate_total(ctx: Context) -> dict:
    items = ctx.state.get("items", [])
    total = len(items) * 12.99  # simplified
    ctx.state["total"] = total
    return {"total": total}

# Level 1: Register and execute
from evoid import register_processor
register_processor("validate_order", validate_order)
register_processor("calculate_total", calculate_total)

intent = Intent(
    name="place_order",
    level=Level.STANDARD,
    pipeline=("validate_order", "calculate_total"),
)

result = await execute(intent)
# result.value = {"total": 25.98}
```

!!! example "IOP in a script"
    ```python
    # Quick data pipeline — no classes, no imports, no ceremony
    from evoid import Intent, Level, execute
    
    async def clean_data(ctx):
        raw = ctx.state["raw"]
        ctx.state["cleaned"] = [r.strip() for r in raw if r]
        return {"rows": len(ctx.state["cleaned"])}
    
    async def save_to_file(ctx):
        data = ctx.state["cleaned"]
        with open("output.csv", "w") as f:
            f.writerows(data)
        return {"saved": True}
    
    from evoid import register_processor
    register_processor("clean", clean_data)
    register_processor("save", save_to_file)
    
    result = await execute(Intent(
        name="etl_pipeline",
        level=Level.EPHEMERAL,  # Disposable data
        pipeline=("clean", "save"),
    ))
    ```

**What you get:** Dicts for data, functions for logic, pipeline for composition.
**What you don't get:** Type safety, IDE autocomplete, validation.

### Level 2: TypedDict + Compose

**When:** Medium CLIs, 10-30 commands, solo developer, need type hints.

Add type hints to your dicts. The structure becomes visible to your IDE.

```python
from typing import TypedDict, NotRequired
from evoid import Intent, Level, execute
from evoid.core import Context

# Level 2: TypedDict — your IDE knows the shape
class OrderState(TypedDict, total=False):
    order_id: str
    items: list[str]
    total: float
    validated: bool
    error: str | None

# Level 2: Processors are typed
async def validate_order(ctx: Context) -> dict:
    items = ctx.state.get("items", [])
    if not items:
        ctx.state["error"] = "Empty order"
        raise ValueError("Empty order")
    ctx.state["validated"] = True
    return {"valid": True}

async def calculate_total(ctx: Context) -> dict:
    items = ctx.state.get("items", [])
    total = len(items) * 12.99
    ctx.state["total"] = total
    return {"total": total}

async def apply_discount(ctx: Context) -> dict:
    total = ctx.state.get("total", 0)
    if total > 50:
        ctx.state["total"] = total * 0.9  # 10% off
    return {"discounted": True}

# Level 2: Pipeline is explicit
intent = Intent(
    name="place_order",
    level=Level.STANDARD,
    pipeline=("validate_order", "calculate_total", "apply_discount"),
)

from evoid import register_processor
register_processor("validate_order", validate_order)
register_processor("calculate_total", calculate_total)
register_processor("apply_discount", apply_discount)

result = await execute(intent)
```

!!! example "TypedDict in a CLI"
    ```python
    # Your IDE autocompletes ctx.state["items"]
    # Type checker catches ctx.state["iteams"] (typo)
    # No frozen dataclass overhead, but you see the shape
    
    class InventoryState(TypedDict, total=False):
        product_id: str
        quantity: int
        warehouse: str
        reserved: bool
    
    async def check_stock(ctx: Context) -> dict:
        # IDE knows: ctx.state["quantity"] is int
        qty = ctx.state.get("quantity", 0)
        if qty <= 0:
            raise ValueError("Out of stock")
        return {"in_stock": True}
    ```

**What you get:** Type hints, IDE autocomplete, structured data without classes.
**What you don't get:** Immutability, schema validation, complex state machines.

### Level 3: Dataclass + Decorator

**When:** Production systems, teams 5+, complex state machines, need validation.

Frozen dataclasses for immutable data. Decorators for registration. Full IOP.

```python
from dataclasses import dataclass, field
from evoid import Intent, Level, execute, register_processor
from evoid.core import Context

# Level 3: Frozen dataclass — immutable, validated, thread-safe
@dataclass(frozen=True)
class OrderState:
    order_id: str = ""
    items: tuple[str, ...] = ()  # tuple, not list — immutable
    total: float = 0.0
    validated: bool = False
    error: str | None = None

# Level 3: Processors are typed, registered, composable
async def validate_order(ctx: Context) -> dict:
    items = ctx.state.get("items", ())
    if not items:
        raise ValueError("Empty order")
    return {"valid": True}

async def calculate_total(ctx: Context) -> dict:
    items = ctx.state.get("items", ())
    total = len(items) * 12.99
    return {"total": total}

# Level 3: Intent with full control
PLACE_ORDER = Intent(
    name="place_order",
    level=Level.STANDARD,
    pipeline=("validate_order", "calculate_total"),
    timeout=10.0,
    priority=0,
)

# Level 3: Register and execute with full Result
register_processor("validate_order", validate_order)
register_processor("calculate_total", calculate_total)

result = await execute(PLACE_ORDER, context=Context(intent=PLACE_ORDER))

if result.success:
    print(f"Done in {result.duration:.3f}s")
    print(f"Processors: {result.processors}")
else:
    print(f"Failed: {result.error}")
```

!!! example "Full IOP: payment processing"
    ```python
    # Level 3 with Critical Intent — the full IOP experience
    from dataclasses import dataclass
    
    @dataclass(frozen=True)
    class PaymentResult:
        transaction_id: str
        status: str
        amount: float
        currency: str
    
    PROCESS_PAYMENT = Intent(
        name="process_payment",
        level=Level.CRITICAL,  # Full pipeline: validate → authorize → audit → protect
        pipeline=("validate_payment", "charge_card", "send_receipt"),
        timeout=30.0,
        priority=100,  # High priority — payments first
        metadata={"currency": "USD"},
    )
    
    # Pipeline runs:
    # 1. validate (built-in) — checks data shape
    # 2. authorize (built-in) — checks your role
    # 3. audit (built-in) — logs everything
    # 4. protect (built-in) — rate limit, circuit breaker
    # 5. validate_payment (yours) — business validation
    # 6. charge_card (yours) — payment logic
    # 7. send_receipt (yours) — notification
    ```

**What you get:** Frozen dataclasses, full Result, pipeline control, plugin system.
**What you don't get:** Simplicity — more code, more concepts.

---

## Comparison

### Code Levels

| Feature | Level 1 | Level 2 | Level 3 |
|---------|---------|---------|---------|
| Data | `dict` | `TypedDict` | `dataclass(frozen=True)` |
| Type hints | No | Yes | Yes + validation |
| Immutability | No | No | Yes |
| Registration | Manual | Manual | Decorator or manual |
| Pipeline | List of names | List of names | List of names + config |
| Best for | Scripts | Medium CLIs | Production systems |

### Intent Levels

| Level | Pipeline | Timeout | Plugins Active | Use Case |
|-------|----------|---------|----------------|----------|
| Ephemeral | `validate` | 5s | Cache, transport | Sessions, cache, game state |
| Standard | `validate` → `authorize` | 10s | Auth, storage | Profiles, posts, orders |
| Critical | `validate` → `authorize` → `audit` → `protect` | 30s | Auth, audit, storage, rate limit | Payments, medical, legal |

---

## How They Combine

The magic: code levels and Intent levels are independent. You can use Level 1 code with Critical Intent, or Level 3 code with Ephemeral Intent.

```python
# Level 1 code + Critical Intent (works, but you lose type safety)
intent = Intent(name="payment", level=Level.CRITICAL)

# Level 3 code + Ephemeral Intent (overkill, but works)
@dataclass(frozen=True)
class CacheKey:
    key: str

CACHE_GET = Intent(name="cache_get", level=Level.EPHEMERAL)
```

**Recommendation:** Match the code level to your team size and project maturity. Match the Intent level to your data's criticality.

---

## When to Upgrade

| Signal | Action |
|--------|--------|
| "I keep passing the wrong keys" | Upgrade code to Level 2 (TypedDict) |
| "Two devs keep breaking state" | Upgrade code to Level 3 (frozen dataclass) |
| "I need to audit who changed what" | Upgrade Intent to Level CRITICAL |
| "Auth is too slow for this endpoint" | Downgrade Intent to Level EPHEMERAL |
| "I'm over-engineering this" | Stay at Level 1 code, use the simplest Intent level that fits |
