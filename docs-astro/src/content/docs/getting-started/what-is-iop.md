---
title: 'What is IOP?'
description: 'Intent-Oriented Programming (IOP) is a paradigm where your data model IS your infrastructure policy.'
---

# What is IOP?

**Intent-Oriented Programming (IOP)** is a paradigm where your data model IS your infrastructure policy.

## The Problem

Every time you write a new endpoint, you decide:

- Which database?
- How to cache?
- Should I encrypt this?
- What priority?

These decisions repeat across every function. The same patterns appear in every project. The infrastructure logic mixes with business logic.

## The IOP Solution

What if your data could tell the system what it needs?

```python
# Your data model IS your infrastructure policy
class User(BaseModel):
    name: standard(str)      # Normal processing
    email: critical(str)     # Auto-encrypt, audit, replicate
    session: ephemeral(str)  # Memory only, auto-expire
```

**That's IOP. Your data tells the system what to do. You focus on what matters.**

## Three Intent Levels

| Level | What It Means | Use Case |
|-------|---------------|----------|
| **EPHEMERAL** | "I don't care if this disappears" | Sessions, temporary data, cache |
| **STANDARD** | "Normal business data" | User profiles, posts, comments |
| **CRITICAL** | "This must never be lost" | Payments, medical records, legal docs |

Each level maps to a different pipeline, timeout, and set of infrastructure behaviors.

## Traditional vs IOP

=== "Traditional"

    ```python
    def save_user(user):
        # 1. Manual encryption
        encrypted = encrypt(user.email)

        # 2. Manual caching
        cache.set(f"user:{user.id}", encrypted, ttl=300)

        # 3. Manual database storage
        db.insert("users", encrypted)

        # 4. Manual audit logging
        audit_log("user_created", user)

        # 5. Manual error handling
        try:
            db.commit()
        except Exception as e:
            cache.delete(f"user:{user.id}")
            raise
    ```

=== "IOP"

    ```python
    class User(BaseModel):
        name: standard(str)
        email: critical(str)     # Auto-encrypt, audit, replicate
        session: ephemeral(str)  # Memory only, auto-expire

    # That's it. The runtime handles everything.
    ```

## How It Works

```
Your Data Model (with Intent declarations)
        |
Intent Resolver (reads Intent metadata)
        |
Pipeline Composer (builds execution pipeline)
        |
Processor Scheduler (runs processors in order)
        |
Result (with all infrastructure handled)
```

## Key Principles

1. **Intent is Permanent** — Once declared, Intent stays with the data
2. **Infrastructure is Temporary** — Swap databases, caches, queues without changing business logic
3. **Data Carries Intent** — Your models tell the system how to handle them
4. **Pipeline is Composition** — Processors are pure functions composed together

## Learn More

- [Intent](../learn/intent.md) — Deep dive into Intents
- [Pipeline](../learn/pipeline.md) — How execution works
- [Syntax Styles](../styles/route.md) — Different ways to write IOP code
