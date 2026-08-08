"""Tests for Intent definitions, validation, config, and built-in memory handlers."""



class TestIntents:
    """Test standard Intent definitions."""

    def test_storage_intents_exist(self):
        from evoid.core.intents import (
            STORAGE_DELETE,
            STORAGE_HEALTH,
            STORAGE_READ,
            STORAGE_WRITE,
        )
        assert STORAGE_READ.name == "storage.read"
        assert STORAGE_WRITE.name == "storage.write"
        assert STORAGE_DELETE.name == "storage.delete"
        assert STORAGE_HEALTH.name == "storage.health"

    def test_cache_intents_exist(self):
        from evoid.core.intents import (
            CACHE_DELETE,
            CACHE_EXISTS,
            CACHE_GET,
            CACHE_HEALTH,
            CACHE_SET,
        )
        assert CACHE_GET.name == "cache.get"
        assert CACHE_SET.name == "cache.set"
        assert CACHE_DELETE.name == "cache.delete"
        assert CACHE_EXISTS.name == "cache.exists"
        assert CACHE_HEALTH.name == "cache.health"

    def test_all_intent_names_are_dotted(self):
        import inspect

        from evoid.core import intents
        for name, obj in inspect.getmembers(intents):
            if hasattr(obj, 'name') and isinstance(obj.name, str):
                assert '.' in obj.name, f"{name} should use dotted notation"


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
