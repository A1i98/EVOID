---
title: 'Plugin System'
description: 'Custom engines, adapters, and processors. Extend EVOID with plugins.'
---

# Plugin System

Custom engines, adapters, and processors. Extend EVOID with plugins.

!!! info "The official collection"
    EVOID ships with 14 official plugins on PyPI. See [Plugin Collection](../learn/plugin-collection.md) for the full catalog — storage, cache, DI, auth, tasks, cluster, game integration, transport, scheduler, and dashboard.

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

Every EVOID plugin on PyPI has a manifest:

```json
{
  "name": "evoid-redis",
  "version": "1.0.0",
  "type": "engine",
  "description": "Redis cache engine for EVOID",
  "entry_point": "evoid_redis:register_plugin",
  "dependencies": ["redis>=4.0.0"],
  "evoid_version": ">=0.4.0",
  "tags": ["cache", "redis"]
}
```

## Installing Plugins

```bash
# Search for plugins
evo plugin search cache

# Install a plugin
evo plugin install evoid-redis

# List installed
evo plugin list
```

!!! example "Real-world: Sandy's shop gets a database"
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
from evoid.engines.plugin import register

def register_plugin():
    """Called when the plugin is loaded."""
    register(
        name="my-engine",
        type="engine",
        factory=create_engine,
        version="1.0.0",
        description="My custom engine",
    )

def create_engine():
    """Factory: create the engine instance."""
    return {"type": "my-engine", "config": {}}
```

!!! example "IOP: plugins are processors"
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
    
    # Same codebase, different infrastructure — the level decides.
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
| Plugin manifest | `evoid_plugin.json` for PyPI plugins |
| Plugin types | adapter, engine, language, processor |
| Installing | `evo plugin install` |

## Next: AI Analytics

Let's add AI-powered analytics — [AI Analytics](ai-analytics.md).
