"""Tests for all serializer engines — IOP compliance + functionality."""

import pytest
import json
from datetime import datetime, date, time
from decimal import Decimal
from uuid import UUID


# ── JSON Engine Tests ───────────────────────────────────────────────────────

class TestJsonEngine:
    def test_basic_types(self):
        from evoid.engines.serializer.json_engine import encode, decode
        for data in ["hello", 42, 3.14, True, None, [1, 2], {"a": 1}]:
            assert decode(encode(data)) == data

    def test_datetime(self):
        from evoid.engines.serializer.json_engine import encode, decode
        now = datetime.now()
        assert decode(encode({"ts": now}))["ts"] == now.isoformat()

    def test_uuid(self):
        from evoid.engines.serializer.json_engine import encode, decode
        uid = UUID("12345678-1234-5678-1234-567812345678")
        assert decode(encode({"id": uid}))["id"] == str(uid)

    def test_decimal(self):
        from evoid.engines.serializer.json_engine import encode, decode
        assert decode(encode({"amt": Decimal("99.99")}))["amt"] == "99.99"

    def test_nested(self):
        from evoid.engines.serializer.json_engine import encode, decode
        data = {"users": [{"id": 1}, {"id": 2}]}
        assert decode(encode(data)) == data

    def test_adapter_class(self):
        from evoid.engines.serializer.json_engine import JsonSerializer
        s = JsonSerializer()
        assert s.encode("test") == b'"test"'


# ── Msgpack Engine Tests ────────────────────────────────────────────────────

class TestMsgpackEngine:
    def test_basic_types(self):
        from evoid.engines.serializer.msgpack_engine import encode, decode
        for data in ["hello", 42, 3.14, True, None, [1, 2], {"a": 1}]:
            assert decode(encode(data)) == data

    def test_datetime(self):
        from evoid.engines.serializer.msgpack_engine import encode, decode
        now = datetime.now()
        result = decode(encode({"ts": now}))
        assert result["ts"].year == now.year

    def test_uuid(self):
        from evoid.engines.serializer.msgpack_engine import encode, decode
        uid = UUID("12345678-1234-5678-1234-567812345678")
        assert decode(encode({"id": uid}))["id"] == uid

    def test_decimal(self):
        from evoid.engines.serializer.msgpack_engine import encode, decode
        assert decode(encode({"amt": Decimal("99.99")}))["amt"] == Decimal("99.99")

    def test_bytes_native(self):
        from evoid.engines.serializer.msgpack_engine import encode, decode
        assert decode(encode({"bin": b"data"}))["bin"] == b"data"

    def test_set(self):
        from evoid.engines.serializer.msgpack_engine import encode, decode
        result = decode(encode({"tags": {"a", "b"}}))
        assert set(result["tags"]) == {"a", "b"}

    def test_smaller_than_json(self):
        import json
        from evoid.engines.serializer.msgpack_engine import encode as mp_encode
        data = {"items": list(range(100))}
        assert len(mp_encode(data)) < len(json.dumps(data).encode())

    def test_adapter_class(self):
        from evoid.engines.serializer.msgpack_engine import MsgpackSerializer, decode
        s = MsgpackSerializer()
        assert decode(s.encode("test")) == "test"


# ── Msgspec Engine Tests ────────────────────────────────────────────────────

class TestMsgspecEngine:
    def test_basic_types(self):
        pytest.importorskip("msgspec")
        from evoid.engines.serializer.msgspec_engine import encode, decode
        for data in ["hello", 42, 3.14, True, None, [1, 2], {"a": 1}]:
            assert decode(encode(data)) == data

    def test_nested(self):
        pytest.importorskip("msgspec")
        from evoid.engines.serializer.msgspec_engine import encode, decode
        data = {"users": [{"id": 1}, {"id": 2}]}
        assert decode(encode(data)) == data

    def test_adapter_class(self):
        pytest.importorskip("msgspec")
        from evoid.engines.serializer.msgspec_engine import MsgspecSerializer
        s = MsgspecSerializer()
        assert s.decode(s.encode("test")) == "test"


# ── Pydantic Engine Tests ───────────────────────────────────────────────────

class TestPydanticEngine:
    def test_basic_types(self):
        from evoid.engines.serializer.pydantic_engine import encode, decode
        for data in ["hello", 42, 3.14, True, None, [1, 2], {"a": 1}]:
            assert decode(encode(data)) == data

    def test_with_schema(self):
        try:
            from pydantic import BaseModel
            from evoid.engines.serializer.pydantic_engine import encode, decode

            class User(BaseModel):
                id: int
                name: str

            user = User(id=1, name="Ali")
            encoded = encode(user)
            decoded = decode(encoded, schema=User)
            assert decoded.id == 1
            assert decoded.name == "Ali"
        except ImportError:
            pytest.skip("pydantic not installed")

    def test_adapter_class(self):
        from evoid.engines.serializer.pydantic_engine import PydanticSerializer
        s = PydanticSerializer()
        assert s.decode(s.encode("test")) == "test"


# ── Serializer Registry Tests ───────────────────────────────────────────────

class TestSerializerRegistry:
    def test_get_serializer(self):
        from evoid.engines.serializer import get_serializer
        s = get_serializer()
        assert hasattr(s, "encode")
        assert hasattr(s, "decode")

    def test_set_serializer(self):
        from evoid.engines.serializer import set_serializer, get_serializer, reset_serializer

        class Dummy:
            def encode(self, data): return b"dummy"
            def decode(self, data, schema=None): return "dummy"

        set_serializer(Dummy())
        assert get_serializer().encode("test") == b"dummy"
        reset_serializer()

    def test_auto_detect_without_set(self):
        from evoid.engines.serializer import get_serializer, reset_serializer
        reset_serializer()
        s = get_serializer()
        assert s is not None


# ── Cross-Engine Compatibility ──────────────────────────────────────────────

class TestCrossEngine:
    def test_all_engines_handle_same_data(self):
        from evoid.engines.serializer.json_engine import encode as json_encode, decode as json_decode
        from evoid.engines.serializer.msgpack_engine import encode as mp_encode, decode as mp_decode

        data = {"users": [{"id": i, "name": f"user_{i}"} for i in range(10)]}

        json_result = json_decode(json_encode(data))
        mp_result = mp_decode(mp_encode(data))

        assert json_result == mp_result
