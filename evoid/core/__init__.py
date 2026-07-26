"""EVOID Core — IOP Runtime. Pure functions, pure data.

No classes with behavior. No inheritance. No stateful objects.
Just data carrying intent, and functions composing pipelines.
"""

# Convenience functions (Intent-based engine access)
from . import cache, intents, storage
from .annotations import apply_annotations, body, headers, params, rate_limit, requires, validate_annotations, validates

# Annotations
from .annotations import intent as intent_decorator
from .context import Context, fork

# Events
from .events import Event, EventContext, emit, emit_sync, hook_count
from .events import off as off_event
from .events import on as on_event
from .intent import Intent, Level, all_intents, clear_registry, register, resolve
from .message_bus import Message, get_history, publish, subscribe, unsubscribe
from .pipeline import Result
from .pipeline import execute as execute_pipeline
from .processor import Processor, all_processors
from .processor import get as get_processor
from .processor import register as register_processor
from .resolver import PipelineConfig, resolve_pipeline
from .runtime import Config, execute, execute_by_name

# Schema Export
from .schema import (
    FieldSchema,
    IntentSchema,
    export_json_schema,
    export_json_schemas,
    export_schema_for,
    export_schemas,
)
from .service import Service

__all__ = [
    # Intent
    "Intent",
    "Level",
    "register",
    "resolve",
    "all_intents",
    "clear_registry",
    # Resolver
    "PipelineConfig",
    "resolve_pipeline",
    # Pipeline
    "Result",
    "execute_pipeline",
    # Context
    "Context",
    "fork",
    # Processor
    "Processor",
    "register_processor",
    "get_processor",
    "all_processors",
    # Runtime
    "Config",
    "execute",
    "execute_by_name",
    # Message Bus
    "Message",
    "subscribe",
    "unsubscribe",
    "publish",
    "get_history",
    # Service
    "Service",
    # Events
    "Event",
    "EventContext",
    "on_event",
    "off_event",
    "emit",
    "emit_sync",
    "hook_count",
    # Schema Export
    "IntentSchema",
    "FieldSchema",
    "export_schemas",
    "export_schema_for",
    "export_json_schemas",
    "export_json_schema",
    # Annotations
    "intent_decorator",
    "requires",
    "validates",
    "rate_limit",
    "body",
    "params",
    "headers",
    "apply_annotations",
    "validate_annotations",
    # Convenience (Intent-based engine access)
    "intents",
    "storage",
    "cache",
]
