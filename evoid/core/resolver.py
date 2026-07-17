"""Resolver — Pure functions. Maps Intent to pipeline configuration.

IOP Principle: Processors are independent Lego blocks.
The resolver is just a function that maps data to data.
"""

from __future__ import annotations

from dataclasses import dataclass, field
from typing import Any

from .intent import Intent, Level


@dataclass(frozen=True)
class PipelineConfig:
    """Pipeline configuration — pure data.

    Attributes:
        processors: Ordered processor names
        priority: Execution priority
        timeout: Maximum execution time
        metadata: Extra config for processors
    """

    processors: tuple[str, ...] = ()
    priority: int = 0
    timeout: float | None = None
    metadata: dict[str, Any] = field(default_factory=dict)


# Default processor chains per intent level
_DEFAULT_PROCESSORS: dict[Level, tuple[str, ...]] = {
    Level.EPHEMERAL: ("validate",),
    Level.STANDARD: ("validate", "authorize"),
    Level.CRITICAL: ("validate", "authorize", "audit", "protect"),
}

# Default timeouts per intent level
_DEFAULT_TIMEOUTS: dict[Level, float] = {
    Level.EPHEMERAL: 5.0,
    Level.STANDARD: 10.0,
    Level.CRITICAL: 30.0,
}

# Cached default configs per level — avoids repeated dataclass creation
_DEFAULT_CONFIGS: dict[Level, PipelineConfig] = {
    level: PipelineConfig(processors=procs, timeout=_DEFAULT_TIMEOUTS[level])
    for level, procs in _DEFAULT_PROCESSORS.items()
}


def resolve_pipeline(intent: Intent) -> PipelineConfig:
    """Map an Intent to a PipelineConfig.

    This is a pure function: data in → data out.
    No classes, no state, no side effects.
    """
    level = intent.level

    # Fast path — no custom metadata, use cached default
    if not intent.metadata:
        cached = _DEFAULT_CONFIGS.get(level)
        if cached and intent.priority == 0:
            return cached

    processors = intent.metadata.get("processors", _DEFAULT_PROCESSORS.get(level, ()))
    timeout = intent.metadata.get("timeout", _DEFAULT_TIMEOUTS.get(level, 10.0))

    return PipelineConfig(
        processors=tuple(processors),
        priority=intent.priority,
        timeout=timeout,
        metadata=intent.metadata,
    )
