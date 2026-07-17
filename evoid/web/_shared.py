"""Shared utilities for web syntaxes (route, controller)."""

from __future__ import annotations

from ..core.intent import Intent, Level


def create_intent(method: str, path: str, level: str = "standard") -> Intent:
    """Auto-create Intent from method + path."""
    intent_level = Level(level) if level in ("ephemeral", "standard", "critical") else Level.STANDARD

    return Intent(
        name=f"{method.upper()}:{path}",
        level=intent_level,
        metadata={"method": method, "path": path},
    )
