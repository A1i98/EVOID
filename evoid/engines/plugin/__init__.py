"""Plugin Engine — Register custom adapters, engines, and languages.

IOP: Plugin system is just a registry (dict) and registration functions.
Users can register:
- Adapters (Telegram, Discord, MQTT, gRPC, etc.)
- Engines (Storage, Cache, Serializer, etc.)
- Languages (Rust, Go, etc.)
- Processors (custom logic)

The runtime doesn't care what you register — it just resolves by name.

Plugin Standard:
- Package name: evoid-* or evoid-plugin-*
- Manifest: evoid_plugin.json
- Entry point: module:function
"""

from .registry import Plugin, register, resolve, list_plugins, has, unregister, clear
from .loader import from_config, from_module, from_file
from .manifest import PluginManifest, load_manifest, validate_manifest, create_manifest
from .discovery import search_plugins, discover_installed, install_plugin, get_plugin_info

__all__ = [
    "Plugin",
    "register",
    "resolve",
    "list_plugins",
    "has",
    "unregister",
    "clear",
    "from_config",
    "from_module",
    "from_file",
    "PluginManifest",
    "load_manifest",
    "validate_manifest",
    "create_manifest",
    "search_plugins",
    "discover_installed",
    "install_plugin",
    "get_plugin_info",
]
