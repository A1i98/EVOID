---
title: 'Plugin Standard'
description: 'How to publish EVOID plugins to PyPI and make them discoverable.'
---

# Plugin Standard

Standard for publishing EVOID plugins to PyPI.

## Naming Convention

Plugins must follow this naming:

| Pattern | Example | Use Case |
|---------|---------|----------|
| `evoid-*` | `evoid-redis` | Official plugins |
| `evoid-plugin-*` | `evoid-plugin-discord` | Community plugins |

## Manifest

Every plugin must have an `evoid_plugin.json`:

```json
{
    "name": "evoid-redis",
    "version": "1.0.0",
    "type": "engine",
    "description": "Redis cache engine for EVOID",
    "author": "Your Name",
    "entry_point": "evoid_redis:register_plugin",
    "dependencies": ["redis>=4.0.0"],
    "evoid_version": ">=0.4.0",
    "tags": ["cache", "redis"]
}
```

### Manifest Fields

| Field | Required | Description |
|-------|----------|-------------|
| `name` | yes | Must start with `evoid` |
| `version` | yes | Semantic version |
| `type` | yes | `adapter`, `engine`, `language`, or `processor` |
| `description` | no | What the plugin does |
| `author` | no | Plugin author |
| `entry_point` | no | `module:function` format |
| `dependencies` | no | Required packages |
| `evoid_version` | no | Required EVOID version |
| `tags` | no | Discovery tags |

## Creating a Plugin

### Step 1: Package Structure

```
evoid-redis/
  evoid_plugin/
    __init__.py
    evoid_plugin.json
  pyproject.toml
  README.md
```

### Step 2: Implement Entry Point

```python
# evoid_plugin/__init__.py
from evoid.engines.plugin import register

def register_plugin():
    """Called by EVOID to register this plugin."""
    from .cache import RedisCache
    register("redis", "engine", RedisCache, version="1.0.0")
```

### Step 3: pyproject.toml

```toml
[project]
name = "evoid-redis"
version = "1.0.0"
dependencies = ["redis>=4.0.0"]

[project.entry-points."evoid.plugins"]
redis = "evoid_plugin:register_plugin"
```

## Discovery

### Search PyPI

```python
from evoid.engines.plugin import search_plugins

plugins = search_plugins("evoid")
# [{"name": "evoid-redis", "version": "1.0.0"}, ...]
```

### Discover Installed

```python
from evoid.engines.plugin import discover_installed

plugins = discover_installed()
# [PluginManifest(name="evoid-redis", ...), ...]
```

## Installation

### Via evo plug (recommended)

```bash
# From PyPI
evo plug install evoid-redis

# From git
evo plug install git+https://github.com/user/evoid-redis.git

# Search for plugins
evo plug search cache

# List installed
evo plug list
```

### Via uv

```bash
uv add evoid-redis
```

### Via pip

```bash
pip install evoid-redis
```

### Via EVOID Config

```toml
# evoid.toml
[plugins]
engines = ["redis"]

[plugins.redis]
module = "evoid_redis"
factory = "register_plugin"
```

## Plugin Types

| Type | Purpose | Example |
|------|---------|---------|
| `adapter` | Convert external events to Intents | telegram, discord |
| `engine` | Replace infrastructure components | redis, sqlalchemy |
| `language` | Add language runtimes | rust, go |
| `processor` | Add custom pipeline processors | rate_limiter |

## Validation

```python
from evoid.engines.plugin import PluginManifest, validate_manifest

manifest = PluginManifest(
    name="evoid-redis",
    version="1.0.0",
    type="engine",
)

errors = validate_manifest(manifest)
if errors:
    print(f"Invalid: {errors}")
```

## Native IOP Style

In native IOP, plugins are just Intent-based:

```python
from evoid.native import create_service, on
from evoid import Intent, Level
from evoid.engines.plugin import register

# Plugin registers itself
def register_plugin():
    register("redis", "engine", RedisCache, version="1.0.0")

# Service uses the plugin
app = create_service("api")
on(app, Intent(name="cache_get"), handle_cache_get)
```

## Related

- [Plugins](plugins.md) — Plugin system overview
- [Configuration](configuration.md) — Config reference
- [Schema Export](schema-export.md) — Export Intent schemas
