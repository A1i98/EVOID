"""AsyncAPI Adapter — Generate AsyncAPI 3.0 spec from Intent schemas.

IOP: AsyncAPI spec is pure data. No behavior, no side effects.

Maps:
  Intent name    → Channel
  Intent metadata → Message payload
  Pipeline       → Operation (subscribe/publish)
  Level          → Security level
"""

from __future__ import annotations

from dataclasses import dataclass, field
from typing import Any

from ..core.schema import IntentSchema, export_schemas


@dataclass(frozen=True)
class AsyncAPISpec:
    """AsyncAPI 3.0 specification — pure data."""
    asyncapi: str = "3.0.0"
    info: dict[str, Any] = field(default_factory=dict)
    servers: dict[str, Any] = field(default_factory=dict)
    channels: dict[str, Any] = field(default_factory=dict)
    operations: dict[str, Any] = field(default_factory=dict)
    components: dict[str, Any] = field(default_factory=dict)


def generate_asyncapi(
    title: str = "EVOID API",
    version: str = "1.0.0",
    description: str = "Intent-based API generated from EVOID Intents",
    server_url: str = "http://localhost:8000",
) -> dict[str, Any]:
    """Generate AsyncAPI 3.0 spec from registered Intents.

    Returns a dict that can be serialized to JSON or YAML.
    """
    schemas = export_schemas()

    channels = {}
    operations = {}
    messages = {}

    for name, schema in schemas.items():
        # Channel = Intent name
        channel_name = name.replace(":", ".")
        channels[channel_name] = {
            "address": f"intents/{channel_name}",
            "messages": {
                f"{channel_name}Message": _build_message(schema),
            },
            "description": schema.description,
        }

        # Operation = subscribe (service listens) + publish (client sends)
        operations[f"on_{channel_name}"] = {
            "action": "receive",
            "channel": {"$ref": f"#/channels/{channel_name}"},
            "messages": [
                {"$ref": f"#/channels/{channel_name}/messages/{channel_name}Message"},
            ],
            "description": f"Handle {name} Intent",
        }

        # Message schema
        messages[f"{channel_name}Message"] = _build_message(schema)

    # Components: reusable schemas
    components = {
        "schemas": {
            "IntentLevel": {
                "type": "string",
                "enum": ["ephemeral", "standard", "critical"],
                "description": "Intent protection level",
            },
        },
    }

    return {
        "asyncapi": "3.0.0",
        "info": {
            "title": title,
            "version": version,
            "description": description,
        },
        "servers": {
            "main": {
                "url": server_url,
                "description": "EVOID gateway server",
            },
        },
        "channels": channels,
        "operations": operations,
        "components": components,
    }


def _build_message(schema: IntentSchema) -> dict[str, Any]:
    """Build AsyncAPI message from IntentSchema."""
    properties: dict[str, Any] = {
        "name": {
            "type": "string",
            "const": schema.name,
            "description": "Intent name",
        },
        "level": {
            "$ref": "#/components/schemas/IntentLevel",
        },
    }

    # Add metadata fields
    metadata_props = {}
    for f in schema.metadata_fields:
        prop: dict[str, Any] = {"type": f.type}
        if f.description:
            prop["description"] = f.description
        if f.default is not None:
            prop["default"] = f.default
        metadata_props[f.name] = prop

    if metadata_props:
        properties["metadata"] = {
            "type": "object",
            "properties": metadata_props,
        }

    return {
        "name": schema.name,
        "description": schema.description,
        "payload": {
            "type": "object",
            "properties": properties,
            "required": ["name", "level"],
        },
        "x-evoid": {
            "level": schema.level,
            "pipeline": list(schema.pipeline),
            "timeout": schema.timeout,
        },
    }


def generate_asyncapi_markdown(title: str = "EVOID API", version: str = "1.0.0") -> str:
    """Generate human-readable Markdown documentation from Intent schemas."""
    schemas = export_schemas()

    lines = [
        f"# {title}",
        "",
        f"Version: {version}",
        "",
        "Auto-generated from registered Intents.",
        "",
        "## Intents",
        "",
        "| Name | Level | Pipeline | Description |",
        "|------|-------|----------|-------------|",
    ]

    for name, schema in sorted(schemas.items()):
        pipeline = " → ".join(schema.pipeline) if schema.pipeline else "default"
        lines.append(f"| `{name}` | {schema.level} | {pipeline} | {schema.description} |")

    lines.append("")
    lines.append("## Intent Details")
    lines.append("")

    for name, schema in sorted(schemas.items()):
        lines.append(f"### `{name}`")
        lines.append("")
        lines.append(f"- **Level**: {schema.level}")
        lines.append(f"- **Description**: {schema.description}")
        if schema.pipeline:
            lines.append(f"- **Pipeline**: {' → '.join(schema.pipeline)}")
        if schema.timeout:
            lines.append(f"- **Timeout**: {schema.timeout}s")
        if schema.metadata_fields:
            lines.append("- **Metadata**:")
            for f in schema.metadata_fields:
                desc = f" — {f.description}" if f.description else ""
                lines.append(f"  - `{f.name}` ({f.type}){desc}")
        lines.append("")

    return "\n".join(lines)
