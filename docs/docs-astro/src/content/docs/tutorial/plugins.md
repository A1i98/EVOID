---
title: 'Plugin System'
description: 'Custom engines, adapters, and processors. Extend EVOID with plugins.'
---

# Plugin System

Custom engines, adapters, and processors. Extend EVOID with plugins.

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

## Plugin Types

| Type | Purpose | Example |
|------|---------|---------|
| `adapter` | Transport layer | Telegram, Discord, MQTT |
| `engine` | Infrastructure | Storage, cache, serializer |
| `language` | Runtime support | Rust, Go |
| `processor` | Pipeline step | Custom validation, auth |

## What You Learned

| Concept | What It Is |
|---------|-----------|
| Plugin registry | Register and resolve plugins by name |
| Plugin manifest | `evoid_plugin.json` for PyPI plugins |
| Plugin types | adapter, engine, language, processor |
| Installing | `evo plugin install` |

## Next: AI Analytics

Let's add AI-powered analytics — [AI Analytics](ai-analytics.md).
