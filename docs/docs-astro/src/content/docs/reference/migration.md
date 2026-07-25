---
title: 'Migration Guide'
description: 'Before/after code snippets for every breaking change between versions.'
---

# Migration Guide

## 0.4.0 → 0.4.1

### Python version requirement lowered

```bash
# Before (0.4.0)
# Required Python 3.13+

# After (0.4.1)
# Requires Python 3.12+
```

### `tomli_w` moved to optional

```bash
# Before (0.4.0)
pip install evoid  # tomli_w was required

# After (0.4.1)
pip install evoid          # tomli_w NOT installed
pip install evoid[toml]    # Install if you need TOML writing
```

### `evo install` command added

```bash
# Before (0.4.0)
pip install evoid[sqlite]

# After (0.4.1)
evo install sqlite
```

## 0.4.1 → 0.5.0

### `tomli_w` is now a core dependency again

```bash
# Before (0.4.1)
pip install evoid  # tomli_w NOT included

# After (0.5.0)
pip install evoid  # tomli_w included (required for project scaffolding)
```

### Zero-deps claim corrected

The README and docs previously claimed "zero dependencies." This was inaccurate. `tomli_w` is required for `evo init` and `evo service new` to write TOML config files.

```python
# Before: misleading
# "EVOID has zero dependencies"

# After: accurate
# "EVOID has 1 required dependency: tomli_w"
```

## 0.3.x → 0.4.0

### Intent Schema Export

```python
# Before (0.3.x)
from evoid import export_schemas  # Did not exist

# After (0.4.0)
from evoid import export_schemas, export_json_schemas
schemas = export_schemas()
json_schemas = export_json_schemas()
```

### Plugin Lifecycle Hooks

```python
# Before (0.3.x)
from evoid import on_event  # Did not exist

# After (0.4.0)
from evoid import on_event, Event
def log(ctx): print(ctx.intent_name)
on_event(Event.POST_EXECUTE, log)
```

### Pipeline event flow

Pipeline now emits `pre_execute` and `post_execute` events. If you had custom processors that depended on the old single-event flow, update them.

## 0.3.3 → 0.4.0

### Context IDs

Context uses fast counter-based IDs instead of UUID4. If you stored Context IDs externally, they're now integers, not UUID strings.

```python
# Before (0.3.3)
ctx.id  # "a1b2c3d4-e5f6-7890-abcd-ef1234567890"

# After (0.4.0)
ctx.id  # 1, 2, 3, ...
```
