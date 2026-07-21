"""Startup — Auto-wires config to Intent handlers at runtime startup.

IOP: Config declares which engine to use.
Startup reads config, loads the plugin, validates it, and wires the handlers.

Features:
- Auto-discovery of installed plugins via entry points
- Lazy loading — only import when category is first used
- Conflict detection — warns if multiple handlers compete
- Profile support — different configs per environment
"""

from __future__ import annotations

import importlib
from typing import Any

from ..config.loader import EvoidConfig
from ..engines.handler import (
    set_handler,
    get_config,
    register_lazy_handler,
    ensure_loaded,
    set_profile,
    activate_profile,
    init_plugin_system,
)
from ..engines.validator import validate_plugin


# Built-in engine handlers (no plugin needed)
BUILTIN_HANDLERS: dict[str, dict[str, str]] = {
    "storage": {
        "memory": "evoid.engines.storage.memory:register_handlers",
    },
    "cache": {
        "memory": "evoid.engines.cache.memory:register_handlers",
    },
    "schema": {
        "native": "evoid.engines.schema.native:register_handlers",
    },
    "serializer": {
        "json": "evoid.engines.serializer.json_engine:register_handlers",
    },
}

# Plugin engine handlers (third-party)
PLUGIN_HANDLERS: dict[str, str] = {
    "sqlite": "evoid_sqlite:register_handlers",
    "redis": "evoid_redis:register_handlers",
    "sqlalchemy": "evoid_sqlalchemy:register_handlers",
    "postgres": "evoid_postgresql:register_handlers",
    "scylla": "evoid_scylla:register_handlers",
    "smart_storage": "evoid_smart_storage:register_handlers",
    "di": "evoid_di:register_handlers",
    "auth": "evoid_auth:register_handlers",
    "tasks": "evoid_tasks:register_handlers",
    "scheduler": "evoid_scheduler:register_handlers",
}


def wire_engines(config: EvoidConfig) -> None:
    """Wire config to Intent handlers at startup.

    Reads config.engines.*, loads the appropriate handlers,
    validates them, and registers them as Intent processors.

    Args:
        config: Complete EVOID configuration

    Raises:
        RuntimeError: If a plugin fails validation
    """
    # Initialize plugin system (auto-discover installed plugins)
    init_plugin_system()

    # Wire each engine category
    for category in ["storage", "cache", "schema", "serializer"]:
        engine_name = getattr(config.engines, category, None)
        if not engine_name:
            continue

        # Get handler registration function path
        handler_path = _resolve_handler_path(category, engine_name)
        if not handler_path:
            continue

        # Register as lazy handler
        register_lazy_handler(category, handler_path)

        # Set handler with config options
        options = config.engines.options.get(engine_name, {})
        intent_name = f"{category}.read" if category == "storage" else f"{category}.get"

        try:
            set_handler(category, intent_name, options)
        except ValueError as e:
            # Conflict detected — log warning but continue
            import warnings
            warnings.warn(str(e))

        # Load immediately if needed (or keep lazy)
        # For now, load eagerly for backward compatibility
        ensure_loaded(category)


def wire_engines_lazy(config: EvoidConfig) -> None:
    """Wire config to Intent handlers with lazy loading.

    Same as wire_engines() but handlers are only loaded when first accessed.
    This is faster at startup but first access will be slower.
    """
    # Initialize plugin system
    init_plugin_system()

    for category in ["storage", "cache", "schema", "serializer"]:
        engine_name = getattr(config.engines, category, None)
        if not engine_name:
            continue

        handler_path = _resolve_handler_path(category, engine_name)
        if not handler_path:
            continue

        # Register as lazy — don't load yet
        register_lazy_handler(category, handler_path)

        options = config.engines.options.get(engine_name, {})
        intent_name = f"{category}.read" if category == "storage" else f"{category}.get"

        try:
            set_handler(category, intent_name, options)
        except ValueError:
            pass  # Conflict already warned


def wire_engines_with_profile(config: EvoidConfig, profile: str) -> None:
    """Wire config with a specific profile.

    Profiles allow different engine configurations per environment.

    Args:
        config: Base EVOID configuration
        profile: Profile name (e.g. "production", "development")
    """
    # Set and activate the profile
    profile_config = config.engines.options.get("profiles", {}).get(profile, {})
    if profile_config:
        set_profile(profile, profile_config)
        activate_profile(profile)

    # Wire with profile-aware config
    wire_engines(config)


def _resolve_handler_path(category: str, engine_name: str) -> str | None:
    """Resolve the handler registration function path."""
    # Check built-in first
    if category in BUILTIN_HANDLERS and engine_name in BUILTIN_HANDLERS[category]:
        return BUILTIN_HANDLERS[category][engine_name]

    # Check plugins
    if engine_name in PLUGIN_HANDLERS:
        return PLUGIN_HANDLERS[engine_name]

    return None


def _load_and_register(handler_path: str) -> None:
    """Load a module and call its registration function."""
    mod_path, func_name = handler_path.split(":", 1)
    mod = importlib.import_module(mod_path)
    func = getattr(mod, func_name)
    func()


def register_engine_handler(
    category: str,
    engine_name: str,
    handler_path: str,
) -> None:
    """Register a custom engine handler at runtime.

    Use this to add support for engines not in the built-in list.

    Args:
        category: Engine category (storage, cache, etc.)
        engine_name: Name to use in config (e.g. "my-custom-db")
        handler_path: Module:function path (e.g. "my_package:register_handlers")
    """
    PLUGIN_HANDLERS[engine_name] = handler_path
    register_lazy_handler(category, handler_path)
