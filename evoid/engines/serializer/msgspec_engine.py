"""Msgspec Serializer — Example implementation.

IOP: This is an EXAMPLE. Users can implement their own with any library.
"""

from __future__ import annotations

from typing import Any


class MsgspecSerializer:
    """Msgspec-based serializer. Requires: pip install msgspec"""

    def encode(self, data: Any) -> bytes:
        """Encode data using msgspec (fastest Python JSON library)."""
        import msgspec
        return msgspec.json.encode(data)

    def decode(self, data: bytes, schema: type | None = None) -> Any:
        """Decode data using msgspec with optional type validation."""
        import msgspec
        if schema:
            return msgspec.json.decode(data, type=schema)
        return msgspec.json.decode(data)
