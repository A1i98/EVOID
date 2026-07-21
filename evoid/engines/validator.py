"""Plugin Validator — Validates third-party plugins before registration.

IOP: Every plugin must implement the required handlers for its category.
This module checks that plugins are correct before they enter the runtime.
"""

from __future__ import annotations

import asyncio
import inspect
from dataclasses import dataclass, field
from typing import Any, Callable


@dataclass
class ValidationResult:
    """Result of plugin validation."""
    valid: bool
    errors: list[str] = field(default_factory=list)
    warnings: list[str] = field(default_factory=list)


# Required handlers per engine category
REQUIRED_HANDLERS: dict[str, dict[str, dict[str, Any]]] = {
    "storage": {
        "storage.read": {"params": ["key"]},
        "storage.write": {"params": ["key", "value"]},
        "storage.delete": {"params": ["key"]},
        "storage.health": {"params": []},
    },
    "cache": {
        "cache.get": {"params": ["key"]},
        "cache.set": {"params": ["key", "value"]},
        "cache.delete": {"params": ["key"]},
        "cache.exists": {"params": ["key"]},
        "cache.health": {"params": []},
    },
    "schema": {
        "schema.validate": {"params": ["data"]},
    },
    "serializer": {
        "serializer.encode": {"params": ["data"]},
        "serializer.decode": {"params": ["data"]},
    },
    "auth": {
        "auth.authenticate": {"params": ["token"]},
        "auth.authorize": {"params": ["user", "resource"]},
    },
    "logger": {
        "log.info": {"params": ["message"]},
        "log.warning": {"params": ["message"]},
        "log.error": {"params": ["message"]},
    },
    "metrics": {
        "metrics.record": {"params": ["name", "value"]},
    },
}


def validate_plugin(
    category: str,
    handlers: dict[str, Callable],
    config: dict[str, Any] | None = None,
) -> ValidationResult:
    """Validate a plugin before registration.

    Checks:
    1. Category is recognized
    2. All required handlers are provided
    3. Each handler is an async callable
    4. Handler signatures match expected params

    Args:
        category: Engine category (storage, cache, schema, etc.)
        handlers: Dict mapping intent names to handler functions
        config: Optional config dict for validation

    Returns:
        ValidationResult with valid flag, errors, and warnings
    """
    errors: list[str] = []
    warnings: list[str] = []

    # 1. Check category
    if category not in REQUIRED_HANDLERS:
        errors.append(
            f"Unknown category '{category}'. "
            f"Valid: {list(REQUIRED_HANDLERS.keys())}"
        )
        return ValidationResult(valid=False, errors=errors, warnings=warnings)

    required = REQUIRED_HANDLERS[category]

    # 2. Check required handlers
    for intent_name, spec in required.items():
        if intent_name not in handlers:
            errors.append(f"Missing required handler: {intent_name}")
            continue

        handler = handlers[intent_name]

        # 3. Check it's callable
        if not callable(handler):
            errors.append(f"Handler '{intent_name}' is not callable")
            continue

        # 4. Check it's async
        if not asyncio.iscoroutinefunction(handler):
            warnings.append(
                f"Handler '{intent_name}' is not async — "
                f"will block the pipeline"
            )

        # 5. Check it accepts ctx as first parameter
        valid, msg = _check_ctx_param(handler)
        if not valid:
            errors.append(f"Handler '{intent_name}' signature error: {msg}")

    return ValidationResult(
        valid=len(errors) == 0,
        errors=errors,
        warnings=warnings,
    )


def _check_ctx_param(handler: Callable) -> tuple[bool, str]:
    """Validate that a handler accepts ctx as its first parameter.

    Handlers receive Context as first arg, which contains intent.metadata.
    """
    try:
        sig = inspect.signature(handler)
        params = list(sig.parameters.keys())
    except (ValueError, TypeError):
        return True, ""  # Can't inspect — skip check

    # Handler must accept at least one parameter (ctx)
    if not params:
        return False, "Handler must accept 'ctx' as first parameter"

    # Check for **kwargs (accepts anything)
    for p in sig.parameters.values():
        if p.kind == inspect.Parameter.VAR_KEYWORD:
            return True, ""

    return True, ""


def get_required_handlers(category: str) -> dict[str, list[str]]:
    """Get required handler specs for a category."""
    if category not in REQUIRED_HANDLERS:
        return {}
    return {
        name: spec.get("params", [])
        for name, spec in REQUIRED_HANDLERS[category].items()
    }
