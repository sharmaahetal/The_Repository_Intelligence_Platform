import traceback
from datetime import UTC, datetime
from typing import Any

from fastapi import FastAPI, Request, status
from fastapi.responses import JSONResponse
from pydantic import BaseModel, ConfigDict, Field

from backend.app.logging import get_request_context, logger


class ErrorBody(BaseModel):
    """Encapsulated error object details."""

    model_config = ConfigDict(frozen=True)

    code: str
    message: str
    request_id: str = "unknown"
    timestamp: str = Field(default_factory=lambda: datetime.now(UTC).isoformat())


class ErrorResponse(BaseModel):
    """Standardized JSON error response body across all API endpoints."""

    model_config = ConfigDict(frozen=True)

    error_code: str
    message: str
    error: ErrorBody
    details: dict[str, Any] = Field(default_factory=dict)
    timestamp: str = Field(default_factory=lambda: datetime.now(UTC).isoformat())

    def __init__(
        self,
        error_code: str | None = None,
        message: str = "",
        request_id: str = "unknown",
        error: ErrorBody | None = None,
        details: dict[str, Any] | None = None,
        **data: Any,
    ):
        code = error_code or (error.code if error else data.get("error_code")) or "INTERNAL_SERVER_ERROR"
        msg = message or (error.message if error else data.get("message")) or ""
        req_id = request_id or (error.request_id if error else data.get("request_id")) or "unknown"
        err_body = error or ErrorBody(code=code, message=msg, request_id=req_id)

        super().__init__(
            error_code=code,
            message=msg,
            error=err_body,
            details=details or {},
            **data,
        )


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
) -> str:
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
    return request_id


def register_exception_handlers(app: FastAPI) -> None:
    """Registers application exception handlers on FastAPI application instance."""

    @app.exception_handler(RepositoryNotFoundError)
    async def repo_not_found_handler(request: Request, exc: RepositoryNotFoundError):
        req_id = _log_exception_context(request, exc, "REPOSITORY_NOT_FOUND", status.HTTP_404_NOT_FOUND)
        return JSONResponse(
            status_code=status.HTTP_404_NOT_FOUND,
            content=ErrorResponse(
                error_code="REPOSITORY_NOT_FOUND",
                message=exc.message,
                request_id=req_id,
                details=exc.details,
            ).model_dump(),
        )

    @app.exception_handler(SnapshotNotFoundError)
    async def snapshot_not_found_handler(request: Request, exc: SnapshotNotFoundError):
        req_id = _log_exception_context(request, exc, "SNAPSHOT_NOT_FOUND", status.HTTP_404_NOT_FOUND)
        return JSONResponse(
            status_code=status.HTTP_404_NOT_FOUND,
            content=ErrorResponse(
                error_code="SNAPSHOT_NOT_FOUND",
                message=exc.message,
                request_id=req_id,
                details=exc.details,
            ).model_dump(),
        )

    @app.exception_handler(ModelUnavailableError)
    async def model_unavailable_handler(request: Request, exc: ModelUnavailableError):
        req_id = _log_exception_context(request, exc, "MODEL_UNAVAILABLE", status.HTTP_503_SERVICE_UNAVAILABLE)
        return JSONResponse(
            status_code=status.HTTP_503_SERVICE_UNAVAILABLE,
            content=ErrorResponse(
                error_code="MODEL_UNAVAILABLE",
                message=exc.message,
                request_id=req_id,
                details=exc.details,
            ).model_dump(),
        )

    @app.exception_handler(PredictionError)
    async def prediction_error_handler(request: Request, exc: PredictionError):
        req_id = _log_exception_context(request, exc, "PREDICTION_ERROR", status.HTTP_500_INTERNAL_SERVER_ERROR)
        return JSONResponse(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            content=ErrorResponse(
                error_code="PREDICTION_ERROR",
                message=exc.message,
                request_id=req_id,
                details=exc.details,
            ).model_dump(),
        )

    @app.exception_handler(Exception)
    async def unhandled_exception_handler(request: Request, exc: Exception):
        req_id = _log_exception_context(request, exc, "INTERNAL_SERVER_ERROR", status.HTTP_500_INTERNAL_SERVER_ERROR)
        return JSONResponse(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            content=ErrorResponse(
                error_code="INTERNAL_SERVER_ERROR",
                message="An unexpected internal error occurred.",
                request_id=req_id,
                details={},
            ).model_dump(),
        )
