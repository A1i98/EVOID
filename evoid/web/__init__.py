"""Web — Web-specific features for EVOID services.

Primary entry points:
    evoid.native        — IOP mother syntax (adapter-agnostic)
    evoid.web.route     — Function-based routes (@get, @post)
    evoid.web.controller — Class-based controllers (@Controller)
    evoid.web.pipeline  — Web pipeline (auto-detect framework)

Backward-compat aliases:
    from evoid.web import NativeService, create_service  → use evoid.native
    from evoid.web import RouteService, get, post        → use evoid.web.route
    from evoid.web import ControllerService, Controller  → use evoid.web.controller
"""

from ..native import (
    Service as NativeService,
    create_service,
    on,
    execute_service,
    run as run_native,
)
from .route import (
    App as RouteApp,
    Service as RouteService,
    get,
    post,
    put,
    delete,
    before,
    after,
    before_handler,
    after_handler,
    replace_pipeline,
    run as run_route,
)
from .controller import (
    App as ControllerApp,
    Service as ControllerService,
    Controller,
    GET,
    POST,
    PUT,
    DELETE,
    run as run_controller,
)
from ..native.pipeline import (
    WebPipeline,
    detect,
    create_web_pipeline,
)

__all__ = [
    # Native IOP syntax (from evoid.native)
    "NativeService",
    "create_service",
    "on",
    "execute_service",
    "run_native",
    # @route syntax
    "RouteService",
    "RouteApp",
    "get",
    "post",
    "put",
    "delete",
    "before",
    "after",
    "before_handler",
    "after_handler",
    "replace_pipeline",
    "run_route",
    # @controller syntax
    "ControllerService",
    "ControllerApp",
    "Controller",
    "GET",
    "POST",
    "PUT",
    "DELETE",
    "run_controller",
    # Web pipeline
    "WebPipeline",
    "detect",
    "create_web_pipeline",
]
