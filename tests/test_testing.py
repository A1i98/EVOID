"""Tests for the testing system."""

import asyncio
import pytest
from evoid import Intent, Level, Context, register, register_processor, clear_registry
from evoid.testing import tc, TestCase, check_result
from evoid.core.pipeline import Result


class TestTestCase:
    def test_create_test_case(self):
        intent = Intent(name="test_intent", level=Level.STANDARD)
        case = tc(intent, expect={"ok": True})
        assert case.name == "test_intent"
        assert case.expect == {"ok": True}
        assert case.intent == intent

    def test_create_with_tags(self):
        intent = Intent(name="tagged", level=Level.STANDARD)
        case = tc(intent, tags=("fast", "unit"))
        assert case.tags == ("fast", "unit")

    def test_create_with_custom_name(self):
        intent = Intent(name="intent_name", level=Level.STANDARD)
        case = tc(intent, name="custom_name")
        assert case.name == "custom_name"


class TestCheckResult:
    def test_success(self):
        result = Result(success=True, value={"ok": True})
        case = TestCase(name="t", intent=Intent(name="x", level=Level.STANDARD), expect={"ok": True})
        assert check_result(result, case) is True

    def test_failure(self):
        result = Result(success=True, value={"ok": False})
        case = TestCase(name="t", intent=Intent(name="x", level=Level.STANDARD), expect={"ok": True})
        assert check_result(result, case) is False

    def test_expected_error(self):
        result = Result(success=False, error=ValueError("bad"))
        case = TestCase(name="t", intent=Intent(name="x", level=Level.STANDARD), expect_error=ValueError)
        assert check_result(result, case) is True

    def test_wrong_error_type(self):
        result = Result(success=False, error=ValueError("bad"))
        case = TestCase(name="t", intent=Intent(name="x", level=Level.STANDARD), expect_error=TypeError)
        assert check_result(result, case) is False

    def test_no_expectations(self):
        result = Result(success=True, value=None)
        case = TestCase(name="t", intent=Intent(name="x", level=Level.STANDARD))
        assert check_result(result, case) is True


class TestIntegration:
    def setup_method(self):
        clear_registry()

    def test_end_to_end(self):
        from evoid.core.extend import add_intent_with_pipeline

        intent = Intent(name="e2e_test", level=Level.EPHEMERAL)

        async def handler(ctx: Context) -> dict:
            return {"status": "ok"}

        add_intent_with_pipeline(intent, processors=["e2e_test"], handler=handler)

        case = tc(intent, expect={"status": "ok"})

        # Simulate what the plugin does
        from evoid.core.runtime import execute
        result = asyncio.run(execute(case.intent))

        assert result.success is True
        assert check_result(result, case) is True
