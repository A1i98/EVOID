"""Schema Export — Machine-readable Intent descriptions for AI agents and plugins.

IOP: Schema export is pure data. No behavior, no side effects.

Exports Intent definitions as JSON Schema-compatible structures so AI agents
can discover, understand, and invoke Intents programmatically.
"""

from __future__ import annotations

from dataclasses import dataclass, field
from typing import Any

from .intent import Intent, Level, all_intents
from .extend import get_pipeline_config
from .resolver import resolve_pipeline


@dataclass(frozen=True)
class FieldSchema:
    """Description of a single metadata field."""
    name: str
    type: str
    required: bool = True
    default: Any = None
    description: str = ""


@dataclass(frozen=True)
class IntentSchema:
    """Machine-readable description of an Intent."""
    name: str
    level: str
    description: str
    metadata_fields: tuple[FieldSchema, ...] = ()
    return_schema: dict[str, Any] = field(default_factory=dict)
    pipeline: tuple[str, ...] = ()
    timeout: float | None = None
    priority: int = 0


def export_schemas() -> dict[str, IntentSchema]:
    """Export all registered Intents as schemas."""
    result = {}
    for name, intent in all_intents().items():
        schema = export_schema_for(intent)
        if schema:
            result[name] = schema
    return result


def export_schema_for(intent: Intent) -> IntentSchema:
    """Generate schema for a single Intent."""
    # Get pipeline config
    try:
        config = get_pipeline_config(intent)
    except Exception:
        config = resolve_pipeline(intent)

    # Extract metadata fields
    fields = _extract_fields(intent)

    # Build description
    description = intent.metadata.get("description", f"Intent: {intent.name}")

    return IntentSchema(
        name=intent.name,
        level=intent.level.value,
        description=description,
        metadata_fields=tuple(fields),
        return_schema=_infer_return_schema(intent),
        pipeline=config.processors,
        timeout=config.timeout or intent.timeout,
        priority=intent.priority,
    )


def export_json_schemas() -> dict[str, dict[str, Any]]:
    """Export all Intents as JSON Schema compatible dicts."""
    schemas = export_schemas()
    return {name: _to_json_schema(schema) for name, schema in schemas.items()}


def export_json_schema(intent_name: str) -> dict[str, Any] | None:
    """Export a single Intent as JSON Schema dict."""
    schemas = export_schemas()
    schema = schemas.get(intent_name)
    if schema:
        return _to_json_schema(schema)
    return None


def _extract_fields(intent: Intent) -> list[FieldSchema]:
    """Extract FieldSchema from Intent metadata."""
    fields = []
    meta = intent.metadata

    # Skip internal metadata keys
    _internal = {"method", "path", "description", "processors", "examples", "mcp_visible"}

    for key, value in meta.items():
        if key in _internal:
            continue
        fields.append(FieldSchema(
            name=key,
            type=_infer_type(value),
            required=value is not None,
            default=value if value is not None else None,
            description=meta.get(f"{key}_description", ""),
        ))

    return fields


def _infer_type(value: Any) -> str:
    """Infer JSON Schema type from Python value."""
    if value is None:
        return "null"
    if isinstance(value, bool):
        return "boolean"
    if isinstance(value, int):
        return "integer"
    if isinstance(value, float):
        return "number"
    if isinstance(value, str):
        return "string"
    if isinstance(value, list):
        return "array"
    if isinstance(value, dict):
        return "object"
    return "string"


def _infer_return_schema(intent: Intent) -> dict[str, Any]:
    """Infer return type schema from Intent metadata."""
    if "return_schema" in intent.metadata:
        return intent.metadata["return_schema"]
    return {"type": "object"}


def _to_json_schema(schema: IntentSchema) -> dict[str, Any]:
    """Convert IntentSchema to JSON Schema dict."""
    properties = {}
    required = []

    for field in schema.metadata_fields:
        prop: dict[str, Any] = {"type": field.type}
        if field.description:
            prop["description"] = field.description
        if field.default is not None:
            prop["default"] = field.default
        properties[field.name] = prop
        if field.required:
            required.append(field.name)

    return {
        "type": "object",
        "title": schema.name,
        "description": schema.description,
        "properties": {
            "name": {"type": "string", "const": schema.name},
            "level": {"type": "string", "enum": ["ephemeral", "standard", "critical"]},
            "metadata": {
                "type": "object",
                "properties": properties,
                "required": required if required else [],
            },
        },
        "required": ["name", "level"],
        "_evoid": {
            "pipeline": list(schema.pipeline),
            "timeout": schema.timeout,
            "priority": schema.priority,
        },
    }
