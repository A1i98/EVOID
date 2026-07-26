"""Project Manager — Create and manage projects with multiple services.

IOP: Just data and functions. No classes with behavior.

Project structure:
my-project/
├── pyproject.toml           # Project config (pyproject + [tool.evoid])
├── services/
│   ├── user-service/
│   │   ├── evoid.toml       # Service config
│   │   └── main.py
│   └── payment-service/
│       ├── evoid.toml
│       └── main.py
└── shared/
    └── models.py            # Shared models
"""

from __future__ import annotations

from dataclasses import dataclass, field
from pathlib import Path
from typing import Any

import tomli_w

try:
    import tomli
except ImportError:
    import tomllib as tomli


# ============================================================
# Project root detection
# ============================================================

def find_project_root(start: Path | str = ".") -> Path | None:
    """Find the EVOID project root by walking up from start directory.

    Looks for a directory containing both:
    - services/ subdirectory
    - pyproject.toml with [tool.evoid] section (or at least pyproject.toml)

    Returns the project root Path, or None if not found.
    """
    current = Path(start).resolve()

    while True:
        # Check for services/ directory
        services_dir = current / "services"
        if services_dir.exists() and services_dir.is_dir():
            # Check for pyproject.toml (project marker)
            pyproject = current / "pyproject.toml"
            if pyproject.exists():
                return current

        # Stop if we've reached the filesystem root
        parent = current.parent
        if parent == current:
            break
        current = parent

    return None


# ============================================================
# Data structures
# ============================================================

@dataclass
class ServiceInfo:
    """Service info — pure data."""

    name: str
    path: Path
    port: int = 8000
    adapter: str = "asgi"
    engines: dict[str, str] = field(default_factory=dict)


@dataclass
class ProjectInfo:
    """Project info — pure data."""

    name: str
    path: Path
    services: list[ServiceInfo] = field(default_factory=list)


# ============================================================
# Project functions
# ============================================================

def init_project(name: str, path: str | Path = ".") -> ProjectInfo:
    """Create a new project.

    Creates:
    - <name>/pyproject.toml (project config + [tool.evoid])
    - <name>/services/ (services directory)
    - <name>/shared/ (shared code)
    - <name>/services/gateway/ (default gateway service)
    """
    project_path = Path(path) / name
    project_path.mkdir(parents=True, exist_ok=True)

    # Create directories
    (project_path / "services").mkdir(exist_ok=True)
    (project_path / "shared").mkdir(exist_ok=True)

    # Create pyproject.toml with project metadata + [tool.evoid] config
    config = {
        "project": {
            "name": name,
            "version": "0.1.0",
            "requires-python": ">=3.12",
            "dependencies": ["evoid>=0.5.0"],
        },
        "build-system": {
            "requires": ["hatchling"],
            "build-backend": "hatchling.build",
        },
        "tool": {
            "evoid": {
                "adapter": "asgi",
                "host": "0.0.0.0",
                "engines": {
                    "schema": "native",
                    "storage": "memory",
                    "cache": "memory",
                    "logger": "loguru",
                },
            },
        },
    }

    config_path = project_path / "pyproject.toml"
    with open(config_path, "wb") as f:
        tomli_w.dump(config, f)

    # Create shared models
    shared_init = '''"""Shared models for all services."""

# Add shared Pydantic models here
'''
    (project_path / "shared" / "__init__.py").write_text(shared_init)

    # Create default gateway service
    add_service(project_path, "gateway", port=8000)

    return ProjectInfo(
        name=name,
        path=project_path,
        services=[ServiceInfo(name="gateway", path=project_path / "services" / "gateway", port=8000)],
    )


def _next_port(project: Path) -> int:
    """Find the next available port (8000, 8001, 8002, ...)."""
    used = set()
    services_dir = project / "services"
    if services_dir.exists():
        for d in services_dir.iterdir():
            if d.is_dir():
                cfg = d / "evoid.toml"
                if cfg.exists():
                    try:
                        with open(cfg, "rb") as f:
                            data = tomli.load(f)
                        used.add(data.get("runtime", {}).get("port", 8000))
                    except Exception:
                        pass
    port = 8000
    while port in used:
        port += 1
    return port


def add_service(
    project_path: str | Path,
    service_name: str,
    port: int | None = None,
) -> ServiceInfo:
    """Add a new service to a project.

    Creates:
    - services/<service_name>/evoid.toml
    - services/<service_name>/main.py

    If port is None, auto-increments from existing services.
    """
    project = Path(project_path)
    if port is None:
        port = _next_port(project)
    service_path = project / "services" / service_name
    service_path.mkdir(parents=True, exist_ok=True)

    # Load project config for engine defaults
    project_config = _load_project_config(project)

    # Create service config
    config = {
        "service": {
            "name": service_name,
            "version": "0.1.0",
        },
        "runtime": {
            "adapter": project_config.get("runtime", {}).get("adapter", "asgi"),
            "host": "0.0.0.0",
            "port": port,
        },
        "engines": project_config.get("engines", {}),
        "pipeline": {
            "processors": ["validate"],
        },
    }

    config_path = service_path / "evoid.toml"
    with open(config_path, "wb") as f:
        tomli_w.dump(config, f)

    # Create service main.py
    if service_name == "gateway":
        main_py = f'''"""Gateway — entry point for all external requests.

Routes HTTP requests to services via the message bus.
Customize: add routes, middleware, auth checks here.
"""

import json
from evoid.web.route import Service, get, post, run
from evoid.engines.logger import loguru as log
from evoid.adapters.mcp import create_mcp_server, handle_mcp_request
from evoid.adapters.asyncapi import generate_asyncapi, generate_asyncapi_markdown
from evoid.core.annotations import body


app = Service("gateway")


@get("/health")
async def health() -> dict:
    return {{"status": "healthy"}}


@get("/")
async def index() -> dict:
    return {{"service": "gateway", "status": "running"}}


@get("/docs")
async def docs() -> str:
    """AsyncAPI documentation as Markdown."""
    return generate_asyncapi_markdown(title="{service_name}")


@get("/docs/openapi")
async def docs_openapi() -> dict:
    """AsyncAPI spec as JSON."""
    return generate_asyncapi(title="{service_name}")


# MCP server — created once, reused across requests
_mcp_server = create_mcp_server("{service_name}")


@post("/mcp")
@body()
async def mcp_endpoint(body: dict) -> dict:
    """MCP JSON-RPC endpoint for AI agents."""
    return await handle_mcp_request(_mcp_server, body)


if __name__ == "__main__":
    log.init("gateway")
    run(app, port={port})
'''
    else:
        main_py = f'''"""Service: {service_name}"""

from evoid.web.route import Service, get, post, run
from evoid.engines.logger import loguru as log


app = Service("{service_name}")


@get("/health")
async def health() -> dict:
    return {{"status": "healthy"}}


if __name__ == "__main__":
    log.init("{service_name}")
    run(app, port={port})
'''
    (service_path / "main.py").write_text(main_py)

    return ServiceInfo(
        name=service_name,
        path=service_path,
        port=port,
    )


def list_services(project_path: str | Path) -> list[ServiceInfo]:
    """List all services in a project.

    If project_path doesn't contain a services/ directory, attempts to
    find the project root by walking up the directory tree.
    """
    project = Path(project_path)
    services_dir = project / "services"

    if not services_dir.exists():
        # Try to find project root by walking up
        project_root = find_project_root(project)
        if project_root:
            project = project_root
            services_dir = project / "services"
        else:
            return []

    services = []
    for service_dir in services_dir.iterdir():
        if service_dir.is_dir():
            config_path = service_dir / "evoid.toml"
            if config_path.exists():
                config = _load_service_config(config_path)
                services.append(ServiceInfo(
                    name=config.get("service", {}).get("name", service_dir.name),
                    path=service_dir,
                    port=config.get("runtime", {}).get("port", 8000),
                    adapter=config.get("runtime", {}).get("adapter", "asgi"),
                    engines=config.get("engines", {}),
                ))

    return services


def get_project_config(project_path: str | Path) -> dict[str, Any]:
    """Get project configuration."""
    return _load_project_config(Path(project_path))


# ============================================================
# Helpers
# ============================================================

def _load_project_config(project_path: Path) -> dict[str, Any]:
    """Load project config from pyproject.toml [tool.evoid] section."""
    config_path = project_path / "pyproject.toml"
    if not config_path.exists():
        return {}

    with open(config_path, "rb") as f:
        data = tomli.load(f)

    return data.get("tool", {}).get("evoid", {})


def _load_service_config(config_path: Path) -> dict[str, Any]:
    """Load service config from evoid.toml."""
    with open(config_path, "rb") as f:
        return tomli.load(f)
