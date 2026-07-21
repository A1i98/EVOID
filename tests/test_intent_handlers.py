"""Tests for Intent Handler system — storage, cache, validation."""

import pytest


class TestIntents:
    """Test standard Intent definitions."""

    def test_storage_intents_exist(self):
        from evoid.core.intents import (
            STORAGE_READ, STORAGE_WRITE, STORAGE_DELETE, STORAGE_HEALTH,
        )
        assert STORAGE_READ.name == "storage.read"
        assert STORAGE_WRITE.name == "storage.write"
        assert STORAGE_DELETE.name == "storage.delete"
        assert STORAGE_HEALTH.name == "storage.health"

    def test_cache_intents_exist(self):
        from evoid.core.intents import (
            CACHE_GET, CACHE_SET, CACHE_DELETE, CACHE_EXISTS, CACHE_HEALTH,
        )
        assert CACHE_GET.name == "cache.get"
        assert CACHE_SET.name == "cache.set"
        assert CACHE_DELETE.name == "cache.delete"
        assert CACHE_EXISTS.name == "cache.exists"
        assert CACHE_HEALTH.name == "cache.health"

    def test_all_intent_names_are_dotted(self):
        from evoid.core import intents
        import inspect
        for name, obj in inspect.getmembers(intents):
            if hasattr(obj, 'name') and isinstance(obj.name, str):
                assert '.' in obj.name, f"{name} should use dotted notation"


class TestHandlerRegistry:
    """Test handler registry operations."""

    def test_set_and_get_handler(self):
        from evoid.engines.handler import set_handler, get_handler, clear_handlers
        clear_handlers()
        set_handler("storage", "storage.read", {"db_path": "test.db"})
        assert get_handler("storage") == "storage.read"
        clear_handlers()

    def test_get_config(self):
        from evoid.engines.handler import set_handler, get_config, clear_handlers
        clear_handlers()
        set_handler("cache", "cache.get", {"url": "redis://localhost"})
        config = get_config("cache.get")
        assert config["url"] == "redis://localhost"
        clear_handlers()

    def test_get_all_handlers(self):
        from evoid.engines.handler import set_handler, get_all_handlers, clear_handlers
        clear_handlers()
        set_handler("storage", "storage.read")
        set_handler("cache", "cache.get")
        handlers = get_all_handlers()
        assert "storage" in handlers
        assert "cache" in handlers
        clear_handlers()


class TestValidator:
    """Test plugin validation."""

    def test_valid_storage_plugin(self):
        from evoid.engines.validator import validate_plugin

        async def read(ctx): return None
        async def write(ctx): return True
        async def delete(ctx): return True
        async def health(ctx): return True

        handlers = {
            "storage.read": read,
            "storage.write": write,
            "storage.delete": delete,
            "storage.health": health,
        }
        result = validate_plugin("storage", handlers)
        assert result.valid is True
        assert len(result.errors) == 0

    def test_missing_handler_fails(self):
        from evoid.engines.validator import validate_plugin

        async def read(ctx): return None
        handlers = {"storage.read": read}

        result = validate_plugin("storage", handlers)
        assert result.valid is False
        assert len(result.errors) > 0
        assert "Missing required handler" in result.errors[0]

    def test_unknown_category_fails(self):
        from evoid.engines.validator import validate_plugin
        result = validate_plugin("nonexistent", {})
        assert result.valid is False

    def test_non_async_handler_warns(self):
        from evoid.engines.validator import validate_plugin

        def sync_handler(ctx): return None
        handlers = {
            "storage.read": sync_handler,
            "storage.write": sync_handler,
            "storage.delete": sync_handler,
            "storage.health": sync_handler,
        }
        result = validate_plugin("storage", handlers)
        assert result.valid is True  # Warnings only
        assert len(result.warnings) > 0

    def test_valid_cache_plugin(self):
        from evoid.engines.validator import validate_plugin

        async def get(ctx): return None
        async def set(ctx): return True
        async def delete(ctx): return True
        async def exists(ctx): return False
        async def health(ctx): return True

        handlers = {
            "cache.get": get,
            "cache.set": set,
            "cache.delete": delete,
            "cache.exists": exists,
            "cache.health": health,
        }
        result = validate_plugin("cache", handlers)
        assert result.valid is True


class TestConfigOptions:
    """Test config options support."""

    def test_toml_options_parsed(self):
        from evoid.config.loader import _parse_config
        data = {
            "engines": {
                "storage": "sqlite",
                "cache": "redis",
                "sqlite": {"db_path": "test.db"},
                "redis": {"url": "redis://localhost:6379"},
            }
        }
        config = _parse_config(data)
        assert config.engines.storage == "sqlite"
        assert config.engines.cache == "redis"
        assert config.engines.options["sqlite"]["db_path"] == "test.db"
        assert config.engines.options["redis"]["url"] == "redis://localhost:6379"

    def test_python_config_options(self):
        from evoid.config.schema import config
        app = config(
            engines={
                "storage": "sqlite",
                "options": {
                    "sqlite": {"db_path": "my.db"},
                },
            }
        )
        assert app.engines.storage == "sqlite"
        assert app.engines.options["sqlite"]["db_path"] == "my.db"


class TestConflictDetection:
    """Test conflict detection when registering handlers."""

    def test_conflict_raises_error(self):
        from evoid.engines.handler import set_handler, clear_handlers
        clear_handlers()
        set_handler("storage", "storage.read")
        with pytest.raises(ValueError, match="Conflict"):
            set_handler("storage", "storage.write")
        clear_handlers()

    def test_same_handler_no_conflict(self):
        from evoid.engines.handler import set_handler, clear_handlers
        clear_handlers()
        set_handler("storage", "storage.read")
        set_handler("storage", "storage.read")  # Same handler — no conflict
        clear_handlers()


class TestLazyLoading:
    """Test lazy handler loading."""

    def test_register_lazy_handler(self):
        from evoid.engines.handler import register_lazy_handler, _lazy_handlers, clear_handlers
        clear_handlers()
        register_lazy_handler("test_category", "some.module:register_handlers")
        assert "test_category" in _lazy_handlers
        clear_handlers()

    def test_ensure_loaded_skips_if_not_registered(self):
        from evoid.engines.handler import ensure_loaded, _loaded
        # Should not raise for unknown category
        ensure_loaded("nonexistent_category")


class TestProfileSystem:
    """Test profile-based configuration."""

    def test_set_and_activate_profile(self):
        from evoid.engines.handler import (
            set_profile, activate_profile, get_active_profile,
            list_profiles, clear_handlers,
        )
        clear_handlers()
        set_profile("production", {
            "storage": {"engine": "postgresql", "url": "postgresql://prod/db"},
        })
        assert "production" in list_profiles()
        activate_profile("production")
        assert get_active_profile() == "production"
        clear_handlers()

    def test_activate_nonexistent_profile_raises(self):
        from evoid.engines.handler import activate_profile, clear_handlers
        clear_handlers()
        with pytest.raises(ValueError, match="not found"):
            activate_profile("nonexistent")
        clear_handlers()


class TestMemoryHandlers:
    """Test built-in memory storage/cache handler registration."""

    def test_memory_storage_register(self):
        from evoid.engines.storage.memory import register_handlers
        register_handlers()
        # Should not raise

    def test_memory_cache_register(self):
        from evoid.engines.cache.memory import register_handlers
        register_handlers()
        # Should not raise
