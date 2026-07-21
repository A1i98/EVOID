"""Memory Storage Engine — In-memory storage.

IOP: Just a dict wrapper. No class behavior.
"""

from __future__ import annotations

from typing import Any

# Module-level state — simple dict
_store: dict[str, Any] = {}


async def read(key: str) -> Any | None:
    """Read from memory."""
    return _store.get(key)


async def write(key: str, value: Any) -> bool:
    """Write to memory."""
    _store[key] = value
    return True


async def delete(key: str) -> bool:
    """Delete from memory."""
    if key in _store:
        del _store[key]
        return True
    return False


async def health() -> bool:
    """Memory is always healthy."""
    return True


def clear() -> None:
    """Clear all stored data."""
    _store.clear()


def register_handlers() -> None:
    """Register memory storage as Intent handlers."""
    from ...core import register, register_processor
    from ...core.intents import STORAGE_READ, STORAGE_WRITE, STORAGE_DELETE, STORAGE_HEALTH

    async def handle_read(ctx):
        key = ctx.intent.metadata.get("key")
        return await read(key)

    async def handle_write(ctx):
        key = ctx.intent.metadata.get("key")
        value = ctx.intent.metadata.get("value")
        return await write(key, value)

    async def handle_delete(ctx):
        key = ctx.intent.metadata.get("key")
        return await delete(key)

    async def handle_health(ctx):
        return await health()

    register(STORAGE_READ)
    register(STORAGE_WRITE)
    register(STORAGE_DELETE)
    register(STORAGE_HEALTH)
    register_processor("storage.read", handle_read)
    register_processor("storage.write", handle_write)
    register_processor("storage.delete", handle_delete)
    register_processor("storage.health", handle_health)
