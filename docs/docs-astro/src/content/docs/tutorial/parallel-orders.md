---
title: 'Parallel Orders'
description: 'Process multiple orders concurrently. gather(), priority, concurrency limits.'
---

# Parallel Orders

Process multiple orders concurrently. gather(), priority, concurrency limits.

## The Problem

Sandy's 4 locations process 100+ orders per hour. Sequential processing is too slow.

!!! info "Parallel = multiple cooks"
    One cook makes sandwiches one at a time. Four cooks make four at once. But you need to decide who gets the premium ingredients first — that's priority.

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

## The Scheduler Plugin

The `evoid-scheduler` plugin goes further — it watches system load and defers low-priority tasks when the CPU is busy:

```python
from evoid_scheduler import SchedulerEngine, Priority

scheduler = SchedulerEngine()

# High-priority order goes first — always
scheduler.submit(process_vip_order, priority=Priority.CRITICAL)  # 100

# Normal order — runs when capacity exists
scheduler.submit(process_normal_order, priority=Priority.NORMAL)  # 50

# Analytics sync — deferred if CPU is overloaded
scheduler.submit(sync_analytics, priority=Priority.LOW)  # 25
```

!!! example "IOP: priority in metadata"
    ```python
    # Priority declared in Intent metadata
    VIP_ORDER = Intent(
        name="process_order",
        level=Level.CRITICAL,
        metadata={"priority": Priority.CRITICAL},  # 100
        location="downtown",
    )
    
    NORMAL_ORDER = Intent(
        name="process_order",
        level=Level.STANDARD,
        metadata={"priority": Priority.NORMAL},  # 50
        location="mall",
    )
    
    ANALYTICS_SYNC = Intent(
        name="sync_analytics",
        level=Level.EPHEMERAL,
        metadata={"priority": Priority.LOW},  # 25
    )
    
    # Scheduler reads system load:
    # - CPU < 80%: all run immediately
    # - CPU > 80%: LOW intents get deferred to a queue
    # - CPU > 95%: NORMAL intents get deferred too
    # CRITICAL always runs. Your code doesn't know this happens.
    ```

## Next: Performance

Let's optimize Sandy's system — [Performance](performance.md).
