"""Engine Handler Registry — Maps engine categories to Intent handlers.

IOP: Each engine category (storage, cache, etc.) has active handlers.
Config or code selects which handler is active.

Features borrowed from best plugin systems:
- Plugin discovery via entry points (pluggy/stevedore)
- Lazy activation — load only when first Intent called (VS Code)
- Conflict detection — detect duplicate handlers (pluggy)
- Profile support — different configs per environment (Spring)
"""

from __future__ import annotations

import importlib
from typing import Any, Callable


# Global state
_handlers: dict[str, str] = {}         # "storage" -> "storage.read" intent name
_configs: dict[str, dict] = {}         # "storage.read" -> {"db_path": "..."}
_lazy_handlers: dict[str, str] = {}    # "storage" -> "module:register_handlers"
_loaded: set[str] = set()              # Track which categories are loaded
_profiles: dict[str, dict[str, Any]] = {}  # "production" -> {engine configs}
_active_profile: str = "default"


# ============================================================
# Core handler management
# ============================================================

def set_handler(category: str, intent_name: str, config: dict[str, Any] | None = None) -> None:
    """Register which handler handles this engine category.

    Args:
        category: Engine category (storage, cache, schema, etc.)
        intent_name: Intent name that handles this category (e.g. "storage.read")
        config: Optional config dict for this handler
    """
    # Conflict detection
    if category in _handlers and _handlers[category] != intent_name:
        existing = _handlers[category]
        raise ValueError(
            f"Conflict: handler already registered for '{category}': {existing}. "
            f"Cannot register {intent_name}. Use clear_handler() first."
        )

    _handlers[category] = intent_name
    _loaded.add(category)
    if config:
        _configs[intent_name] = config


def get_handler(category: str) -> str | None:
    """Get the active handler intent name for a category."""
    return _handlers.get(category)


def get_config(intent_name: str) -> dict[str, Any]:
    """Get config for a specific handler."""
    return _configs.get(intent_name, {})


def get_all_handlers() -> dict[str, str]:
    """Get all registered handler mappings."""
    return dict(_handlers)


def clear_handler(category: str) -> None:
    """Clear a specific handler registration."""
    _handlers.pop(category, None)
    _loaded.discard(category)


def clear_handlers() -> None:
    """Clear all handler registrations (for testing)."""
    _handlers.clear()
    _configs.clear()
    _loaded.clear()


# ============================================================
# Lazy activation (from VS Code/stevedore)
# ============================================================

def register_lazy_handler(category: str, handler_path: str) -> None:
    """Register a handler to be loaded lazily.

    The handler module is only imported when the category is first accessed.
    This saves startup time for plugins that aren't immediately needed.

    Args:
        category: Engine category (storage, cache, etc.)
        handler_path: Module:function path (e.g. "evoid_sqlite:register_handlers")
    """
    _lazy_handlers[category] = handler_path


def ensure_loaded(category: str) -> None:
    """Ensure a category's handler is loaded.

    If registered lazily, imports the module and calls register_handlers().
    If already loaded, does nothing.
    """
    if category in _loaded:
        return

    if category in _lazy_handlers:
        _load_handler(category)
    elif category in _handlers:
        _loaded.add(category)


def _load_handler(category: str) -> None:
    """Import and call a lazy handler's registration function."""
    if category not in _lazy_handlers:
        return

    handler_path = _lazy_handlers[category]
    mod_path, func_name = handler_path.split(":", 1)

    try:
        mod = importlib.import_module(mod_path)
        func = getattr(mod, func_name)
        func()
        _loaded.add(category)
    except ImportError:
        # Plugin not installed — skip silently
        pass
    except Exception as e:
        raise RuntimeError(f"Failed to load handler for '{category}': {e}")


# ============================================================
# Plugin discovery via entry points (from pluggy/stevedore)
# ============================================================

def discover_plugins() -> dict[str, str]:
    """Discover installed EVOID plugins via entry points.

    Looks for 'evoid_plugins' entry point group in pyproject.toml.
    Returns dict mapping plugin names to their register_handlers paths.

    Usage in plugin's pyproject.toml:
        [project.entry-points.evoid_plugins]
        redis = "evoid_redis:register_handlers"
    """
    discovered: dict[str, str] = {}

    try:
        from importlib.metadata import entry_points
        eps = entry_points(group="evoid_plugins")
        for ep in eps:
            discovered[ep.name] = ep.value
    except Exception:
        pass

    return discovered


def auto_discover_and_register() -> None:
    """Auto-discover plugins and register them as lazy handlers.

    Call this at startup to find all installed EVOID plugins.
    They won't be loaded until their category is first accessed.
    """
    plugins = discover_plugins()
    for name, handler_path in plugins.items():
        if name not in _lazy_handlers:
            register_lazy_handler(name, handler_path)


# ============================================================
# Profile system (from Spring)
# ============================================================

def set_profile(name: str, config: dict[str, Any]) -> None:
    """Define a configuration profile.

    Profiles allow different engine configurations for different environments.

    Args:
        name: Profile name (e.g. "production", "development", "testing")
        config: Engine configuration for this profile

    Example:
        set_profile("production", {
            "storage": {"engine": "postgresql", "url": "postgresql://prod/db"},
            "cache": {"engine": "redis", "url": "redis://prod:6379"},
        })
    """
    _profiles[name] = config


def activate_profile(name: str) -> None:
    """Activate a configuration profile.

    Applies the profile's engine configurations.
    """
    global _active_profile

    if name not in _profiles:
        raise ValueError(f"Profile '{name}' not found. Available: {list(_profiles.keys())}")

    _active_profile = name
    profile_config = _profiles[name]

    # Apply engine configs from profile
    for category, engine_config in profile_config.items():
        if isinstance(engine_config, dict) and "engine" in engine_config:
            engine_name = engine_config["engine"]
            options = {k: v for k, v in engine_config.items() if k != "engine"}
            _configs[f"{category}.{engine_name}"] = options


def get_active_profile() -> str:
    """Get the currently active profile name."""
    return _active_profile


def get_profile_config(category: str) -> dict[str, Any]:
    """Get the config for a category in the active profile."""
    if _active_profile not in _profiles:
        return {}
    return _profiles[_active_profile].get(category, {})


def list_profiles() -> list[str]:
    """List all defined profile names."""
    return list(_profiles.keys())


# ============================================================
# Entry point: discover + register all plugins
# ============================================================

def init_plugin_system() -> None:
    """Initialize the plugin system.

    Call once at application startup:
        from evoid.engines.handler import init_plugin_system
        init_plugin_system()

    This will:
    1. Auto-discover installed plugins via entry points
    2. Register them as lazy handlers
    3. They load on-demand when their category is first used
    """
    auto_discover_and_register()
