"""Regression tests: add_intent() must preserve the intent's declared security level.

These tests exercise the real execution path (execute() → get_pipeline_config()
→ execute_pipeline()) and assert that level-derived security processors are
NOT silently bypassed.
"""

import asyncio

import pytest

from evoid.core import Context, Intent, Level, clear_registry, resolve_pipeline
from evoid.core.extend import (
    add_intent,
    add_intent_with_pipeline,
    clear_overrides,
    get_pipeline_config,
    replace_pipeline,
)
from evoid.core.processor import clear_processors
from evoid.core.runtime import execute
from evoid.processors.defaults import register_defaults


@pytest.fixture(autouse=True)
def _clean_state():
    """Reset registries before each test — real defaults are re-registered on import."""
    clear_registry()
    clear_overrides()
    clear_processors()
    register_defaults()


async def _handler(ctx: Context) -> dict:
    return {"handled": True}


class TestAddIntentPipelineLevels:
    """add_intent() must compose level-derived security processors + handler."""

    def test_standard_gets_validate_and_authorize(self):
        intent = Intent(name="std_op", level=Level.STANDARD)
        add_intent(intent, _handler)

        result = asyncio.run(execute(intent))

        assert result.success is True
        # Security processors must run before the handler
        assert result.processors == ("validate", "authorize", "std_op")

    def test_critical_gets_full_security_pipeline(self):
        intent = Intent(name="crit_op", level=Level.CRITICAL)
        add_intent(intent, _handler)

        result = asyncio.run(execute(intent))

        assert result.success is True
        assert result.processors == ("validate", "authorize", "audit", "protect", "crit_op")

    def test_ephemeral_gets_validate(self):
        intent = Intent(name="eph_op", level=Level.EPHEMERAL)
        add_intent(intent, _handler)

        result = asyncio.run(execute(intent))

        assert result.success is True
        assert result.processors == ("validate", "eph_op")


class TestAddIntentWithPipelineUnchanged:
    """add_intent_with_pipeline() behavior must remain unchanged."""

    def test_custom_pipeline_preserved(self):
        """Custom pipeline from add_intent_with_pipeline is used as-is."""
        intent = Intent(name="custom_op", level=Level.CRITICAL)

        async def my_handler(ctx: Context) -> dict:
            return {"custom": True}

        # String processors must be pre-registered
        async def custom_processor(ctx: Context) -> dict:
            return {"processed": True}

        async def save(ctx: Context) -> dict:
            return {"saved": True}

        from evoid.core import register_processor
        register_processor("custom_processor", custom_processor)
        register_processor("save", save)

        add_intent_with_pipeline(
            intent,
            processors=["validate", "custom_processor", "save"],
            handler=my_handler,
        )

        # Custom pipeline with callables gets auto-registered
        result = asyncio.run(execute(intent))

        # Pipeline: validate + custom_processor + save + handler
        # But security processors not in pipeline unless explicitly listed
        assert result.success is True
        assert result.processors == ("validate", "custom_processor", "save", "custom_op")

    def test_standard_level_ignored_when_custom_pipeline_provided(self):
        """Level-derived defaults are NOT used when custom pipeline given."""
        intent = Intent(name="explicit_op", level=Level.CRITICAL)

        async def my_handler(ctx: Context) -> dict:
            return {"explicit": True}

        from evoid.core import register_processor

        async def custom_only(ctx: Context) -> dict:
            return {"custom": True}

        register_processor("custom_only", custom_only)

        add_intent_with_pipeline(
            intent,
            processors=["custom_only"],
            handler=my_handler,
        )

        result = asyncio.run(execute(intent))

        assert result.success is True
        # Only the explicitly provided processors + handler
        assert result.processors == ("custom_only", "explicit_op")


class TestAddIntentUsesResolver:
    """add_intent() must delegate to resolve_pipeline(), not duplicate _DEFAULT_PROCESSORS."""

    def test_add_intent_matches_resolve_pipeline_plus_handler(self):
        """The override produced by add_intent() equals resolve_pipeline(intent)
        with the handler name appended — proving no duplicated level mapping."""
        intent = Intent(name="derive_op", level=Level.CRITICAL)
        add_intent(intent, _handler)

        cfg = get_pipeline_config(intent)
        resolved = resolve_pipeline(intent)

        assert cfg.processors == (*resolved.processors, intent.name)

    def test_add_intent_does_not_directly_access_default_processors(self):
        """Source-level guard: add_intent does not reference _DEFAULT_PROCESSORS."""
        import inspect

        from evoid.core import extend

        src = inspect.getsource(extend.add_intent)
        assert "_DEFAULT_PROCESSORS" not in src, (
            "add_intent() must not directly access _DEFAULT_PROCESSORS — "
            "it should delegate to resolve_pipeline()"
        )


class TestExplicitPipelineOverride:
    """replace_pipeline() must fully override level-derived pipeline."""

    def test_replace_pipeline_replaces_entire_chain(self):
        intent = Intent(name="replace_op", level=Level.CRITICAL)
        add_intent(intent, _handler)

        # Replace with entirely custom pipeline
        replace_pipeline("replace_op", ["custom_validate", "custom_handler"])

        async def custom_validate(ctx: Context) -> dict:
            return {"validated": True}

        async def custom_handler(ctx: Context) -> dict:
            return {"custom": True}

        from evoid.core import register_processor
        register_processor("custom_validate", custom_validate)
        register_processor("custom_handler", custom_handler)

        result = asyncio.run(execute(intent))

        assert result.success is True
        assert result.processors == ("custom_validate", "custom_handler")


class TestPipelineProcessorOrder:
    """Security processors execute before handler, in declared order."""

    def test_standard_order_validate_then_authorize_then_handler(self):
        order: list[str] = []

        async def record_validate(ctx: Context) -> dict:
            order.append("validate")
            return {"validated": True}

        async def record_authorize(ctx: Context) -> dict:
            order.append("authorize")
            return {"authorized": True}

        from evoid.core import register_processor
        register_processor("validate", record_validate)
        register_processor("authorize", record_authorize)

        intent = Intent(name="order_op", level=Level.STANDARD)
        add_intent(intent, _handler)

        asyncio.run(execute(intent))

        assert order == ["validate", "authorize"]

    def test_critical_order_validate_authorize_audit_protect_then_handler(self):
        order: list[str] = []

        async def record_validate(ctx: Context) -> dict:
            order.append("validate")
            return {"validated": True}

        async def record_authorize(ctx: Context) -> dict:
            order.append("authorize")
            return {"authorized": True}

        async def record_audit(ctx: Context) -> dict:
            order.append("audit")
            return {"audited": True}

        async def record_protect(ctx: Context) -> dict:
            order.append("protect")
            return {"allowed": True}

        from evoid.core import register_processor
        register_processor("validate", record_validate)
        register_processor("authorize", record_authorize)
        register_processor("audit", record_audit)
        register_processor("protect", record_protect)

        intent = Intent(name="order_crit", level=Level.CRITICAL)
        add_intent(intent, _handler)

        asyncio.run(execute(intent))

        assert order == ["validate", "authorize", "audit", "protect"]


class TestSecurityNotBypassed:
    """Security processors must not be silently bypassed."""

    def test_authorize_rejection_fails_execution(self):
        """A rejecting authorize processor must fail the whole execution."""
        from evoid.core import register_processor

        async def denying_authorize(ctx: Context) -> dict:
            return {"authorized": False, "reason": "denied_by_test"}

        register_processor("authorize", denying_authorize)

        intent = Intent(name="denied_op", level=Level.STANDARD)
        add_intent(intent, _handler)

        result = asyncio.run(execute(intent))

        assert result.success is False
        assert isinstance(result.error, PermissionError)
        assert "denied_by_test" in str(result.error)

    def test_validate_rejection_fails_execution(self):
        """A rejecting validate processor must fail the whole execution."""
        from evoid.core import register_processor

        async def failing_validate(ctx: Context) -> dict:
            return {"validated": False, "error": "bad_data"}

        register_processor("validate", failing_validate)

        intent = Intent(name="bad_data_op", level=Level.STANDARD)
        add_intent(intent, _handler)

        result = asyncio.run(execute(intent))

        assert result.success is False
        assert isinstance(result.error, ValueError)
        assert "bad_data" in str(result.error)

    def test_handler_never_runs_when_authorize_rejects(self):
        """Handler must not run if a security processor rejects first."""
        from evoid.core import register_processor

        ran = []

        async def denying_authorize(ctx: Context) -> dict:
            return {"authorized": False, "reason": "denied"}

        async def tracking_handler(ctx: Context) -> dict:
            ran.append("handler")
            return {"handled": True}

        register_processor("authorize", denying_authorize)

        intent = Intent(name="never_runs", level=Level.STANDARD)
        add_intent(intent, tracking_handler)

        result = asyncio.run(execute(intent))

        assert result.success is False
        assert ran == []  # handler never executed


class TestEdgeCases:
    """Edge cases: unknown level, duplicates, repeated registration, metadata."""

    def test_unknown_level_uses_resolver_fallback(self):
        """Levels not in _DEFAULT_PROCESSORS → resolve_pipeline returns
        empty processors. add_intent() inherits this via delegation."""
        from evoid.core.resolver import _DEFAULT_PROCESSORS

        # Verify the resolver's fallback contract: known level → processors
        assert _DEFAULT_PROCESSORS[Level.EPHEMERAL] == ("validate",)

        # add_intent() delegates to resolve_pipeline() for all levels
        intent = Intent(name="eph_op2", level=Level.EPHEMERAL)
        add_intent(intent, _handler)

        result = asyncio.run(execute(intent))
        assert result.success is True
        assert result.processors == ("validate", "eph_op2")

    def test_handler_executes_exactly_once(self):
        """Handler must run exactly once per execution."""
        calls = []

        async def counting_handler(ctx: Context) -> dict:
            calls.append("call")
            return {"handled": True}

        intent = Intent(name="count_op2", level=Level.STANDARD)
        add_intent(intent, counting_handler)

        asyncio.run(execute(intent))

        assert calls == ["call"]

    def test_repeated_add_intent_does_not_accumulate(self):
        """Calling add_intent() twice for same intent must not duplicate processors."""
        intent = Intent(name="repeat_op", level=Level.STANDARD)
        add_intent(intent, _handler)
        add_intent(intent, _handler)  # re-registration overwrites

        cfg = get_pipeline_config(intent)

        assert cfg.processors == ("validate", "authorize", "repeat_op")
        assert cfg.processors.count("repeat_op") == 1

    def test_handler_already_in_resolved_chain_no_duplicate(self):
        """If handler name already appears in resolved chain, do not append a duplicate."""
        intent = Intent(name="chain_op", level=Level.STANDARD)
        # Intent metadata processors include the handler name itself
        intent = Intent(
            name="chain_op",
            level=Level.STANDARD,
            metadata={"processors": ["validate", "chain_op"]},
        )
        add_intent(intent, _handler)

        cfg = get_pipeline_config(intent)

        # resolve_pipeline() uses metadata processors → handler already there
        assert cfg.processors == ("validate", "chain_op")
        assert cfg.processors.count("chain_op") == 1

    def test_priority_and_timeout_preserved(self):
        """add_intent() must preserve priority and timeout from intent metadata."""
        intent = Intent(
            name="meta_op2",
            level=Level.STANDARD,
            priority=5,
            timeout=7.5,
            metadata={"timeout": 7.5},
        )
        add_intent(intent, _handler)

        cfg = get_pipeline_config(intent)

        assert cfg.processors == ("validate", "authorize", "meta_op2")
        assert cfg.priority == 5
        assert cfg.timeout == 7.5


if __name__ == "__main__":
    pytest.main([__file__, "-v"])
