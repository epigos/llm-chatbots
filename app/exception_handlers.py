import logging

import fastapi
from fastapi import status
from fastapi.encoders import jsonable_encoder
from fastapi.exceptions import HTTPException, RequestValidationError
from fastapi.responses import JSONResponse, Response
from pydantic_core import ValidationError

from app import exceptions

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
    details = None
    if isinstance(exc, fastapi.exceptions.HTTPException):
        status_code = exc.status_code
        headers = exc.headers
        message = str(exc.detail)
    elif isinstance(exc, exceptions.DoesNotExist):
        status_code = status.HTTP_404_NOT_FOUND
        message = str(exc)
    elif isinstance(exc, (RequestValidationError, ValidationError)):
        status_code = status.HTTP_400_BAD_REQUEST
        message = "Request validation errors"
        details = exc.errors()
    elif isinstance(exc, exceptions.AuthenticationError):
        status_code = status.HTTP_401_UNAUTHORIZED
        message = str(exc)
        headers = {"WWW-Authenticate": "Bearer"}
    else:
        logger.exception(exc, exc_info=True)

    return JSONResponse(
        status_code=status_code,
        content=jsonable_encoder(
            {"message": message, "status_code": status_code, "detail": details}
        ),
        headers=headers,
    )


def override_exception_handlers(app: fastapi.FastAPI) -> None:
    """
    Override exception default exception handlers
    """

    @app.exception_handler(RequestValidationError)
    @app.exception_handler(ValidationError)
    @app.exception_handler(exceptions.DoesNotExist)
    @app.exception_handler(exceptions.AuthenticationError)
    @app.exception_handler(HTTPException)
    async def http_exception_handler(
        request: fastapi.Request, exc: Exception | HTTPException
    ) -> Response:
        return await default_exception_handler(request, exc)
