"""Storage convenience functions — High-level API for storage operations.

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
    """Ensure storage pipeline is configured."""
    global _pipeline_configured
    if _pipeline_configured:
        return

    # Set pipeline to use storage handlers directly
    replace_pipeline("storage.read", ["storage.read"])
    replace_pipeline("storage.write", ["storage.write"])
    replace_pipeline("storage.delete", ["storage.delete"])
    replace_pipeline("storage.health", ["storage.health"])
    _pipeline_configured = True


async def storage_read(key: str) -> Any | None:
    """Read from configured storage backend.

    Creates a storage.read Intent and executes it through the pipeline.
    The active storage handler returns the value.
    """
    _ensure_pipeline()
    intent = Intent(
        name="storage.read",
        level=Level.STANDARD,
        metadata={"key": key},
    )
    result = await execute(intent)
    return result.value


async def storage_write(key: str, value: Any) -> bool:
    """Write to configured storage backend.

    Creates a storage.write Intent and executes it through the pipeline.
    The active storage handler persists the value.
    """
    _ensure_pipeline()
    intent = Intent(
        name="storage.write",
        level=Level.STANDARD,
        metadata={"key": key, "value": value},
    )
    result = await execute(intent)
    return result.value


async def storage_delete(key: str) -> bool:
    """Delete from configured storage backend.

    Creates a storage.delete Intent and executes it through the pipeline.
    The active storage handler removes the key.
    """
    _ensure_pipeline()
    intent = Intent(
        name="storage.delete",
        level=Level.STANDARD,
        metadata={"key": key},
    )
    result = await execute(intent)
    return result.value


async def storage_health() -> bool:
    """Check storage backend health.

    Creates a storage.health Intent and executes it through the pipeline.
    The active storage handler reports its status.
    """
    _ensure_pipeline()
    intent = Intent(
        name="storage.health",
        level=Level.EPHEMERAL,
    )
    result = await execute(intent)
    return result.value
