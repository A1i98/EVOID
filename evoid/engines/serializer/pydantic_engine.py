"""Pydantic Serializer — Example implementation.

IOP: This is an EXAMPLE. Users can implement their own with any library.
"""

from __future__ import annotations

import json
from typing import Any


class PydanticSerializer:
    """Pydantic-based serializer. Requires: pip install pydantic"""

    def encode(self, data: Any) -> bytes:
        """Encode data using Pydantic's serialization."""
        if hasattr(data, "model_dump_json"):
            return data.model_dump_json().encode("utf-8")
        if hasattr(data, "model_dump"):
            return json.dumps(data.model_dump(), default=str).encode("utf-8")
        return json.dumps(data, default=str).encode("utf-8")

    def decode(self, data: bytes, schema: type | None = None) -> Any:
        """Decode data using Pydantic's validation."""
        if schema and hasattr(schema, "model_validate_json"):
            return schema.model_validate_json(data)
        if schema and hasattr(schema, "model_validate"):
            parsed = json.loads(data)
            return schema.model_validate(parsed)
        return json.loads(data)
