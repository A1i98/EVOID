"""Plugin Manifest — Standard format for EVOID plugins on PyPI.

Every EVOID plugin must have an `evoid_plugin.json` manifest.
This enables discovery, installation, and validation.

Manifest format:
{
    "name": "evoid-redis",
    "version": "1.0.0",
    "type": "engine",
    "description": "Redis cache engine for EVOID",
    "author": "Your Name",
    "entry_point": "evoid_redis:register_plugin",
    "dependencies": ["redis>=4.0.0"],
    "evoid_version": ">=0.4.0",
    "tags": ["cache", "redis"]
}
"""

from __future__ import annotations

import json
from dataclasses import dataclass, field
from pathlib import Path
from typing import Any


MANIFEST_FILE = "evoid_plugin.json"


@dataclass(frozen=True)
class PluginManifest:
    """Plugin manifest — pure data."""

    name: str
    version: str
    type: str  # "adapter", "engine", "language", "processor"
    description: str = ""
    author: str = ""
    entry_point: str = ""  # module:function
    dependencies: tuple[str, ...] = ()
    evoid_version: str = ">=0.4.0"
    tags: tuple[str, ...] = ()
    metadata: dict[str, Any] = field(default_factory=dict)


def load_manifest(package_path: str | Path) -> PluginManifest | None:
    """Load manifest from a package directory."""
    path = Path(package_path) / MANIFEST_FILE

    if not path.exists():
        # Try inside evoid_plugin/ subdirectory
        path = Path(package_path) / "evoid_plugin" / MANIFEST_FILE
        if not path.exists():
            return None

    try:
        with open(path) as f:
            data = json.load(f)
        return _parse_manifest(data)
    except (json.JSONDecodeError, KeyError):
        return None


def load_manifest_from_module(module_path: str) -> PluginManifest | None:
    """Load manifest by importing a module that exposes it."""
    import importlib

    try:
        module = importlib.import_module(module_path)
        if hasattr(module, "MANIFEST"):
            return _parse_manifest(module.MANIFEST)
        if hasattr(module, "plugin_manifest"):
            return _parse_manifest(module.plugin_manifest)
    except ImportError:
        pass

    return None


def create_manifest(
    name: str,
    version: str,
    type: str,
    description: str = "",
    author: str = "",
    entry_point: str = "",
    dependencies: tuple[str, ...] = (),
    evoid_version: str = ">=0.4.0",
    tags: tuple[str, ...] = (),
) -> dict[str, Any]:
    """Create a manifest dict for writing to evoid_plugin.json."""
    return {
        "name": name,
        "version": version,
        "type": type,
        "description": description,
        "author": author,
        "entry_point": entry_point,
        "dependencies": list(dependencies),
        "evoid_version": evoid_version,
        "tags": list(tags),
    }


def write_manifest(data: dict[str, Any], path: str | Path) -> None:
    """Write manifest to evoid_plugin.json."""
    path = Path(path) / MANIFEST_FILE
    with open(path, "w") as f:
        json.dump(data, f, indent=2)


def validate_manifest(manifest: PluginManifest) -> list[str]:
    """Validate a manifest. Returns list of errors (empty = valid)."""
    errors = []

    if not manifest.name:
        errors.append("name is required")
    elif not manifest.name.startswith("evoid"):
        errors.append(f"name should start with 'evoid' (got '{manifest.name}')")

    if not manifest.version:
        errors.append("version is required")

    if manifest.type not in ("adapter", "engine", "language", "processor"):
        errors.append(f"type must be adapter/engine/language/processor (got '{manifest.type}')")

    if manifest.entry_point and ":" not in manifest.entry_point:
        errors.append(f"entry_point must be 'module:function' format (got '{manifest.entry_point}')")

    return errors


def _parse_manifest(data: dict[str, Any]) -> PluginManifest:
    """Parse raw dict into PluginManifest."""
    deps = data.get("dependencies", [])
    tags = data.get("tags", [])

    return PluginManifest(
        name=data["name"],
        version=data["version"],
        type=data["type"],
        description=data.get("description", ""),
        author=data.get("author", ""),
        entry_point=data.get("entry_point", ""),
        dependencies=tuple(deps) if isinstance(deps, list) else tuple(deps),
        evoid_version=data.get("evoid_version", ">=0.4.0"),
        tags=tuple(tags) if isinstance(tags, list) else tuple(tags),
        metadata=data.get("metadata", {}),
    )
