# CLI

EVOID comes with a powerful CLI tool called `evo`.

## Installation

The CLI is automatically installed with EVOID:

```bash
uv add evoid
```

## Commands

### Project Management

```bash
# Create a new project
evo init my-api

# Navigate to project
cd my-api
```

### Service Management

```bash
# Add a new service
evo service new api

# List all services
evo service list

# Run a specific service
evo service run api
```

### Development

```bash
# Sync dependencies
evo sync

# Run all services
evo run

# Quick serve (development)
evo serve
```

### Information

```bash
# Show version
evo version

# List all intents
evo list-intents

# Execute a command
evo exec <command>
```

## Configuration

The CLI reads configuration from `evoid.toml` files:

```toml
[service]
name = "my-api"
version = "1.0.0"

[engines]
schema = "pydantic"
storage = "memory"
```

## Examples

```bash
# Full workflow
evo init my-project
cd my-project
evo service new api
evo sync
evo service run api
```
