---
title: 'Parallel Orders'
description: 'Process multiple orders concurrently. gather(), priority, concurrency limits.'
---

# Parallel Orders

Process multiple orders concurrently. gather(), priority, concurrency limits.

## The Problem

Sandy's 4 locations process 100+ orders per hour. Sequential processing is too slow.

## Parallel Execution

```python
from evoid import Intent, Level
from evoid.core.parallel import gather

# Define intents for each location
orders = [
    Intent(name="process_order", level=Level.STANDARD, metadata={"location": "downtown", "sandwich": "BLT"}),
    Intent(name="process_order", level=Level.STANDARD, metadata={"location": "mall", "sandwich": "Club"}),
    Intent(name="process_order", level=Level.STANDARD, metadata={"location": "airport", "sandwich": "Veggie"}),
    Intent(name="process_order", level=Level.STANDARD, metadata={"location": "university", "sandwich": "Reuben"}),
]

# Process all at once
results = await gather(orders)

for result in results:
    if result.success:
        print(f"Order processed: {result.value}")
    else:
        print(f"Order failed: {result.error}")
```

## Priority Ordering

Process urgent orders first:

```python
from evoid.core.parallel import gather_with_priority

orders = [
    Intent(name="process_order", level=Level.CRITICAL, priority=10, metadata={"sandwich": "VIP"}),
    Intent(name="process_order", level=Level.STANDARD, priority=5, metadata={"sandwich": "BLT"}),
    Intent(name="process_order", level=Level.EPHEMERAL, priority=1, metadata={"sandwich": "Veggie"}),
]

# Process in priority order
results = await gather_with_priority(orders)
```

## Concurrency Limits

Don't overload the kitchen:

```python
from evoid.core.parallel import gather

# Max 3 concurrent orders
results = await gather(orders, concurrency=3)
```

## Thread Offloading

For CPU-bound work (e.g., image processing):

```python
from evoid.core.parallel import run_in_thread_async

async def process_image(image_path: str) -> dict:
    # CPU-bound work runs in a thread pool
    result = await run_in_thread_async(heavy_computation, image_path)
    return {"processed": result}
```

## Sequential vs Parallel

```python
import time
from evoid import execute, Intent, Level
from evoid.core.parallel import gather

# Sequential: 4 × 0.5s = 2s
start = time.time()
for intent in orders:
    await execute(intent)
print(f"Sequential: {time.time() - start:.1f}s")

# Parallel: 0.5s total
start = time.time()
await gather(orders)
print(f"Parallel: {time.time() - start:.1f}s")
```

## What You Learned

| Concept | What It Is |
|---------|-----------|
| `gather()` | Execute multiple Intents concurrently |
| `gather_with_priority()` | Priority-ordered execution |
| Concurrency limits | Max concurrent executions |
| Thread offloading | CPU-bound work in thread pool |

## Next: Performance

Let's optimize Sandy's system — [Performance](performance.md).
