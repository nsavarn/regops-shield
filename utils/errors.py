"""Custom exception hierarchy and FastAPI error handlers for RegOps Shield.

Centralises all error handling so every response follows a consistent
JSON structure that clients and monitoring systems can rely on.
"""
from __future__ import annotations

import logging
from http import HTTPStatus
from typing import Any, Optional

from fastapi import Request, status
from fastapi.responses import JSONResponse
from pydantic import ValidationError

logger = logging.getLogger(__name__)

# ---------------------------------------------------------------------------
# Exception hierarchy
# ---------------------------------------------------------------------------


class RegOpsError(Exception):
    """Base exception for all RegOps Shield errors."""

    http_status: int = status.HTTP_500_INTERNAL_SERVER_ERROR
    error_code: str = "REGOPS_ERROR"

    def __init__(
        self,
        message: str = "An unexpected error occurred.",
        details: Optional[Any] = None,
        http_status: Optional[int] = None,
        error_code: Optional[str] = None,
    ) -> None:
        super().__init__(message)
        self.message = message
        self.details = details
        if http_status is not None:
            self.http_status = http_status
        if error_code is not None:
            self.error_code = error_code


class NotFoundError(RegOpsError):
    """Raised when a requested resource does not exist."""

    http_status = status.HTTP_404_NOT_FOUND
    error_code = "NOT_FOUND"

    def __init__(self, resource: str = "Resource") -> None:
        super().__init__(message=f"{resource} not found.")


class ValidationFailed(RegOpsError):
    """Raised when input validation fails."""

    http_status = status.HTTP_422_UNPROCESSABLE_ENTITY
    error_code = "VALIDATION_FAILED"


class ServiceUnavailableError(RegOpsError):
    """Raised when a downstream service is unreachable."""

    http_status = status.HTTP_503_SERVICE_UNAVAILABLE
    error_code = "SERVICE_UNAVAILABLE"


class UnauthorizedError(RegOpsError):
    """Raised when the caller lacks valid credentials."""

    http_status = status.HTTP_401_UNAUTHORIZED
    error_code = "UNAUTHORIZED"


class ForbiddenError(RegOpsError):
    """Raised when the caller lacks permission for the operation."""

    http_status = status.HTTP_403_FORBIDDEN
    error_code = "FORBIDDEN"


# ---------------------------------------------------------------------------
# Internal helper
# ---------------------------------------------------------------------------


def _error_response(exc: RegOpsError) -> JSONResponse:
    """Serialize a RegOpsError into a standard JSONResponse."""
    body: dict[str, Any] = {
        "error": {
            "code": exc.error_code,
            "message": exc.message,
        }
    }
    if exc.details is not None:
        body["error"]["details"] = exc.details
    return JSONResponse(status_code=exc.http_status, content=body)


# ---------------------------------------------------------------------------
# Standalone handler functions (imported by main.py)
# ---------------------------------------------------------------------------


async def handler_regops_error(request: Request, exc: Exception) -> JSONResponse:  # noqa: ARG001
    """Handle RegOpsError and its subclasses."""
    assert isinstance(exc, RegOpsError)
    logger.warning(
        "RegOpsError [%s]: %s",
        exc.error_code,
        exc.message,
        extra={"path": request.url.path},
    )
    return _error_response(exc)


async def handler_validation_error(request: Request, exc: Exception) -> JSONResponse:  # noqa: ARG001
    """Handle Pydantic ValidationError."""
    assert isinstance(exc, ValidationError)
    logger.warning(
        "ValidationError on %s: %s",
        request.url.path,
        exc.error_count(),
    )
    error = ValidationFailed(
        message="Request validation failed.",
        details=exc.errors(include_url=False),
    )
    return _error_response(error)


async def handler_unhandled(request: Request, exc: Exception) -> JSONResponse:  # noqa: ARG001
    """Catch-all handler for unhandled exceptions."""
    logger.exception(
        "Unhandled exception on %s",
        request.url.path,
        exc_info=exc,
    )
    error = RegOpsError(
        message="An unexpected internal error occurred.",
        http_status=status.HTTP_500_INTERNAL_SERVER_ERROR,
        error_code="INTERNAL_SERVER_ERROR",
    )
    return _error_response(error)


# ---------------------------------------------------------------------------
# Helper to register all handlers on an existing app (optional pattern)
# ---------------------------------------------------------------------------


def register_error_handlers(app: Any) -> None:  # type: ignore[misc]
    """Register all error handlers on a FastAPI app instance."""
    from pydantic import ValidationError as PydanticValidationError  # local import

    app.add_exception_handler(RegOpsError, handler_regops_error)
    app.add_exception_handler(PydanticValidationError, handler_validation_error)
    app.add_exception_handler(Exception, handler_unhandled)
