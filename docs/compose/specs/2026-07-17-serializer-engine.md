# Serializer Engine — Abstraction Layer

> EVOID provides the interface. Users bring their own library.

## [S1] Principle

IOP is about Intent + Pipeline. The intent defines the activity, the pipeline shapes it.
Serialization is HOW you move data in/out — that's the user's choice, not EVOID's.

EVOID provides:
- A Protocol (contract)
- Example implementations (optional)
- Documentation showing how to use any library

EVOID does NOT:
- Force a specific library
- Require a specific pattern
- Add dependencies

## [S2] The Contract

```python
# evoid/contracts/serializer.py

from typing import Any, Protocol

class Serializer(Protocol):
    """Implement this to use your preferred library."""

    def encode(self, data: Any) -> bytes: ...
    def decode(self, data: bytes, schema: type | None = None) -> Any: ...
```

That's it. One interface. Two methods.

## [S3] How Users Use It

### With Pydantic
```python
from pydantic import BaseModel

class PydanticSerializer:
    def encode(self, data):
        if hasattr(data, 'model_dump'):
            return data.model_dump_json().encode()
        import json
        return json.dumps(data).encode()

    def decode(self, data, schema=None):
        if schema and hasattr(schema, 'model_validate'):
            return schema.model_validate_json(data)
        import json
        return json.loads(data)

serializer = PydanticSerializer()
```

### With msgspec
```python
import msgspec

class MsgspecSerializer:
    def encode(self, data):
        return msgspec.json.encode(data)

    def decode(self, data, schema=None):
        if schema:
            return msgspec.json.decode(data, type=schema)
        return msgspec.json.decode(data)

serializer = MsgspecSerializer()
```

### With stdlib json
```python
import json

class StdlibSerializer:
    def encode(self, data):
        return json.dumps(data).encode()

    def decode(self, data, schema=None):
        return json.loads(data)

serializer = StdlibSerializer()
```

## [S4] Registration

Users register their serializer once:

```python
from evoid.engines.serializer import set_serializer

set_serializer(PydanticSerializer())
```

Or per-adapter:

```python
from evoid.web.native.pipeline import WebPipeline

pipeline = WebPipeline(
    service=app,
    serializer=MsgspecSerializer(),  # this adapter uses msgspec
)
```

## [S5] Usage in Adapters

```python
from evoid.engines.serializer import get_serializer

# In adapter
serializer = get_serializer()
body = serializer.encode(result.value)
data = serializer.decode(request_body, schema=MyModel)
```

## [S6] What to Build

1. **Contract** — `evoid/contracts/serializer.py` (already exists, keep as-is)
2. **Registry** — `evoid/engines/serializer/__init__.py` (get_serializer, set_serializer)
3. **Example engines** — optional, for reference:
   - `json_engine.py` (stdlib, default)
   - `pydantic_engine.py` (example)
   - `msgspec_engine.py` (example)
4. **Documentation** — tutorial page showing how to use any library
5. **ASGI adapter** — use serializer engine for encode/decode

## [S7] Files

### Create:
- `evoid/engines/serializer/pydantic_engine.py` (example)
- `evoid/engines/serializer/msgspec_engine.py` (example)
- `docs/docs-astro/src/content/docs/tutorial/serialization.md`

### Modify:
- `evoid/engines/serializer/__init__.py` (add registry)
- `evoid/engines/serializer/json_engine.py` (minor cleanup)
- `evoid/adapters/asgi.py` (use serializer engine)
