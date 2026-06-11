"""Structured logging configuration for RegOps Shield.

Provides JSON-formatted structured logging powered by structlog,
designed for Google Cloud Run log ingestion and Cloud Logging.
"""
import logging
import os
import sys
from typing import Any

try:
    import structlog
    HAS_STRUCTLOG = True
except ImportError:
    HAS_STRUCTLOG = False


LOG_LEVEL = os.environ.get("LOG_LEVEL", "INFO").upper()
ENVIRONMENT = os.environ.get("ENVIRONMENT", "production")


def configure_logging() -> None:
    """Configure structured logging for the application.

    In production (Cloud Run), emits JSON logs compatible with
    Google Cloud Logging. In development/test, emits human-readable
    colored console output.
    """
    level = getattr(logging, LOG_LEVEL, logging.INFO)

    if HAS_STRUCTLOG:
        shared_processors: list[Any] = [
            structlog.contextvars.merge_contextvars,
            structlog.stdlib.add_logger_name,
            structlog.stdlib.add_log_level,
            structlog.stdlib.PositionalArgumentsFormatter(),
            structlog.processors.TimeStamper(fmt="iso"),
            structlog.processors.StackInfoRenderer(),
        ]

        if ENVIRONMENT in ("production", "staging"):
            # JSON output for Cloud Logging
            processors = shared_processors + [
                structlog.processors.format_exc_info,
                structlog.processors.JSONRenderer(),
            ]
        else:
            # Human-readable for local dev/test
            processors = shared_processors + [
                structlog.dev.ConsoleRenderer(colors=True),
            ]

        structlog.configure(
            processors=processors,
            wrapper_class=structlog.stdlib.BoundLogger,
            context_class=dict,
            logger_factory=structlog.stdlib.LoggerFactory(),
            cache_logger_on_first_use=True,
        )

    logging.basicConfig(
        format="%(message)s",
        stream=sys.stdout,
        level=level,
    )


def get_logger(name: str) -> Any:
    """Return a configured logger instance.

    Args:
        name: Logger name (typically __name__ of the calling module).

    Returns:
        A structlog BoundLogger or stdlib Logger depending on availability.
    """
    if HAS_STRUCTLOG:
        return structlog.get_logger(name)
    return logging.getLogger(name)


# Auto-configure on import
configure_logging()
