---
title: 'Plugin Ecosystem'
description: 'Build your own EVOID plugins — extend the runtime with custom engines, adapters, and processors.'
---

# Plugin Ecosystem

Build your own EVOID plugins. Extend the runtime with custom engines, adapters, and processors. Share them with the community.

## Why Build Plugins?

- **Composability** — Mix and match infrastructure components
- **Reusability** — Write once, use across projects
- **Community** — Share solutions with other EVOID users
- **Marketplace** — Publish to PyPI for discovery

## Plugin Anatomy

Every plugin has three parts:

1. **Manifest** (`evoid_plugin.json`) — metadata
2. **Entry point** (`register_plugin()`) — registration function
3. **Implementation** — your engine, adapter, or processor

## Quick Start: Your First Plugin

### Step 1: Create the package

```
evoid-hello/
  evoid_hello/
    __init__.py
    evoid_plugin.json
  pyproject.toml
  README.md
```

### Step 2: Write the manifest

```json
{
  "name": "evoid-hello",
  "version": "1.0.0",
  "type": "engine",
  "description": "Hello world engine for EVOID",
  "entry_point": "evoid_hello:register_plugin",
  "evoid_version": ">=0.4.0"
}
```

### Step 3: Implement the engine

```python
# evoid_hello/__init__.py
from evoid.engines.plugin import register

async def hello_read(key: str) -> str:
    return f"Hello from {key}!"

async def hello_write(key: str, value: str) -> bool:
    print(f"Stored: {key} = {value}")
    return True

async def hello_delete(key: str) -> bool:
    return True

async def hello_health() -> bool:
    return True

def register_plugin():
    """Called by EVOID to register this plugin."""
    register(
        name="hello",
        type="engine",
        factory=lambda: {
            "read": hello_read,
            "write": hello_write,
            "delete": hello_delete,
            "health": hello_health,
        },
        version="1.0.0",
        description="Hello world engine",
    )
```

### Step 4: Package it

```toml
# pyproject.toml
[project]
name = "evoid-hello"
version = "1.0.0"
dependencies = ["evoid>=0.4.0"]

[project.entry-points."evoid.plugins"]
hello = "evoid_hello:register_plugin"
```

### Step 5: Install and use

```bash
uv add -e .
```

```toml
# evoid.toml
[engines]
storage = "hello"
```

## Plugin Types

| Type | Purpose | Example |
|------|---------|---------|
| `engine` | Replace infrastructure | Storage, cache, serializer |
| `adapter` | Convert external events | Telegram, Discord, MQTT |
| `processor` | Add pipeline steps | Rate limiter, auth checker |
| `language` | Add language runtimes | Rust, Go |

## Contracts

Implement the contract for your plugin type:

### Storage Engine

```python
from evoid.contracts import StorageEngine

class MyStorage:
    async def read(self, key: str) -> Any | None: ...
    async def write(self, key: str, value: Any) -> bool: ...
    async def delete(self, key: str) -> bool: ...
    async def health(self) -> bool: ...
```

### Cache Engine

```python
from evoid.contracts import CacheEngine

class MyCache:
    async def get(self, key: str) -> Any | None: ...
    async def set(self, key: str, value: Any, ttl: float | None = None) -> bool: ...
    async def delete(self, key: str) -> bool: ...
    async def health(self) -> bool: ...
```

### Processor

```python
from evoid import register_processor

async def my_processor(ctx: Context) -> dict:
    # Your logic here
    return {"processed": True}

register_processor("my_processor", my_processor)
```

## Publishing to PyPI

### Step 1: Build

```bash
python -m build
```

### Step 2: Upload

```bash
twine upload dist/*
```

### Step 3: Verify

```bash
evo plug search hello
evo plug install evoid-hello
```

## Testing Your Plugin

```python
import pytest
from evoid import Intent, Level, execute
from evoid_hello import register_plugin

def test_hello_engine():
    register_plugin()
    
    intent = Intent(
        name="test_hello",
        level=Level.STANDARD,
        pipeline=("hello_read",),
    )
    
    result = await execute(intent)
    assert result.success
```

## Best Practices

1. **Follow the contract** — Implement the full interface
2. **Zero dependencies** — Don't require packages beyond evoid
3. **Async-native** — All methods should be async
4. **Health checks** — Always implement `health()`
5. **Error handling** — Raise clear exceptions

## Related

- [Plugin Standard](plugin-standard.md) — Full packaging spec
- [Plugin Collection](plugin-collection.md) — Official plugins
- [Plugins and Engines](plugins.md) — Built-in engines
