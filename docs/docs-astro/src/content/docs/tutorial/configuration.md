---
title: 'Configuration'
description: 'Configure your EVOID app — engines, pipelines, environments. See [Configuration Reference](../learn/configuration.md) for full details.'
---

# Configuration

Configure your EVOID app — engines, pipelines, environments.

> **Full reference:** [Configuration Reference](../learn/configuration.md) — complete field reference, examples, and engine map.

## Quick Start

```toml
# evoid.toml
[service]
name = "my-api"
version = "1.0.0"

[runtime]
adapter = "asgi"
port = 8000

[engines]
schema = "native"
storage = "memory"
cache = "memory"
logger = "loguru"
```

```python
# evoid_config.py (recommended)
from evoid.config import config

app = config(
    service={"name": "my-api", "version": "1.0.0"},
    runtime={"adapter": "asgi", "port": 8000},
    engines={"storage": "memory", "cache": "memory"},
)
```

## Environment Configs

```python
# config/development.py
config = config(
    name="my-dev",
    engines={"storage": "memory", "cache": "memory"},
)

# config/production.py
config = config(
    name="my-prod",
    engines={"storage": "sqlite", "cache": "redis"},
)
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