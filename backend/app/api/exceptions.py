import traceback
from datetime import UTC, datetime
from typing import Any

from fastapi import FastAPI, Request, status
from fastapi.responses import JSONResponse
from pydantic import BaseModel, Field

from backend.app.logging import get_request_context, logger


class ErrorResponse(BaseModel):
    """Standardized JSON error response body across all API endpoints."""

    error_code: str
    message: str
    details: dict[str, Any] = Field(default_factory=dict)
    timestamp: str = Field(default_factory=lambda: datetime.now(UTC).isoformat())


# Domain Application Exceptions
class DomainException(Exception):
    """Base domain exception."""

    def __init__(self, message: str, details: dict[str, Any] | None = None):
        super().__init__(message)
        self.message = message
        self.details = details or {}


class RepositoryNotFoundError(DomainException):
    """Raised when target GitHub repository is not found or inaccessible."""

    pass


class ModelUnavailableError(DomainException):
    """Raised when no trained model binary or registry manifest is loaded in memory."""

    pass


class SnapshotNotFoundError(DomainException):
    """Raised when historical or point-in-time snapshot cannot be built."""

    pass


class PredictionError(DomainException):
    """Raised when ML inference computation encounters an error."""

    pass


def _log_exception_context(
    request: Request,
    exc: Exception,
    error_code: str,
    status_code: int,
) -> None:
    """Helper logging rich exception context including request_id, endpoint, stacktrace, user_agent, repository, and model_version."""
    ctx = get_request_context()
    request_id = getattr(request.state, "request_id", None) or ctx.get("request_id", "unknown")
    endpoint = request.url.path
    user_agent = request.headers.get("user-agent", "unknown")
    repository = (
        ctx.get("repository")
        or request.query_params.get("repo")
        or (exc.details.get("repository") if hasattr(exc, "details") else None)
        or "unknown"
    )
    model_version = (
        (exc.details.get("model_version") if hasattr(exc, "details") else None)
        or ctx.get("model_version")
        or "unknown"
    )
    stacktrace = traceback.format_exc()

    logger.error(
        f"Exception [{error_code}] on {request.method} {endpoint}: {str(exc)}",
        extra={
            "request_id": request_id,
            "endpoint": endpoint,
            "method": request.method,
            "status_code": status_code,
            "error_code": error_code,
            "user_agent": user_agent,
            "repository": repository,
            "model_version": model_version,
            "stacktrace": stacktrace,
        },
        exc_info=True,
    )


def register_exception_handlers(app: FastAPI) -> None:
    """Registers application exception handlers on FastAPI application instance."""

    @app.exception_handler(RepositoryNotFoundError)
    async def repo_not_found_handler(request: Request, exc: RepositoryNotFoundError):
        _log_exception_context(request, exc, "REPOSITORY_NOT_FOUND", status.HTTP_404_NOT_FOUND)
        return JSONResponse(
            status_code=status.HTTP_404_NOT_FOUND,
            content=ErrorResponse(
                error_code="REPOSITORY_NOT_FOUND",
                message=exc.message,
                details=exc.details,
            ).model_dump(),
        )

    @app.exception_handler(SnapshotNotFoundError)
    async def snapshot_not_found_handler(request: Request, exc: SnapshotNotFoundError):
        _log_exception_context(request, exc, "SNAPSHOT_NOT_FOUND", status.HTTP_404_NOT_FOUND)
        return JSONResponse(
            status_code=status.HTTP_404_NOT_FOUND,
            content=ErrorResponse(
                error_code="SNAPSHOT_NOT_FOUND",
                message=exc.message,
                details=exc.details,
            ).model_dump(),
        )

    @app.exception_handler(ModelUnavailableError)
    async def model_unavailable_handler(request: Request, exc: ModelUnavailableError):
        _log_exception_context(request, exc, "MODEL_UNAVAILABLE", status.HTTP_503_SERVICE_UNAVAILABLE)
        return JSONResponse(
            status_code=status.HTTP_503_SERVICE_UNAVAILABLE,
            content=ErrorResponse(
                error_code="MODEL_UNAVAILABLE",
                message=exc.message,
                details=exc.details,
            ).model_dump(),
        )

    @app.exception_handler(PredictionError)
    async def prediction_error_handler(request: Request, exc: PredictionError):
        _log_exception_context(request, exc, "PREDICTION_ERROR", status.HTTP_500_INTERNAL_SERVER_ERROR)
        return JSONResponse(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            content=ErrorResponse(
                error_code="PREDICTION_ERROR",
                message=exc.message,
                details=exc.details,
            ).model_dump(),
        )

    @app.exception_handler(Exception)
    async def unhandled_exception_handler(request: Request, exc: Exception):
        _log_exception_context(request, exc, "INTERNAL_SERVER_ERROR", status.HTTP_500_INTERNAL_SERVER_ERROR)
        return JSONResponse(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            content=ErrorResponse(
                error_code="INTERNAL_SERVER_ERROR",
                message="An unexpected internal error occurred.",
                details={},
            ).model_dump(),
        )
