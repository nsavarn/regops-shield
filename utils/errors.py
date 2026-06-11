"""Custom exception hierarchy and FastAPI error handlers for RegOps Shield.

Centralises all error handling so every response follows a consistent
JSON structure that clients and monitoring systems can rely on.
"""
from __future__ import annotations

from typing import Any, Optional

from fastapi import FastAPI, Request, status
from fastapi.responses import JSONResponse
from pydantic import ValidationError


# ---------------------------------------------------------------------------
# Exception Hierarchy
# ---------------------------------------------------------------------------

class RegOpsError(Exception):
    """Base exception for all RegOps Shield errors."""

    def __init__(
        self,
        message: str,
        code: str = "REGOPS_ERROR",
        status_code: int = status.HTTP_500_INTERNAL_SERVER_ERROR,
        details: Optional[Any] = None,
    ) -> None:
        super().__init__(message)
        self.message = message
        self.code = code
        self.status_code = status_code
        self.details = details


class ValidationFailed(RegOpsError):
    """Raised when request or policy validation fails."""

    def __init__(self, message: str, details: Optional[Any] = None) -> None:
        super().__init__(
            message=message,
            code="VALIDATION_FAILED",
            status_code=status.HTTP_422_UNPROCESSABLE_ENTITY,
            details=details,
        )


class PolicyNotFound(RegOpsError):
    """Raised when the requested policy document does not exist."""

    def __init__(self, policy_id: str) -> None:
        super().__init__(
            message=f"Policy '{policy_id}' not found.",
            code="POLICY_NOT_FOUND",
            status_code=status.HTTP_404_NOT_FOUND,
        )


class AgentExecutionError(RegOpsError):
    """Raised when an agent fails during execution."""

    def __init__(self, agent_name: str, reason: str) -> None:
        super().__init__(
            message=f"Agent '{agent_name}' failed: {reason}",
            code="AGENT_EXECUTION_ERROR",
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
        )


class IntegrityCheckFailed(RegOpsError):
    """Raised when SHA-256 integrity verification fails."""

    def __init__(self, expected: str, actual: str) -> None:
        super().__init__(
            message="SHA-256 integrity check failed.",
            code="INTEGRITY_CHECK_FAILED",
            status_code=status.HTTP_409_CONFLICT,
            details={"expected": expected, "actual": actual},
        )


class RateLimitExceeded(RegOpsError):
    """Raised when a client exceeds the API rate limit."""

    def __init__(self) -> None:
        super().__init__(
            message="Rate limit exceeded. Please retry after a short delay.",
            code="RATE_LIMIT_EXCEEDED",
            status_code=status.HTTP_429_TOO_MANY_REQUESTS,
        )


# ---------------------------------------------------------------------------
# Error Response Helper
# ---------------------------------------------------------------------------

def _error_response(error: RegOpsError) -> JSONResponse:
    """Convert a RegOpsError to a standardised JSONResponse."""
    body: dict[str, Any] = {
        "error": {
            "code": error.code,
            "message": error.message,
        }
    }
    if error.details is not None:
        body["error"]["details"] = error.details
    return JSONResponse(status_code=error.status_code, content=body)


# ---------------------------------------------------------------------------
# FastAPI Exception Handlers
# ---------------------------------------------------------------------------

def register_error_handlers(app: FastAPI) -> None:
    """Register all custom exception handlers on the FastAPI app.

    Call this once during application startup::

        from utils.errors import register_error_handlers
        register_error_handlers(app)
    """

    @app.exception_handler(RegOpsError)
    async def regops_error_handler(
        request: Request, exc: RegOpsError
    ) -> JSONResponse:
        return _error_response(exc)

    @app.exception_handler(ValidationError)
    async def pydantic_validation_handler(
        request: Request, exc: ValidationError
    ) -> JSONResponse:
        error = ValidationFailed(
            message="Request validation failed.",
            details=exc.errors(),
        )
        return _error_response(error)

    @app.exception_handler(Exception)
    async def unhandled_exception_handler(
        request: Request, exc: Exception
    ) -> JSONResponse:
        error = RegOpsError(
            message="An unexpected error occurred.",
            code="INTERNAL_SERVER_ERROR",
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
        )
        return _error_response(error)
