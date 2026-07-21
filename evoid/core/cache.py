"""Cache convenience functions — High-level API for cache operations.

IOP: Each function creates an Intent and executes it through the pipeline.
The active handler (selected by config or code) does the actual work.
"""

from __future__ import annotations

from typing import Any

from .intent import Intent, Level
from .runtime import execute
from .extend import replace_pipeline

# Track if pipeline is configured
_pipeline_configured = False


def _ensure_pipeline() -> None:
    """Ensure cache pipeline is configured."""
    global _pipeline_configured
    if _pipeline_configured:
        return

    # Set pipeline to use cache handlers directly
    replace_pipeline("cache.get", ["cache.get"])
    replace_pipeline("cache.set", ["cache.set"])
    replace_pipeline("cache.delete", ["cache.delete"])
    replace_pipeline("cache.exists", ["cache.exists"])
    replace_pipeline("cache.health", ["cache.health"])
    _pipeline_configured = True


async def cache_get(key: str) -> Any | None:
    """Get value from configured cache backend.

    Creates a cache.get Intent and executes it through the pipeline.
    The active cache handler returns the cached value.
    """
    _ensure_pipeline()
    intent = Intent(
        name="cache.get",
        level=Level.EPHEMERAL,
        metadata={"key": key},
    )
    result = await execute(intent)
    return result.value


async def cache_set(key: str, value: Any, ttl: int | None = None) -> bool:
    """Set value in configured cache backend.

    Creates a cache.set Intent and executes it through the pipeline.
    The active cache handler stores the value.
    """
    _ensure_pipeline()
    intent = Intent(
        name="cache.set",
        level=Level.EPHEMERAL,
        metadata={"key": key, "value": value, "ttl": ttl},
    )
    result = await execute(intent)
    return result.value


async def cache_delete(key: str) -> bool:
    """Delete from configured cache backend.

    Creates a cache.delete Intent and executes it through the pipeline.
    The active cache handler removes the key.
    """
    _ensure_pipeline()
    intent = Intent(
        name="cache.delete",
        level=Level.EPHEMERAL,
        metadata={"key": key},
    )
    result = await execute(intent)
    return result.value


async def cache_exists(key: str) -> bool:
    """Check if key exists in configured cache backend.

    Creates a cache.exists Intent and executes it through the pipeline.
    The active cache handler checks existence.
    """
    _ensure_pipeline()
    intent = Intent(
        name="cache.exists",
        level=Level.EPHEMERAL,
        metadata={"key": key},
    )
    result = await execute(intent)
    return result.value


async def cache_health() -> bool:
    """Check cache backend health.

    Creates a cache.health Intent and executes it through the pipeline.
    The active cache handler reports its status.
    """
    _ensure_pipeline()
    intent = Intent(
        name="cache.health",
        level=Level.EPHEMERAL,
    )
    result = await execute(intent)
    return result.value
