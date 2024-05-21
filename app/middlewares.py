import logging
import typing

import fastapi
import starlette.routing
import structlog
from fastapi.middleware.cors import CORSMiddleware
from fastapi.middleware.gzip import GZipMiddleware
from starlette.middleware.base import BaseHTTPMiddleware

from app import exception_handlers
from app.utils import AsyncElapsedTimer

logger = logging.getLogger(__name__)

NextCall = typing.Callable[
    [fastapi.Request], typing.Awaitable[fastapi.responses.StreamingResponse]
]


async def _get_logging_context(request: fastapi.Request) -> dict[str, typing.Any]:
    # add special fields to the json payload
    context: dict[str, typing.Any] = {
        "httpRequest": {
            "requestMethod": request.method,
            "requestUrl": str(request.url),
        },
    }

    return context


def _get_request_path(request: fastapi.Request) -> str | None:
    request_scope = request.scope
    if not request_scope:
        return None

    scope_route = request.scope.get("route")

    if not isinstance(scope_route, starlette.routing.Route):
        return None

    root_path = typing.cast(str, request_scope.get("root_path", ""))
    route_path = scope_route.path

    return root_path + route_path


async def _log_response(
    request: fastapi.Request,
    response: fastapi.responses.StreamingResponse | fastapi.responses.Response,
    latency: str,
) -> fastapi.responses.Response:
    path = _get_request_path(request)

    extra = {
        "status_code": response.status_code,
        "headers": dict(response.headers),
        "requestPath": path or "UNAVAILABLE",
        "requestLatency": latency,
    }
    # There's behaviour that relies on the `extra` structure here, do not drop any keys!
    # extra = {response: dict | None, status_code: int, headers: dict}
    logger.info("api response", extra=extra)
    return response


async def catch_exceptions_middleware(
    request: fastapi.Request, call_next: NextCall
) -> fastapi.Response:
    """
    Middleware that catches all exceptions and returns a JSON response.
    """
    context = await _get_logging_context(request)
    # bind values to the structlog context via contextvars,
    # which have a separate value per asyncio task, i.e. one value per request
    with structlog.contextvars.bound_contextvars(**context):
        async with AsyncElapsedTimer() as elapsed_timer:
            response: fastapi.responses.StreamingResponse | fastapi.responses.Response
            try:
                response = await call_next(request)
            except Exception as ex:  # pylint: disable=broad-exception-caught
                response = await exception_handlers.default_exception_handler(
                    request, ex
                )

        # log responses
        response = await _log_response(
            request=request,
            response=response,
            latency=elapsed_timer.elapsed_formatted,
        )

    return response


def setup_middlewares(app: fastapi.FastAPI) -> None:
    """
    Setup middlewares for fastapi application
    """
    app.add_middleware(
        CORSMiddleware,
        allow_credentials=True,
        allow_origins=["*"],
        allow_methods=["*"],
        allow_headers=["*"],
    )
    app.add_middleware(GZipMiddleware)
    app.add_middleware(BaseHTTPMiddleware, dispatch=catch_exceptions_middleware)
