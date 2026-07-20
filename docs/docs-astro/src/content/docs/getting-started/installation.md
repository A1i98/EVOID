---
title: 'Installation'
description: 'Install EVOID with zero core dependencies. Add only what you need.'
---

# Installation

## Requirements

- Python 3.12+
- [uv](https://docs.astral.sh/uv/)

!!! tip "Why uv?"
    `uv` is 10-100x faster than pip and handles virtual environments automatically. Install it from [astral.sh/uv](https://docs.astral.sh/uv/).

## Install EVOID

```bash
uv add evoid
```

!!! info "Zero core dependencies"
    EVOID has NO required dependencies. Install only what you need.

## Optional Dependencies

Install extras for specific features. Core EVOID has zero required dependencies.

### Built-in Extras

```bash
# ASGI server (starlette + uvicorn)
uv add "evoid[asgi]"

# Pydantic schema engine
uv add "evoid[pydantic]"

# SQLite storage
uv add "evoid[sqlite]"

# Loguru logging
uv add "evoid[loguru]"

# TOML config support
uv add "evoid[toml]"

# Testing WebUI
uv add "evoid[testing]"

# Everything
uv add "evoid[full]"
```

| Extra | Packages | Use When |
|-------|----------|----------|
| `asgi` | starlette, uvicorn | Running HTTP APIs |
| `pydantic` | pydantic | Schema validation with Pydantic models |
| `sqlite` | aiosqlite | SQLite database storage |
| `loguru` | loguru | Beautiful structured logging |
| `toml` | tomli, tomli_w | TOML config support |
| `testing` | starlette | Test dashboard WebUI |
| `full` | All above | Everything enabled |

### Using evo install

```bash
evo install sqlite        # Install SQLite storage
evo install full          # Install all optional deps
```

### Plugins (Advanced)

Need Redis, PostgreSQL, or advanced features? Install plugins from PyPI:

```bash
# Short names — evo maps them to full package names automatically
evo plug install redis           # → evoid-redis
evo plug install postgresql      # → evoid-postgresql
evo plug install di              # → evoid-di
evo plug install auth            # → evoid-auth

# Some plugins need full package names (no short name available)
evo plug install evoid-scheduler   # Priority scheduler
evo plug install evoid-cluster     # Multi-node clustering
evo plug install evoid-godot       # Godot game hosting

# Search for plugins
evo plug search cache

# List installed
evo plug list
```

!!! info "Short names vs full names"
    `evo plug install` supports short names for common plugins. The CLI automatically maps `di` → `evoid-di`, `redis` → `evoid-redis`, etc. You can also use the full package name — both work. For plugins without a short name (like `evoid-scheduler`), use the full name.

## Verify Installation

```bash
evo version
```

Expected output:

```
evo 0.4.1
```

## Create Your First Project

```bash
evo init my-api
cd my-api
evo service new api
evo service run api
```

Server starts at `http://0.0.0.0:8000`. Test it:

```bash
curl http://localhost:8000/
```
