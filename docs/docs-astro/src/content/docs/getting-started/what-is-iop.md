---
title: 'What is IOP?'
description: 'Intent-Oriented Programming — a paradigm where data declares what it needs, and the runtime handles how.'
---

# What is IOP?

**Intent-Oriented Programming (IOP)** is a paradigm where data declares what it needs, and the runtime handles how.

It's not anti-OOP. It's not anti-FP. It's a third way that combines the best of both: data carries intent (like objects carry state), and processors are pure functions (like FP transforms).

## The Problem

Every time you write an endpoint, you make the same infrastructure decisions:

```python
def save_user(user):
    # 1. Which database? MySQL? PostgreSQL? MongoDB?
    db.insert("users", user)

    # 2. How to cache? Redis? In-memory?
    cache.set(f"user:{user.id}", user, ttl=300)

    # 3. Should I encrypt? Audit? Log?
    encrypt(user.email)
    audit_log("user_created", user)

    # 4. What if it fails? Rollback cache? Retry?
    try:
        db.commit()
    except Exception as e:
        cache.delete(f"user:{user.id}")
        raise
```

These decisions repeat across every function in every project. The infrastructure logic mixes with business logic. Changing the database means rewriting every function.

## The IOP Solution

What if your data could tell the system what it needs?

```python
from evoid import Intent, Level

# Declare WHAT you want — the runtime decides HOW
GET_USER = Intent(
    name="get_user",
    level=Level.STANDARD,  # Normal business data
    metadata={"method": "GET", "path": "/users/{id}"},
)

# Your handler focuses on business logic only
async def handle_get_user(intent: Intent) -> dict:
    user_id = intent.metadata.get("id")
    # No database choice here — the pipeline handles it
    # No caching logic here — the pipeline handles it
    # No encryption here — the pipeline handles it
    return {"id": user_id, "name": "Alice"}
```

**That's IOP.** You declare what you want (the Intent), and the runtime handles how (the pipeline).

## How It Works

```
Your Intent (what you want)
      ↓
Intent Resolver (reads Intent level + metadata)
      ↓
Pipeline Composer (builds execution plan)
      ↓
Processor 1: validate    → checks input
Processor 2: authorize   → checks permissions
Processor 3: your handler → business logic
Processor 4: audit       → logs the action
      ↓
Result (success/failure with timing)
```

Each processor is a **pure function** that receives a `Context` and returns a result. The pipeline composes them. You don't call them directly — the runtime does.

## Three Intent Levels

Each level maps to a different pipeline with different infrastructure behaviors:

| Level | What It Means | Pipeline | Timeout | Use Case |
|-------|---------------|----------|---------|----------|
| **EPHEMERAL** | "I don't care if this disappears" | `validate` | 5s | Sessions, cache, temp data |
| **STANDARD** | "Normal business data" | `validate`, `authorize` | 10s | User profiles, posts, comments |
| **CRITICAL** | "This must never be lost" | `validate`, `authorize`, `audit`, `protect` | 30s | Payments, medical, legal |

You choose the level. The runtime chooses the infrastructure.

## Traditional vs IOP

=== "Traditional"

    ```python
    # Every function repeats infrastructure decisions
    async def get_user(user_id: int):
        user = await db.get_user(user_id)      # Which db?
        cached = cache.get(f"user:{user_id}")   # Which cache?
        if cached:
            return cached
        encrypted = encrypt(user.email)          # Which encryption?
        audit_log("user_accessed", user)         # Which logger?
        cache.set(f"user:{user_id}", user)       # Which cache?
        return user
    ```

=== "IOP"

    ```python
    # Declare intent — runtime handles infrastructure
    GET_USER = Intent(
        name="get_user",
        level=Level.STANDARD,
    )

    async def handle_get_user(intent: Intent) -> dict:
        user_id = intent.metadata.get("id")
        # Just business logic — no infrastructure decisions
        return {"id": user_id, "name": "Alice"}

    # Pipeline: validate → authorize → handle_get_user
    # Infrastructure: chosen by level, configurable via plugins
    ```

The IOP version doesn't eliminate infrastructure — it moves it to the pipeline where it's configured once and applied everywhere.

## Key Principles

1. **Intent is Permanent** — Once declared, the Intent stays with the data through its entire lifecycle
2. **Infrastructure is Temporary** — Swap databases, caches, queues by changing pipeline config, not business logic
3. **Data Carries Intent** — Your data models tell the system how to handle them
4. **Pipeline is Composition** — Processors are pure functions composed together
5. **Processors are Independent** — Each does one thing, knows nothing about others

## Why This Matters for AI

IOP was designed for a world where AI agents need to understand and interact with your system:

- **Schema Export** — Intents export as JSON Schema, making them machine-readable
- **MCP Integration** — Expose Intents as MCP tools for AI agents
- **Self-Describing** — An AI agent can read an Intent and understand what it does, what level it needs, and what pipeline it runs

```python
# AI agents can discover and call your intents
GET_USER = Intent(
    name="get_user",
    level=Level.STANDARD,
    metadata={"method": "GET", "path": "/users/{id}"},
    # AI agent sees: "This intent gets a user by ID"
    # AI agent knows: "This is standard level, needs authorization"
)
```

## Learn More

- [IOP Levels](../learn/iop-levels.md) — Three levels from dict to dataclass
- [Intent](../learn/intent.md) — Deep dive into Intents
- [Pipeline](../learn/pipeline.md) — How execution works
- [Processors](../learn/processors.md) — Functions that handle intents
- [Syntax Styles](../styles/route.md) — Different ways to write IOP code
