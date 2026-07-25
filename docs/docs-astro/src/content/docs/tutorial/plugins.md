---
title: 'Plugin System'
description: 'Custom engines, adapters, and processors. Extend EVOID with plugins.'
---

# Plugin System

Extend EVOID with engines, adapters, and processors.

!!! info "The official collection"
    EVOID ships with 14 official plugins on PyPI. See [Plugin Collection](../learn/plugin-collection.md) for the full catalog: storage, cache, DI, auth, tasks, cluster, game integration, transport, scheduler, and dashboard.

## Plugin Registry

Every infrastructure component is a plugin:

```python
from evoid.engines.plugin import register, resolve, list_plugins

# Register a custom plugin
register(
    name="redis-cache",
    type="engine",
    factory=redis_cache_factory,
    version="1.0.0",
    description="Redis cache engine",
)

# Resolve it later
factory = resolve("redis-cache", "engine")
cache = factory()

# List all plugins
plugins = list_plugins()
for p in plugins:
    print(f"{p.name} [{p.type}] v{p.version}")
```

## Plugin Manifest

Every EVOID plugin on PyPI has a manifest: a Python dict in `__init__.py`.

```python
# evoid_redis/__init__.py
MANIFEST = {
    "name": "evoid-redis",
    "version": "0.1.2",
    "type": "engine",
    "description": "Redis cache engine for EVOID",
    "category": "cache",
    "dependencies": ["redis>=4.0.0"],
    "evoid_version": ">=0.4.0",
}
```

## Installing Plugins

```bash
# Search for plugins
evo plug search cache

# Install a plugin
evo plug install evoid-redis

# List installed
evo plug list
```

!!! info "Real-world: Sandy's shop gets a database"
    ```bash
    # Sandy's sandwich shop needs to save orders
    evo install sqlite
    
    # Now the pipeline can use storage:
    # validate → authorize → store_order → handler
    # Sandy didn't write database code. The plugin handles it.
    ```

## Writing a Plugin

```python
# my_plugin/__init__.py
from typing import Any
from evoid.engines.plugin import register

class MyStorage:
    def __init__(self, path: str = "data.db"):
        self.path = path

    async def write(self, key: str, data: dict[str, Any], **kwargs) -> bool:
        print(f"Stored {key} in {self.path}")
        return True

    async def read(self, key: str, **kwargs) -> Any | None:
        return None

    async def delete(self, key: str, **kwargs) -> bool:
        return True

    async def health(self) -> bool:
        return True

def create_engine(path: str = "data.db") -> MyStorage:
    """Factory: create a MyStorage instance."""
    return MyStorage(path=path)

def register_plugin():
    """Call when the plugin loads."""
    register(
        name="my-engine",
        type="engine",
        factory=create_engine,
        version="0.1.0",
        description="My custom engine",
    )
```

!!! info "IOP: plugins are processors"
    ```python
    # A plugin doesn't know about your business logic.
    # It implements a contract (StorageEngine, CacheEngine, etc.)
    # and the pipeline calls it when the Intent level demands it.
    
    # Your payment Intent (CRITICAL):
    # → validate (built-in)
    # → authorize (evoid-auth plugin)
    # → audit (evoid-auth plugin)
    # → protect (built-in)
    # → handler (your code)
    
    # Your cache Intent (EPHEMERAL):
    # → validate (built-in)
    # → handler (your code, which calls evoid-redis)
    
    # Same codebase, different infrastructure. The level decides.
    ```

## Plugin Types

| Type | Purpose | Example |
|------|---------|---------|
| `adapter` | Transport layer | ASGI, Telegram, WebSocket, Godot |
| `engine` | Infrastructure | Storage, cache, DI, auth, scheduler |
| `language` | Runtime support | Rust, Go |
| `processor` | Pipeline step | Custom validation, auth, audit |

!!! info "Official plugin types"
    | Plugin | Type | What it does |
    |--------|------|-------------|
    | evoid-sqlite | engine | SQLite storage |
    | evoid-redis | engine | Redis cache with TTL |
    | evoid-postgresql | engine | PostgreSQL storage |
    | evoid-scylla | engine | ScyllaDB/Cassandra storage |
    | evoid-smart-storage | engine | Multi-DB routing |
    | evoid-di | engine | 3-tier dependency injection |
    | evoid-auth | engine | BYO auth providers |
    | evoid-tasks | engine | Background tasks with lifecycle |
    | evoid-scheduler | engine | Priority-aware scheduling |
    | evoid-cluster | engine | Multi-node clustering |
    | evoid-transport | engine | Low-latency UDP transport |
    | evoid-dashboard | adapter | Monitoring web UI |
    | evoid-godot | adapter | Godot game integration |
    | evoid-base | contracts | Shared protocols |

## What You Learned

| Concept | What It Is |
|---------|-----------|
| Plugin registry | Register and resolve plugins by name |
| Plugin manifest | `MANIFEST` dict in `__init__.py` |
| Plugin types | adapter, engine, language, processor |
| Installing | `evo plug install` |

## Next: AI Analytics

Add AI-powered analytics next: [AI Analytics](ai-analytics.md).
