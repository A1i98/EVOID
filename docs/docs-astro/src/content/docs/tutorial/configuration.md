---
title: 'Configuration'
description: 'Configure your EVOID app — engines, pipelines, environments.'
---

# Configuration

Configure your EVOID app — engines, pipelines, environments.

## evoid.toml

The main configuration file:

```toml
[project]
name = "sandy-shop"
version = "1.0.0"

[runtime]
adapter = "asgi"
host = "0.0.0.0"
port = 8000

[engines]
schema = "native"
storage = "memory"
cache = "memory"
logger = "loguru"

[pipeline]
timeout = 10.0
processors = ["validate", "authorize"]
```

## Python Config (Recommended)

Python files give you type safety and IDE autocomplete:

```python
# evoid_config.py
from evoid.core.runtime import Config

config = Config(
    name="sandy-shop",
    adapter="asgi",
    engines={
        "schema": "native",
        "storage": "sqlite",
        "cache": "memory",
        "logger": "loguru",
    },
)
```

## Engine Selection

Each engine is a plugin — swap implementations without changing code:

| Engine | Purpose | Options |
|--------|---------|---------|
| `schema` | Validation | `native` (stdlib) |
| `storage` | Persistence | `memory`, `sqlite` |
| `cache` | Caching | `memory`, `redis` |
| `logger` | Logging | `loguru`, `stdlib` |

## Environment Config

Different configs for different environments:

```python
# config/development.py
config = Config(
    name="sandy-dev",
    adapter="asgi",
    engines={"storage": "memory", "cache": "memory"},
)

# config/production.py
config = Config(
    name="sandy-prod",
    adapter="asgi",
    engines={"storage": "sqlite", "cache": "redis"},
)
```

## Pipeline Defaults

Set default pipeline behavior per level:

```python
from evoid.core.resolver import set_default_pipeline

set_default_pipeline("ephemeral", ["validate"], timeout=5.0)
set_default_pipeline("standard", ["validate", "authorize"], timeout=10.0)
set_default_pipeline("critical", ["validate", "authorize", "audit"], timeout=30.0)
```

## What You Learned

| Concept | What It Is |
|---------|-----------|
| `evoid.toml` | Declarative config file |
| Python config | Type-safe, IDE-friendly config |
| Engine selection | Swap implementations via config |
| Pipeline defaults | Set behavior per level |

## Next: Testing

Let's test Sandy's API — [Testing](testing.md).
