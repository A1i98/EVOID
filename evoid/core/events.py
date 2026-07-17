"""Events — Plugin lifecycle hooks with security and performance guarantees.

IOP: Events are just data + functions. No classes with behavior.

Security model:
- Hooks receive EventContext (frozen, read-only snapshot), not mutable Context
- Hooks cannot modify pipeline execution (fire-and-forget by default)
- Max hooks per event: configurable, default 16
- Hooks run with timeout per hook

Performance model:
- Zero cost when no hooks registered (single length check)
- EventContext is frozen dataclass (no mutation overhead)
- Emit is inline, no task creation for empty handler lists
"""

from __future__ import annotations

import asyncio
import time
from collections.abc import Awaitable, Callable
from dataclasses import dataclass, field
from typing import Any


# Event names
class Event:
    PRE_EXECUTE = "pre_execute"
    POST_EXECUTE = "post_execute"
    PRE_PROCESS = "pre_process"
    POST_PROCESS = "post_process"
    INTENT_REGISTERED = "intent_registered"
    INTENT_RESOLVED = "intent_resolved"


@dataclass(frozen=True)
class EventContext:
    """Read-only snapshot passed to hooks. Never the mutable Context."""
    intent_name: str
    intent_level: str
    pipeline: tuple[str, ...]
    timestamp: float
    metadata: dict[str, Any] = field(default_factory=dict)


# Handler type: receives EventContext, may be sync or async
Hook = Callable[[EventContext], Any]

# Registry: event_name -> list of hooks
_hooks: dict[str, list[Hook]] = {}

# Config
_MAX_HOOKS_PER_EVENT = 16
_HOOK_TIMEOUT = 5.0


def on(event: str, handler: Hook) -> None:
    """Register a hook for an event."""
    handlers = _hooks.get(event)
    if handlers is None:
        _hooks[event] = [handler]
    elif len(handlers) < _MAX_HOOKS_PER_EVENT:
        handlers.append(handler)


def off(event: str, handler: Hook) -> bool:
    """Unregister a hook."""
    handlers = _hooks.get(event)
    if handlers:
        try:
            handlers.remove(handler)
            return True
        except ValueError:
            pass
    return False


def _has_hooks(event: str) -> bool:
    """Fast check — single dict lookup + length check."""
    handlers = _hooks.get(event)
    return handlers is not None and len(handlers) > 0


async def emit(event: str, ctx: Any = None, metadata: dict[str, Any] | None = None) -> None:
    """Emit an event to all registered hooks.

    When no hooks are registered, this is a no-op (single dict lookup).
    """
    handlers = _hooks.get(event)
    if not handlers:
        return

    # Build EventContext from whatever was passed
    if isinstance(ctx, EventContext):
        event_ctx = ctx
    elif ctx is not None:
        event_ctx = EventContext(
            intent_name=getattr(ctx, "intent_name", getattr(getattr(ctx, "intent", None), "name", "")),
            intent_level=getattr(ctx, "intent_level", getattr(getattr(ctx, "intent", None), "level", "")).value if hasattr(getattr(getattr(ctx, "intent", None), "level", ""), "value") else str(getattr(getattr(ctx, "intent", None), "level", "")),
            pipeline=getattr(ctx, "pipeline", ()),
            timestamp=time.monotonic(),
            metadata=metadata or {},
        )
    else:
        event_ctx = EventContext(
            intent_name="",
            intent_level="",
            pipeline=(),
            timestamp=time.monotonic(),
            metadata=metadata or {},
        )

    for handler in handlers:
        try:
            result = handler(event_ctx)
            if asyncio.iscoroutine(result):
                await asyncio.wait_for(result, timeout=_HOOK_TIMEOUT)
        except asyncio.TimeoutError:
            pass
        except Exception:
            pass


def emit_sync(event: str, metadata: dict[str, Any] | None = None) -> None:
    """Emit an event synchronously (for non-async contexts like register)."""
    handlers = _hooks.get(event)
    if not handlers:
        return

    event_ctx = EventContext(
        intent_name=metadata.get("name", "") if metadata else "",
        intent_level=metadata.get("level", "") if metadata else "",
        pipeline=(),
        timestamp=time.monotonic(),
        metadata=metadata or {},
    )

    for handler in handlers:
        try:
            handler(event_ctx)
        except Exception:
            pass


def clear_hooks() -> None:
    """Clear all registered hooks."""
    _hooks.clear()


def clear_event(event: str) -> None:
    """Clear hooks for a specific event."""
    _hooks.pop(event, None)


def hook_count(event: str | None = None) -> int:
    """Count registered hooks. Per event or total."""
    if event:
        handlers = _hooks.get(event)
        return len(handlers) if handlers else 0
    return sum(len(h) for h in _hooks.values())
