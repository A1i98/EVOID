---
title: 'Debugging'
description: 'Debug EVOID services with logging, tracing, and inspection tools.'
---

# Debugging

Debug EVOID services with logging, tracing, and inspection tools.

## Basic Logging with loguru

Use loguru for structured logging:

```python
from loguru import logger
from evoid.web.route import Service, get

app = Service("api")

@app.get("/items/{item_id}")
async def get_item(item_id: int):
    logger.debug(f"Fetching item {item_id}")
    
    if item_id > 100:
        logger.warning(f"Item {item_id} might not exist")
        return {"error": "Item not found"}
    
    logger.info(f"Successfully fetched item {item_id}")
    return {"item_id": item_id, "name": "Widget"}
```

!!! tip "Log levels"
    Use `debug` for detailed info, `info` for normal operations, `warning` for potential issues, `error` for failures.

## Pipeline Tracing with logger_processor

Add a logging processor to trace pipeline execution:

```python
from evoid.core import Context, register_processor
from loguru import logger

async def logger_processor(ctx: Context) -> dict:
    logger.info(f"Intent: {ctx.intent.name}")
    logger.info(f"Metadata: {ctx.metadata}")
    logger.info(f"State: {ctx.state}")
    return {"logged": True}

# Register for all intents
register_processor("*", logger_processor)

# Or register for specific intent
register_processor("GET:/items", logger_processor)
```

## Inspecting Intent Metadata

Debug by inspecting intent metadata in handlers:

```python
from evoid.web.route import Service, get, before
from evoid.core import Context
from loguru import logger

async def debug_metadata(ctx: Context) -> dict:
    logger.debug("=== Intent Metadata ===")
    logger.debug(f"Method: {ctx.metadata.get('method')}")
    logger.debug(f"Path: {ctx.metadata.get('path')}")
    logger.debug(f"Headers: {ctx.metadata.get('headers')}")
    logger.debug(f"Query params: {ctx.metadata.get('params')}")
    logger.debug(f"Body: {ctx.metadata.get('body')}")
    logger.debug(f"Path params: {ctx.metadata.get('path_params')}")
    return {"debugged": True}

app = Service("api")

@app.get("/debug/")
async def debug_endpoint():
    return {"status": "ok"}

before("GET:/debug", "debug_metadata")
```

## Debug Mode

Run services in debug mode for verbose output:

```python
from evoid.web.route import Service

# Enable debug mode
app = Service("api", debug=True)

# Or configure via environment
import os
os.environ["EVOID_DEBUG"] = "true"
```

!!! warning "Production"
    Never enable debug mode in production — it exposes sensitive information and reduces performance.

## CLI Debug Flag

Use the `--debug` flag when running services:

```bash
# Run with debug output
evo service run --debug

# Run specific service
evo service run my_service --debug

# Run with custom log level
evo service run --log-level DEBUG
```

## Native IOP Debugging

Debug native IOP services:

```python
from evoid.native import create_service, on
from evoid import Intent, Level
from loguru import logger

app = create_service("api")

GET_ITEMS = Intent(
    name="GET:/items",
    level=Level.STANDARD,
    metadata={"method": "GET", "path": "/items"},
)

async def handle_get_items(intent: Intent) -> dict:
    logger.debug(f"Intent received: {intent.name}")
    logger.debug(f"Metadata: {intent.metadata}")
    
    # Debug logic
    params = intent.metadata.get("params", {})
    logger.debug(f"Query params: {params}")
    
    return {"items": [], "debug": True}

on(app, GET_ITEMS, handle_get_items)
```

## Summary

| Approach | When to Use |
|----------|-------------|
| Basic logging | Track normal operations |
| Pipeline tracing | Understand request flow |
| Metadata inspection | Debug request data |
| Debug mode | Development environment |
| CLI flags | Runtime debugging |