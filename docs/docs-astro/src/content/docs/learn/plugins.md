---
title: 'Plugins and Engines'
description: 'EVOID is infrastructure-agnostic. Every infrastructure component — database, cache, serializer, schema engine, DI — is a plugin. Plugins communicate through ...'
---

# Plugins and Engines

EVOID is infrastructure-agnostic. Every infrastructure component — database, cache, serializer, schema engine, DI — is a plugin. Plugins communicate through contracts, never concrete implementations.

!!! warning "Contracts, not implementations"
    Always code against the contract interface (e.g., `StorageEngine`), never the concrete class. This lets you swap implementations without changing business logic.

## Built-in Engines

EVOID ships with built-in engines. No plugins required.

### Schema Engine

Validates and serializes data.

```python
# Default: native (stdlib dataclasses + TypedDict)
# Located at: evoid/engines/schema/native.py
```

### Storage Engine

Persists data.

| Engine | Location | Use Case |
|--------|----------|----------|
| `memory` | `engines/storage/memory.py` | Testing, ephemeral data |
| `sqlite` | `engines/storage/sqlite.py` | Local persistence |

### Cache Engine

In-memory LRU cache with optional TTL.

```python
from evoid.engines.cache import memory as cache

await cache.configure(max_size=1000)
await cache.set("user:123", user_data, ttl=300)
value = await cache.get("user:123")
```

### Serializer Engine

JSON serialization with datetime support.

```python
from evoid.engines.serializer import json_engine

encoded = json_engine.encode(data)
decoded = json_engine.decode(encoded)
```

### DI Engine

Dependency injection — resolves dependencies by name.

```python
from evoid.engines.di import native as di

di.register("db", database_factory)
db = di.resolve("db")
```

### Logger Engine

Structured logging.

| Engine | Style |
|--------|-------|
| `structlog` | Structured, machine-readable |
| `loguru` | Beautiful, colored output |

### Metrics Engine

Simple metrics collection.

### Auth Engine

Authentication and authorization.

### Plugin Engine

Meta-plugin for registering other plugins.

## Contracts

Contracts define the interface that engines must satisfy. They live in `evoid/contracts/`:

| Contract | Purpose |
|----------|---------|
| `SchemaEngine` | `validate()`, `serialize()`, `deserialize()` |
| `StorageEngine` | `read()`, `write()`, `delete()`, `health()` |
| `CacheEngine` | `get()`, `set()`, `delete()`, `clear()`, `health()` |
| `SerializerEngine` | `encode()`, `decode()` |
| `AdapterEngine` | `start()`, `stop()`, `handle()` |

Engines implement these contracts as plain functions, not classes.

## Configuration

Engines are configured in `evoid.toml`:

```toml
[engines]
schema = "native"
storage = "memory"
cache = "memory"
serializer = "json"
di = "native"
logger = "loguru"
metrics = "simple"
auth = "simple"
```

Change infrastructure by changing config. Business logic stays untouched.

## Writing Custom Engines

Implement the contract as functions:

```python
# my_storage.py

async def read(key: str) -> Any:
    """Read data by key."""
    ...

async def write(key: str, value: Any) -> bool:
    """Write data by key."""
    ...

async def delete(key: str) -> bool:
    """Delete data by key."""
    ...

async def health() -> bool:
    """Check engine health."""
    return True
```

Register it:

```python
from evoid.engines.plugin import register

register(
    name="postgres",
    type="storage",
    factory=lambda: postgres_storage,
    version="1.0.0",
    description="PostgreSQL storage engine",
)
```

!!! tip "Build your own plugin"
    Need Redis caching, PostgreSQL storage, or advanced DI? You can either install an existing plugin or write your own. See [Plugin Ecosystem](plugin-ecosystem.md) for a quick-start guide.

## Plugin Registry

The plugin system is a dict-based registry. Register a plugin, resolve it by name.

```python
from evoid.engines.plugin import register, resolve

# Register a plugin
register(
    name="sqlite",
    type="storage",
    factory=sqlite_storage_factory,
    version="1.0.0",
    description="SQLite storage engine",
)

# Resolve it later
factory = resolve("sqlite", "storage")
engine = factory()
```

## Dependency Map

EVOID maps engine names to Python packages for `evo sync`:

```python
ENGINE_PACKAGES = {
    "sqlite": "aiosqlite",
    "redis": "redis.asyncio",
    "structlog": "structlog",
    "loguru": "loguru",
    # ...
}
```

`evo sync` reads `evoid.toml`, resolves package names, and installs them via `uv`.

## Official Plugin Collection

Need more than built-in engines? The official plugin repository at [EvolveBeyond/evoid-plugins](https://github.com/EvolveBeyond/evoid-plugins) has you covered.

### Install

```bash
# Short names via evo CLI
evo install di            # → evoid-di
evo install redis         # → evoid-redis
evo install smart-storage # → evoid-smart-storage

# Or directly with pip/uv
pip install evoid-di
pip install evoid-redis
pip install evoid-smart-storage
```

### Available Plugins

| Plugin | Package | Description |
|--------|---------|-------------|
| Base | `evoid-base` | Shared protocols (StorageEngine, CacheEngine, LoggerEngine) |
| SQLite | `evoid-sqlite` | SQLite storage engine |
| Redis | `evoid-redis` | Redis cache with TTL |
| PostgreSQL | `evoid-postgresql` | PostgreSQL via SQLAlchemy + asyncpg |
| ScyllaDB | `evoid-scylla` | ScyllaDB/Cassandra storage |
| Smart Storage | `evoid-smart-storage` | Multi-DB routing, schema enforcement, multi-tenancy |
| DI | `evoid-di` | Dependency injection — simple, scoped, or context-aware |
| Auth | `evoid-auth` | Bring your own auth provider |
| Tasks | `evoid-tasks` | Background tasks + structured logging |
| Dashboard | `evoid-dashboard` | Monitoring UI — service map, DB viewer, logs |

### Smart Storage Example

Routes data to different backends based on type, level, or user:

```toml
[engines]
storage = "smart_storage"

[engines.smart_storage.mapping]
credentials = "postgresql"   # Sensitive data → PostgreSQL
session = "redis"            # Sessions → Redis
logs = "memory"              # Logs → Memory

[engines.smart_storage.level_routing]
critical = "postgresql"      # Critical intents → PostgreSQL
standard = "sqlite"          # Standard → SQLite
```

### DI Engine Example

Three levels of complexity in one package:

```python
from evoid_di import DIEngine

# Level 1: Simple
di = DIEngine()
di.register("db", create_db)
db = di.resolve("db")

# Level 2: Scoped
di.register("db", create_db, scope="singleton")
di.register("session", create_session, scope="per_user")

# Level 3: Context-aware routing
di = DIEngine(rules_config=rules, implementations=impls)
instance = await di.resolve("notifier", ctx)  # Routes by level/role
```

### Auth Example

Bring your own provider — no forced JWT:

```python
from evoid_auth import register_provider

# Your auth logic
async def my_auth(token: str) -> dict:
    user = await db.find_by_token(token)
    return {"user": user.name, "role": user.role}

register_provider("my_auth", my_auth)

# Wire to pipeline
from evoid.core.extend import before
before("GET:/users", "authenticate")
```

## Related

- [Plugin Ecosystem](plugin-ecosystem.md) — Build your own plugins
- [Plugin Collection](plugin-collection.md) — Full plugin reference
- [Plugin Standard](plugin-standard.md) — Plugin packaging spec
