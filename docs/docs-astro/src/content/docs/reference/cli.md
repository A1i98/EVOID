---
title: 'CLI Reference'
description: 'Complete reference for the evo command-line interface.'
---

# CLI Reference

`evo` is the EVOID CLI. Every command has a short alias.

| Alias | Full | Example |
|-------|------|---------|
| `i` | `init` | `evo i my-app` |
| `s` | `service` | `evo s new api` |
| `r` | `run` | `evo r` |
| `sv` | `serve` | `evo sv` |
| `v` | `version` | `evo v` |
| `li` | `list-intents` | `evo li` |
| `lp` | `list-processors` | `evo lp` |
| `e` | `exec` | `evo e get_user` |
| `ins` | `install` | `evo ins sqlite` |
| `pl` | `plug` | `evo pl i redis` |

## Project

### `evo init <name>`

Create a new EVOID project with `pyproject.toml`, `evoid.toml`, and `services/` directory.

```bash
evo init my-app
cd my-app
```

Output:
```
Created project: my-app
  pyproject.toml
  evoid.toml
  services/
```

### `evo version`

Show EVOID version.

```bash
evo version
# EVOID 0.6.6
```

!!! info "cwd-independence"
    All `evo` commands work from any directory inside the project tree. The CLI walks up from `cwd` to find the project root (the directory containing `pyproject.toml`). You don't need to be in the project root — just somewhere inside it.

## Service

### `evo service new <name> [port]`

Add a new service to the project. Creates `services/<name>/evoid.toml` and `services/<name>/main.py`.

```bash
evo service new api 8000
evo service new worker 8001
```

### `evo service list`

List all services in the project.

```bash
evo service list
# Services:
#   api (port 8000)
#   worker (port 8001)
```

### `evo service run <name>`

Run a specific service.

```bash
evo service run api
# Running service 'api' on http://0.0.0.0:8000
```

## Global

### `evo sync`

Sync dependencies and pipelines for all services.

```bash
evo sync                    # All services
evo sync --service api      # Single service
evo sync --show             # Show without installing
```

### `evo run`

Run all services in the project.

```bash
evo run
# Starting all services...
#   api: http://0.0.0.0:8000
#   worker: http://0.0.0.0:8001
```

### `evo serve [host] [port]`

Quick serve a single service (default: `0.0.0.0:8000`).

```bash
evo serve                   # 0.0.0.0:8000
evo serve localhost 3000    # localhost:3000
```

### `evo list-intents`

List all registered Intents with their levels and pipelines.

```bash
evo list-intents
# Intents:
#   get_user          STANDARD   validate → authorize → get_user
#   process_payment   CRITICAL   validate → authorize → audit → protect → process_payment
#   cache_check       EPHEMERAL  validate → cache_check
```

### `evo list-processors`

List all registered processors.

```bash
evo list-processors
# Processors:
#   validate
#   authorize
#   audit
#   protect
#   get_user
#   process_payment
```

### `evo exec <intent_name>`

Execute an Intent by name. Useful for testing.

```bash
evo exec get_user
# Result: success=True, value={'user': 'Alice'}, duration=0.002s
```

## Install

### `evo install <package>`

Install built-in extras or common plugins.

```bash
# Extras (built-in optional dependencies)
evo install sqlite         # → evoid[sqlite]
evo install redis          # → evoid[redis]
evo install sqlalchemy     # → evoid[sqlalchemy]
evo install pydantic       # → evoid[pydantic]
evo install full           # All optional dependencies

# Plugins (from evoid-plugins)
evo install di             # → evoid-di
evo install auth           # → evoid-auth
evo install tasks          # → evoid-tasks
evo install smart-storage  # → evoid-smart-storage
evo install scylla         # → evoid-scylla
evo install dashboard      # → evoid-dashboard
```

## Plug

### `evo plug install <name|url>`

Install plugins from PyPI or git.

```bash
evo plug install evoid-redis              # From PyPI
evo plug install git+https://github.com/user/evoid-redis.git  # From git
evo plug install redis                    # Short name (maps to evoid-redis)
```

### `evo plug search <query>`

Search PyPI for plugins.

```bash
evo plug search cache
# Found 3 plugins:
#   evoid-redis                  0.1.2
#   evoid-memory-cache           0.1.0
```

### `evo plug list`

List installed plugins.

```bash
evo plug list
# evoid-redis                  0.1.2      engine
# evoid-di                     0.1.2      engine
# evoid-auth                   0.1.2      engine
```
