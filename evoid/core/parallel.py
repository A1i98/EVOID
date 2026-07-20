"""Parallel — Async, multi-thread, and parallel execution.

IOP: Parallel execution is just function composition.
Users can:
1. Run intents in parallel (gather)
2. Run intents with priority ordering
3. Control concurrency limits
4. Use thread pools for CPU-bound work
"""

from __future__ import annotations

import asyncio
import os
from collections.abc import Awaitable, Callable
from concurrent.futures import ThreadPoolExecutor
from dataclasses import dataclass, field
from typing import Any, Protocol

from .intent import Intent
from .pipeline import Result
from .runtime import execute as execute_intent

# ============================================================
# System metrics
# ============================================================


@dataclass(frozen=True)
class SystemMetrics:
    """System state snapshot."""

    cpu_cores: int
    cpu_count_logical: int
    load_avg_1m: float
    load_avg_5m: float
    load_avg_15m: float
    memory_total_mb: float
    memory_available_mb: float

    @property
    def is_overloaded(self) -> bool:
        """System is overloaded if load > logical cores."""
        return self.load_avg_1m > self.cpu_count_logical

    @property
    def recommended_concurrency(self) -> int:
        """Suggested concurrency based on load."""
        if self.is_overloaded:
            return max(1, self.cpu_count_logical // 2)
        return self.cpu_count_logical


def get_system_metrics() -> SystemMetrics:
    """Get current system metrics."""
    try:
        import resource

        load = os.getloadavg()
        mem_info = resource.getrusage(resource.RUSAGE_SELF)
        # Rough estimate: ru_maxrss is in KB on Linux, bytes on macOS
        mem_mb = mem_info.ru_maxrss / 1024
    except (OSError, AttributeError):
        load = (0.0, 0.0, 0.0)
        mem_mb = 0.0

    try:
        with open("/proc/meminfo") as f:
            lines = f.readlines()
        mem_total = int(lines[0].split()[1]) / 1024  # KB to MB
        mem_avail = int(lines[2].split()[1]) / 1024
    except (FileNotFoundError, IndexError, ValueError):
        mem_total = mem_mb
        mem_avail = mem_mb

    return SystemMetrics(
        cpu_cores=os.cpu_count() or 4,
        cpu_count_logical=os.cpu_count() or 4,
        load_avg_1m=load[0],
        load_avg_5m=load[1],
        load_avg_15m=load[2],
        memory_total_mb=mem_total,
        memory_available_mb=mem_avail,
    )


# ============================================================
# Scheduler backend protocol (for plugins)
# ============================================================


class SchedulerBackend(Protocol):
    """Protocol for scheduler plugins (e.g., evoid-scheduler with PyO3)."""

    async def submit(self, intent: Intent, priority: int = 0) -> str: ...

    async def cancel(self, task_id: str) -> bool: ...

    async def defer(self, intent: Intent, until: float) -> str: ...

    def metrics(self) -> SystemMetrics: ...

    @property
    def queue_size(self) -> int: ...

    @property
    def active_workers(self) -> int: ...


# ============================================================
# Thread pool for CPU-bound work
# ============================================================

_thread_pool: ThreadPoolExecutor | None = None


def _get_thread_pool() -> ThreadPoolExecutor:
    """Get or create thread pool."""
    global _thread_pool
    if _thread_pool is None:
        _thread_pool = ThreadPoolExecutor(max_workers=os.cpu_count() or 4)
    return _thread_pool


def configure_thread_pool(max_workers: int | None = None) -> None:
    """Configure thread pool. Call before first use."""
    global _thread_pool
    if _thread_pool is not None:
        _thread_pool.shutdown(wait=False)
    _thread_pool = ThreadPoolExecutor(max_workers=max_workers or os.cpu_count() or 4)


async def gather(
    *intents: Intent,
    concurrency: int = 10,
    return_exceptions: bool = False,
) -> list[Result]:
    """Execute multiple intents in parallel.

    Usage:
        results = await gather(intent1, intent2, intent3)
        results = await gather(intent1, intent2, concurrency=5)
    """
    semaphore = asyncio.Semaphore(concurrency)

    async def limited_execute(intent: Intent) -> Result:
        async with semaphore:
            return await execute_intent(intent)

    tasks = [limited_execute(intent) for intent in intents]
    return await asyncio.gather(*tasks, return_exceptions=return_exceptions)


async def gather_with_priority(
    *intents: Intent,
    concurrency: int | None = None,
    backend: SchedulerBackend | None = None,
) -> list[Result]:
    """Execute intents with true priority ordering.

    Higher priority intents execute first.
    If backend is provided, delegates to plugin scheduling.
    """
    if backend is not None:
        task_ids = []
        for intent in intents:
            tid = await backend.submit(intent, intent.priority)
            task_ids.append(tid)
        # Results collected via backend.result()
        return []

    # Built-in: concurrent with priority ordering
    sorted_intents = sorted(intents, key=lambda i: i.priority, reverse=True)
    effective_concurrency = concurrency or len(sorted_intents)
    semaphore = asyncio.Semaphore(effective_concurrency)

    async def limited_execute(intent: Intent) -> Result:
        async with semaphore:
            return await execute_intent(intent)

    return await asyncio.gather(
        *[limited_execute(i) for i in sorted_intents]
    )


async def parallel(
    *funcs: Callable[[], Awaitable[Any]],
    concurrency: int = 10,
) -> list[Any]:
    """Execute multiple async functions in parallel.

    Usage:
        results = await parallel(
            lambda: fetch_users(),
            lambda: fetch_orders(),
            lambda: fetch_products(),
        )
    """
    semaphore = asyncio.Semaphore(concurrency)

    async def limited_call(func: Callable) -> Any:
        async with semaphore:
            return await func()

    tasks = [limited_call(func) for func in funcs]
    return await asyncio.gather(*tasks)


def run_in_thread(
    func: Callable[..., Any],
    *args: Any,
    **kwargs: Any,
) -> Any:
    """Run a synchronous function in a thread pool.

    Use for CPU-bound work that would block the event loop.

    Usage:
        result = run_in_thread(cpu_intensive_function, arg1, arg2)
    """
    import functools
    loop = asyncio.get_event_loop()
    return loop.run_in_executor(
        _get_thread_pool(),
        functools.partial(func, *args, **kwargs),
    )


async def run_in_thread_async(
    func: Callable[..., Any],
    *args: Any,
    **kwargs: Any,
) -> Any:
    """Run a synchronous function in a thread pool (async version).

    Usage:
        result = await run_in_thread_async(cpu_intensive_function, arg1)
    """
    import functools
    loop = asyncio.get_event_loop()
    return await loop.run_in_executor(
        _get_thread_pool(),
        functools.partial(func, *args, **kwargs),
    )


# ============================================================
# Priority queue for intents
# ============================================================

@dataclass(order=True)
class PrioritizedIntent:
    """Intent with priority for queue ordering."""

    priority: int
    intent: Intent = field(compare=False)
    metadata: dict[str, Any] = field(default_factory=dict, compare=False)


class IntentQueue:
    """Priority queue for intents.

    Intents are executed based on priority (higher first).
    """

    def __init__(self, max_concurrent: int = 10) -> None:
        self._queue: list[PrioritizedIntent] = []
        self._max_concurrent = max_concurrent
        self._running = 0
        self._semaphore = asyncio.Semaphore(max_concurrent)

    def enqueue(self, intent: Intent, priority: int = 0) -> None:
        """Add intent to queue."""
        item = PrioritizedIntent(priority=priority, intent=intent)
        self._queue.append(item)
        self._queue.sort(reverse=True)  # Higher priority first

    def dequeue(self) -> Intent | None:
        """Remove and return highest priority intent."""
        if self._queue:
            return self._queue.pop(0).intent
        return None

    async def process(self) -> list[Result]:
        """Process all intents in queue with priority ordering."""
        results: list[Result] = []

        async def worker() -> None:
            while True:
                intent = self.dequeue()
                if intent is None:
                    break
                async with self._semaphore:
                    result = await execute_intent(intent)
                    results.append(result)

        # Launch workers concurrently
        workers = [worker() for _ in range(self._max_concurrent)]
        await asyncio.gather(*workers)

        return results

    @property
    def size(self) -> int:
        """Queue size."""
        return len(self._queue)

    @property
    def is_empty(self) -> bool:
        """Check if queue is empty."""
        return len(self._queue) == 0
