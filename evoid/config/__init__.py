"""Config — TOML and Python-native configuration.

Two ways to configure:
1. TOML (evoid.toml) — traditional
2. Python (evoid_config.py) — native, type-safe
"""

from .loader import EvoidConfig, ServiceConfig, RuntimeConfig, EnginesConfig, PipelineConfig, load
from .schema import config, load_config, validate_config

__all__ = [
    "EvoidConfig",
    "ServiceConfig",
    "RuntimeConfig",
    "EnginesConfig",
    "PipelineConfig",
    "load",
    "config",
    "load_config",
    "validate_config",
]
