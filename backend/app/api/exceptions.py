from datetime import UTC, datetime
from typing import Any

from fastapi import FastAPI, Request, status
from fastapi.responses import JSONResponse
from pydantic import BaseModel, Field


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


def register_exception_handlers(app: FastAPI) -> None:
    """Registers application exception handlers on FastAPI application instance."""

    @app.exception_handler(RepositoryNotFoundError)
    async def repo_not_found_handler(request: Request, exc: RepositoryNotFoundError):
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
        return JSONResponse(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            content=ErrorResponse(
                error_code="PREDICTION_ERROR",
                message=exc.message,
                details=exc.details,
            ).model_dump(),
        )
