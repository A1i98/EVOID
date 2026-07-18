---
title: 'IOP Levels'
description: 'Three levels of IOP — from simple dicts to production systems. Start simple, upgrade when it hurts.'
---

# IOP Levels

IOP has three levels. Each adds structure when you need it. Start from Level 1, upgrade only when it hurts.

!!! tip "Golden Rule"
    > Start from Level 1. Upgrade only when it hurts. Never start at Level 3.

## Level 1: Dict + Functions

**When:** Scripts, small tools, <10 commands, single file.

The simplest form of IOP. Data is a dict. Processors are functions. The pipeline is a list.

```python
from evoid import Intent, Level, execute
from evoid.core import Context

# Level 1: Data is just a dict
state = {"volume": 75, "device": None}

# Level 1: Processors are plain functions
async def detect_device(ctx: Context) -> dict:
    device = {"name": "AirPods", "connected": True}
    ctx.state["device"] = device
    return {"detected": True}

async def set_volume(ctx: Context) -> dict:
    vol = ctx.state.get("volume", 50)
    device = ctx.state.get("device")
    if device:
        device["volume"] = vol
    return {"volume_set": vol}

# Level 1: Register and execute
from evoid import register_processor
register_processor("detect_device", detect_device)
register_processor("set_volume", set_volume)

intent = Intent(
    name="configure",
    level=Level.STANDARD,
    pipeline=("detect_device", "set_volume"),
)

result = await execute(intent)
# result.value = {"volume_set": 75}
```

**What you get:**
- Dicts for data — no imports, no classes
- Functions for logic — no registration ceremony
- Pipeline for composition — explicit, readable

**What you don't get:**
- Type safety (dicts are untyped)
- IDE autocomplete
- Validation

## Level 2: TypedDict + Compose

**When:** Medium CLIs, 10-30 commands, solo developer, need type hints.

Add type hints to your dicts. Use function composition for pipelines.

```python
from typing import TypedDict, NotRequired
from evoid import Intent, Level, execute
from evoid.core import Context

# Level 2: TypedDict gives you type hints
class DeviceState(TypedDict, total=False):
    device: dict
    volume: int
    error: str | None
    nc_enabled: bool

# Level 2: Processors are typed functions
async def detect_device(ctx: Context) -> dict:
    ctx.state["device"] = {"name": "AirPods", "connected": True}
    return {"detected": True}

async def enable_nc(ctx: Context) -> dict:
    device = ctx.state.get("device")
    if device:
        ctx.state["nc_enabled"] = True
    return {"nc_enabled": True}

async def set_volume(ctx: Context) -> dict:
    vol = ctx.state.get("volume", 50)
    ctx.state["volume"] = vol
    return {"volume_set": vol}

# Level 2: Pipeline is explicit
from functools import reduce

pipeline = [detect_device, enable_nc, set_volume]

# Level 2: Compose manually or use EVOID pipeline
intent = Intent(
    name="configure",
    level=Level.STANDARD,
    pipeline=("detect_device", "enable_nc", "set_volume"),
)

from evoid import register_processor
register_processor("detect_device", detect_device)
register_processor("enable_nc", enable_nc)
register_processor("set_volume", set_volume)

result = await execute(intent)
```

**What you get:**
- Type hints — IDE autocomplete, error catching
- TypedDict — structured data without classes
- Clear pipeline — each step is visible

**What you don't get:**
- Immutability (TypedDict is mutable)
- Schema validation
- Complex state machines

## Level 3: Dataclass + Decorator

**When:** Production systems, teams 5+, complex state machines, need validation.

Frozen dataclasses for immutable data. Decorators for registration. Full IOP.

```python
from dataclasses import dataclass, field
from evoid import Intent, Level, execute, register_processor
from evoid.core import Context

# Level 3: Frozen dataclass — immutable, validated
@dataclass(frozen=True)
class DeviceState:
    device: dict = field(default_factory=dict)
    volume: int = 50
    nc_enabled: bool = False
    error: str | None = None

# Level 3: Processors are typed, registered, composable
async def detect_device(ctx: Context) -> dict:
    ctx.state["device"] = {"name": "AirPods", "connected": True}
    return {"detected": True}

async def enable_nc(ctx: Context) -> dict:
    device = ctx.state.get("device")
    if device:
        ctx.state["nc_enabled"] = True
    return {"nc_enabled": True}

async def set_volume(ctx: Context) -> dict:
    vol = ctx.state.get("volume", 50)
    ctx.state["volume"] = vol
    return {"volume_set": vol}

# Level 3: Intent with full control
CONFIGURE = Intent(
    name="configure",
    level=Level.STANDARD,
    pipeline=("detect_device", "enable_nc", "set_volume"),
    timeout=10.0,
    priority=0,
)

# Level 3: Register processors
register_processor("detect_device", detect_device)
register_processor("enable_nc", enable_nc)
register_processor("set_volume", set_volume)

# Level 3: Execute with full Result
result = await execute(
    CONFIGURE,
    context=Context(intent=CONFIGURE),
)

if result.success:
    print(f"Done in {result.duration:.3f}s")
    print(f"Processors: {result.processors}")
else:
    print(f"Failed: {result.error}")
```

**What you get:**
- Frozen dataclasses — immutable, thread-safe
- Full Result — timing, processor list, error details
- Pipeline control — custom pipelines, extensions
- Plugin system — engines, adapters, processors

**What you don't get:**
- Simplicity — more code, more concepts

## Comparison

| Feature | Level 1 | Level 2 | Level 3 |
|---------|---------|---------|---------|
| Data | `dict` | `TypedDict` | `dataclass(frozen=True)` |
| Type hints | No | Yes | Yes + validation |
| Immutability | No | No | Yes |
| Registration | Manual | Manual | Decorator or manual |
| Pipeline | List of names | List of names | List of names + config |
| Best for | Scripts | Medium CLIs | Production systems |
| EVOID uses | Processors | — | Intent, Context, Result |

## How EVOID Uses All Three

EVOID itself is built with Level 3 (frozen dataclasses + functions). But you can use any level in your project:

```python
# Level 1 in your script
async def my_processor(ctx: Context) -> dict:
    return {"result": "ok"}

# Level 2 in your CLI
class MyState(TypedDict):
    input: str
    output: str

# Level 3 in your service
@dataclass(frozen=True)
class MyConfig:
    name: str
    version: str
    debug: bool = False
```

The runtime doesn't care which level you use. It executes processors by name. Your data stays your data.

## When to Upgrade

| Signal | Action |
|--------|--------|
| "I keep passing the wrong keys" | Upgrade to Level 2 (TypedDict) |
| "Two devs keep breaking state" | Upgrade to Level 3 (frozen dataclass) |
| "I need to audit who changed what" | Upgrade to Level 3 (frozen dataclass) |
| "I'm over-engineering this" | Stay at Level 1 |
