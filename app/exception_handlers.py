import logging

import fastapi
from fastapi import status
from fastapi.encoders import jsonable_encoder
from fastapi.exceptions import HTTPException, RequestValidationError
from fastapi.responses import JSONResponse, Response

logger = logging.getLogger(__name__)


async def default_exception_handler(
    _: fastapi.Request,
    exc: Exception | fastapi.exceptions.HTTPException,
) -> Response:
    """
    Generic http exception handler.
    """
    status_code = status.HTTP_500_INTERNAL_SERVER_ERROR
    headers = None
    message = "Internal server error"
    if isinstance(exc, fastapi.exceptions.HTTPException):
        status_code = exc.status_code
        headers = exc.headers
        message = str(exc.detail)
    else:
        logger.exception(exc, exc_info=True)

    return JSONResponse(
        status_code=status_code,
        content=jsonable_encoder({"message": message, "status_code": status_code}),
        headers=headers,
    )


def override_exception_handlers(app: fastapi.FastAPI) -> None:
    """
    Override exception default exception handlers
    """

    @app.exception_handler(RequestValidationError)
    async def validation_exception_handler(
        _: fastapi.Request, exc: RequestValidationError
    ) -> Response:
        status_code = status.HTTP_400_BAD_REQUEST
        return JSONResponse(
            status_code=status_code,
            content=jsonable_encoder(
                {
                    "detail": exc.errors(),
                    "message": "Request validation errors",
                    "status_code": status_code,
                }
            ),
        )

    @app.exception_handler(HTTPException)
    async def http_exception_handler(
        request: fastapi.Request, exc: HTTPException
    ) -> Response:
        return await default_exception_handler(request, exc)
