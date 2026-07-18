"""Tests for plugin system and config."""

import pytest
from evoid.engines.plugin.manifest import (
    PluginManifest, load_manifest, validate_manifest, create_manifest,
)
from evoid.engines.plugin.registry import register, resolve, list_plugins, clear, has, unregister
from evoid.config import config, validate_config, EvoidConfig


class TestManifest:
    def test_create_manifest(self):
        data = create_manifest(
            name="evoid-redis",
            version="1.0.0",
            type="engine",
            description="Redis cache",
            entry_point="evoid_redis:register_plugin",
        )
        assert data["name"] == "evoid-redis"
        assert data["type"] == "engine"

    def test_validate_valid(self):
        manifest = PluginManifest(
            name="evoid-redis",
            version="1.0.0",
            type="engine",
            entry_point="evoid_redis:register",
        )
        errors = validate_manifest(manifest)
        assert errors == []

    def test_validate_no_name(self):
        manifest = PluginManifest(name="", version="1.0.0", type="engine")
        errors = validate_manifest(manifest)
        assert any("name is required" in e for e in errors)

    def test_validate_bad_prefix(self):
        manifest = PluginManifest(name="my-plugin", version="1.0.0", type="engine")
        errors = validate_manifest(manifest)
        assert any("evoid" in e for e in errors)

    def test_validate_bad_type(self):
        manifest = PluginManifest(name="evoid-x", version="1.0.0", type="invalid")
        errors = validate_manifest(manifest)
        assert any("type must be" in e for e in errors)

    def test_validate_bad_entry_point(self):
        manifest = PluginManifest(
            name="evoid-x", version="1.0.0", type="engine",
            entry_point="no_colon",
        )
        errors = validate_manifest(manifest)
        assert any("entry_point" in e for e in errors)


class TestRegistry:
    def setup_method(self):
        clear()

    def test_register_and_resolve(self):
        register("test_plugin", "engine", lambda: None, version="1.0.0")
        assert has("test_plugin")
        assert resolve("test_plugin") is not None

    def test_list_plugins(self):
        register("a", "engine", lambda: None)
        register("b", "adapter", lambda: None)
        plugins = list_plugins()
        assert len(plugins) == 2

    def test_unregister(self):
        register("to_remove", "engine", lambda: None)
        assert has("to_remove")
        unregister("to_remove")
        assert not has("to_remove")


class TestConfig:
    def test_python_config(self):
        cfg = config(
            service={"name": "test", "version": "2.0.0"},
            runtime={"adapter": "asgi", "port": 9000},
            engines={"storage": "redis"},
        )
        assert cfg.service.name == "test"
        assert cfg.runtime.port == 9000
        assert cfg.engines.storage == "redis"

    def test_config_defaults(self):
        cfg = config()
        assert cfg.service.name == "evoid-service"
        assert cfg.runtime.adapter == "asgi"
        assert cfg.runtime.port == 8000

    def test_validate_valid(self):
        cfg = config()
        errors = validate_config(cfg)
        assert errors == []

    def test_validate_bad_port(self):
        cfg = config(runtime={"port": 99999})
        errors = validate_config(cfg)
        assert any("port" in e for e in errors)

    def test_validate_bad_adapter(self):
        cfg = config(runtime={"adapter": "invalid"})
        errors = validate_config(cfg)
        assert any("adapter" in e for e in errors)
