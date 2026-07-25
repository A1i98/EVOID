---
title: 'Parallel Execution'
description: 'Run multiple Intents concurrently with gather().'
---

# Parallel Execution

Run multiple Intents at the same time with `gather()`. Each Intent runs its own pipeline independently.

## Basic Usage

```python
from evoid import Intent, Level, gather

results = await gather(
    Intent(name="get_user", level=Level.STANDARD, metadata={"user_id": 1}),
    Intent(name="get_posts", level=Level.STANDARD, metadata={"user_id": 1}),
    Intent(name="get_notifications", level=Level.EPHEMERAL),
)
# All three run concurrently. Results returned as a tuple.
```

## How It Works

`gather()` creates an asyncio task for each Intent. Each Intent resolves its own pipeline and executes independently. Results are collected in order.

## Error Handling

If one Intent fails, others continue. Each result has its own `success` flag:

```python
results = await gather(intent_a, intent_b, intent_c)
for r in results:
    if not r.success:
        print(f"Failed: {r.error}")
```

## When to Use

Use `gather()` when multiple Intents have no dependencies between them. If Intent B needs Intent A's result, run them sequentially instead.

## Priority

Set priority in metadata to control execution order when using the scheduler plugin:

```python
Intent(name="critical_task", level=Level.CRITICAL, metadata={"priority": 100})
```

## Related

- [Intent](intent.md): level and metadata
- [Pipeline](pipeline.md): how each Intent executes
