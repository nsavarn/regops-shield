"""RegOps Shield - Main Application Entry Point.

FastAPI application with health endpoints, rate limiting,
structured logging, and centralized error handling.
"""
from __future__ import annotations

import hashlib
import hmac
import os
import time
from contextlib import asynccontextmanager
from typing import Any

from fastapi import FastAPI, HTTPException, Request, status
from fastapi.middleware.cors import CORSMiddleware
from fastapi.responses import JSONResponse
from pydantic import ValidationError
from slowapi import Limiter, _rate_limit_exceeded_handler
from slowapi.errors import RateLimitExceeded
from slowapi.util import get_remote_address

from utils.errors import RegOpsError, handler_regops_error, handler_validation_error, handler_unhandled
from utils.logging_config import get_logger
from utils.models import HealthResponse, ReadinessResponse

# ---------------------------------------------------------------------------
# App metadata
# ---------------------------------------------------------------------------
APP_TITLE = "RegOps Shield"
APP_VERSION = os.getenv("APP_VERSION", "0.1.0")
APP_DESCRIPTION = (
    "AI-powered regulatory operations platform for insurance claim triage, "
    "compliance checking, and automated remediation."
)

logger = get_logger(__name__)

# ---------------------------------------------------------------------------
# Rate limiter (slowapi)
# ---------------------------------------------------------------------------
limiter = Limiter(key_func=get_remote_address, default_limits=["60/minute"])


# ---------------------------------------------------------------------------
# Lifespan: startup / shutdown hooks
# ---------------------------------------------------------------------------
@asynccontextmanager
async def lifespan(application: FastAPI):  # type: ignore[type-arg]
    """Application lifespan manager."""
    logger.info("Starting %s v%s", APP_TITLE, APP_VERSION)
    # Future: initialise DB pool, load models, warm caches
    yield
    logger.info("Shutting down %s", APP_TITLE)


# ---------------------------------------------------------------------------
# Application factory
# ---------------------------------------------------------------------------
def create_app() -> FastAPI:
    """Create and configure the FastAPI application."""
    application = FastAPI(
        title=APP_TITLE,
        version=APP_VERSION,
        description=APP_DESCRIPTION,
        docs_url="/docs",
        redoc_url="/redoc",
        openapi_url="/openapi.json",
        lifespan=lifespan,
    )

    # -----------------------------------------------------------------------
    # Middleware
    # -----------------------------------------------------------------------
    allowed_origins = os.getenv("ALLOWED_ORIGINS", "*").split(",")
    application.add_middleware(
        CORSMiddleware,
        allow_origins=allowed_origins,
        allow_credentials=True,
        allow_methods=["GET", "POST"],
        allow_headers=["*"],
    )

    # Rate limiter state + handler
    application.state.limiter = limiter
    application.add_exception_handler(RateLimitExceeded, _rate_limit_exceeded_handler)  # type: ignore[arg-type]

    # -----------------------------------------------------------------------
    # Centralised error handlers
    # -----------------------------------------------------------------------
    application.add_exception_handler(RegOpsError, handler_regops_error)  # type: ignore[arg-type]
    application.add_exception_handler(ValidationError, handler_validation_error)  # type: ignore[arg-type]
    application.add_exception_handler(Exception, handler_unhandled)  # type: ignore[arg-type]

    # -----------------------------------------------------------------------
    # Routes
    # -----------------------------------------------------------------------
    _register_routes(application)

    # -----------------------------------------------------------------------
    # Include feature routers (wired as agents are built)
    # -----------------------------------------------------------------------
    # from agents.supervisor import router as supervisor_router
    # application.include_router(supervisor_router, prefix="/api/v1")

    return application


# ---------------------------------------------------------------------------
# Route definitions
# ---------------------------------------------------------------------------
_START_TIME = time.time()


def _register_routes(application: FastAPI) -> None:  # noqa: WPS430
    """Register core routes on the given application instance."""

    @application.get("/", response_model=dict, tags=["Meta"])
    @limiter.limit("30/minute")
    async def root(request: Request) -> dict[str, Any]:
        """Root endpoint — service discovery."""
        return {
            "service": APP_TITLE,
            "version": APP_VERSION,
            "docs": "/docs",
            "health": "/health",
            "readiness": "/readiness",
        }

    @application.get(
        "/health",
        response_model=HealthResponse,
        tags=["Observability"],
        summary="Liveness probe",
    )
    async def health() -> HealthResponse:
        """Kubernetes / Cloud Run liveness probe."""
        return HealthResponse(status="ok", version=APP_VERSION)

    @application.get(
        "/readiness",
        response_model=ReadinessResponse,
        tags=["Observability"],
        summary="Readiness probe",
    )
    async def readiness() -> ReadinessResponse:
        """Kubernetes / Cloud Run readiness probe."""
        uptime_seconds = round(time.time() - _START_TIME, 2)
        # Extend with real dependency checks (DB, cache, etc.) as needed
        checks: dict[str, str] = {"api": "ok"}
        ready = all(v == "ok" for v in checks.values())
        if not ready:
            raise HTTPException(
                status_code=status.HTTP_503_SERVICE_UNAVAILABLE,
                detail="One or more dependencies are unavailable.",
            )
        return ReadinessResponse(
            status="ready",
            uptime_seconds=uptime_seconds,
            checks=checks,
        )

    @application.get(
        "/integrity/{value}",
        tags=["Security"],
        summary="SHA-256 integrity check",
    )
    async def integrity_check(value: str) -> dict[str, str]:
        """Return SHA-256 digest of a value for client-side integrity verification."""
        digest = hashlib.sha256(value.encode()).hexdigest()
        return {"input": value, "sha256": digest}


# ---------------------------------------------------------------------------
# Application instance (module-level for uvicorn / gunicorn)
# ---------------------------------------------------------------------------
app = create_app()


# ---------------------------------------------------------------------------
# Dev entrypoint
# ---------------------------------------------------------------------------
if __name__ == "__main__":
    import uvicorn

    uvicorn.run(
        "main:app",
        host="0.0.0.0",
        port=int(os.environ.get("PORT", "8080")),
        log_level=os.environ.get("LOG_LEVEL", "info").lower(),
        reload=os.environ.get("ENV", "production") == "development",
    )
