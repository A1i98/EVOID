---
title: 'Plugin Collection'
description: 'Official EVOID plugins on PyPI — storage, cache, DI, auth, tasks, dashboard.'
---

# Plugin Collection

Official EVOID plugins on PyPI. Each is an independent package — install only what you need.

## Quick Install

```bash
# Via evo CLI (short names)
evo install di
evo install redis
evo install smart-storage

# Via pip
pip install evoid-di
pip install evoid-redis
pip install evoid-smart-storage
```

## Available Plugins

### Storage

| Package | Install | Description |
|---------|---------|-------------|
| `evoid-sqlite` | `pip install evoid-sqlite` | SQLite storage engine |
| `evoid-redis` | `pip install evoid-redis` | Redis cache with TTL |
| `evoid-postgresql` | `pip install evoid-postgresql` | PostgreSQL via SQLAlchemy |
| `evoid-scylla` | `pip install evoid-scylla` | ScyllaDB/Cassandra |

```python
from evoid_sqlite import create_storage

storage = create_storage("my_app.db")
await storage.write("user:1", {"name": "Alice"})
user = await storage.read("user:1")
```

### Smart Storage

Multi-DB routing — data goes to the right backend automatically.

```bash
pip install evoid-smart-storage
```

```toml
# evoid.toml
[engines]
storage = "smart_storage"

[engines.smart_storage.mapping]
credentials = "postgresql"
session = "redis"
logs = "memory"

[engines.smart_storage.level_routing]
critical = "postgresql"
standard = "sqlite"
```

### DI Engine

Three levels of complexity in one package.

```bash
pip install evoid-di
```

```python
from evoid_di import DIEngine

# Level 1: Simple
di = DIEngine()
di.register("db", create_db)
db = di.resolve("db")

# Level 2: Scoped
di.register("db", create_db, scope="singleton")
di.register("session", create_session, scope="per_user")

# Level 3: Context-aware
di = DIEngine(rules_config=rules, implementations=impls)
instance = await di.resolve("notifier", ctx)
```

### Auth

Bring your own provider — no forced JWT.

```bash
pip install evoid-auth
```

```python
from evoid_auth import register_provider

async def my_auth(token: str) -> dict:
    user = await db.find_by_token(token)
    return {"user": user.name, "role": user.role}

register_provider("my_auth", my_auth)

# Wire to pipeline
from evoid.core.extend import before
before("GET:/users", "authenticate")
```

### Tasks & Logging

Background tasks with Godot-inspired lifecycle.

```bash
pip install evoid-tasks
# With loguru (optional)
pip install "evoid-tasks[loguru]"
```

```python
from evoid_tasks import scheduler, TaskContext

# Fire-and-forget
scheduler.run(send_email, to="alice@example.com")

# Scheduled with lifecycle
@scheduler.task(interval=60)
async def monitor(ctx: TaskContext):
    if ctx.tick:
        await check_levels()

# Event-driven
@scheduler.on("order_placed")
async def update_stats(ctx: TaskContext):
    await recalc(ctx.event_data)
```

### Dashboard

Monitoring UI — service map, DB viewer, logs.

```bash
pip install evoid-dashboard
```

```python
from evoid_dashboard import create_dashboard

# Run on port 8001
create_dashboard(port=8001)
```

Open `http://localhost:8001` to see:
- Service map with connections
- All registered Intents
- Message bus history
- Database connections
- System info

## Combining Plugins

Plugins work together. Example: Smart Storage + DI + Auth + Tasks:

```toml
[engines]
storage = "smart_storage"
di = "di"
auth = "jwt"
```

```python
from evoid_di import DIEngine
from evoid_auth import register_provider
from evoid_tasks import scheduler

# DI routes storage by context
di = DIEngine(rules_config=rules, implementations={
    "sqlite": lambda: create_sqlite("app.db"),
    "redis": lambda: create_redis("redis://localhost"),
})

# Auth with custom provider
register_provider("jwt", jwt_auth)

# Background task
@scheduler.task(interval=300)
async def sync_inventory(ctx):
    await sync_all_locations()
```

## Plugin Standard

Every plugin follows the EVOID plugin standard:

1. `pyproject.toml` with `evoid>=0.4.0` dependency
2. `evoid_plugin.json` manifest
3. `register_plugin()` entry point
4. IOP-compliant code (data + functions)

See [Plugin Standard](plugin-standard.md) for details.
