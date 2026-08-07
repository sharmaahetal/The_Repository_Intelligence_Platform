# pyright: reportImportCycles=false
"""Global exception handlers for Repository Intelligence Platform API layer."""

from __future__ import annotations

import re
import traceback
from datetime import UTC, datetime
from typing import Any

from fastapi import FastAPI, Request, status
from fastapi.responses import JSONResponse
from pydantic import BaseModel, ConfigDict, Field, computed_field, model_validator

from backend.app.logging import get_request_context, logger
from backend.app.services.exceptions import (
    DuplicatePredictionError,
    DuplicateSnapshotError,
    InvalidModelVersion,
    InvalidPredictionRequest,
    ModelVersionAlreadyExists,
    ModelVersionNotFound,
    PredictionExplanationAlreadyExists,
    PredictionExplanationNotFound,
    PredictionNotFound,
    RepositoryAlreadyExists,
    RepositoryNotFound,
    ServiceError,
    SnapshotNotFound,
)


class ErrorDetail(BaseModel):
    """Encapsulated error detail object containing type, code, message, request_id, and timestamp."""

    model_config = ConfigDict(frozen=True)

    type: str
    message: str
    request_id: str = "unknown"
    timestamp: str = Field(default_factory=lambda: datetime.now(UTC).isoformat())

    @computed_field  # type: ignore[misc]
    @property
    def code(self) -> str:
        return self.type


class ErrorResponse(BaseModel):
    """Standardized JSON error response structure across all API endpoints."""

    model_config = ConfigDict(frozen=True)

    error: ErrorDetail
    error_code: str
    message: str
    request_id: str = "unknown"
    details: dict[str, Any] = Field(default_factory=dict)
    timestamp: str = Field(default_factory=lambda: datetime.now(UTC).isoformat())

    @model_validator(mode="before")
    @classmethod
    def populate_defaults(cls, data: Any) -> Any:
        """Ensure error, error_code, message, and details are consistent."""
        if isinstance(data, dict):
            code = data.get("error_code") or "INTERNAL_SERVER_ERROR"
            msg = data.get("message") or ""
            req_id = data.get("request_id") or "unknown"
            err = data.get("error")
            if err is None:
                data["error"] = {"type": code, "message": msg, "request_id": req_id}
            elif isinstance(err, dict):
                if "type" not in err and "code" in err:
                    err["type"] = err["code"]
                if "request_id" not in err:
                    err["request_id"] = req_id
            if not data.get("error_code") and isinstance(data.get("error"), dict):
                data["error_code"] = data["error"].get("type") or data["error"].get("code", "INTERNAL_SERVER_ERROR")
            if not data.get("message") and isinstance(data.get("error"), dict):
                data["message"] = data["error"].get("message", "")
        return data


def _get_error_code(exc: Exception) -> str:
    """Map exception class name to standardized uppercase error_code string."""
    name = exc.__class__.__name__
    mapping = {
        "RepositoryNotFound": "REPOSITORY_NOT_FOUND",
        "RepositoryNotFoundError": "REPOSITORY_NOT_FOUND",
        "ServiceRepositoryNotFound": "REPOSITORY_NOT_FOUND",
        "RepositoryAlreadyExists": "REPOSITORY_ALREADY_EXISTS",
        "SnapshotNotFound": "SNAPSHOT_NOT_FOUND",
        "SnapshotNotFoundError": "SNAPSHOT_NOT_FOUND",
        "DuplicateSnapshotError": "DUPLICATE_SNAPSHOT",
        "PredictionNotFound": "PREDICTION_NOT_FOUND",
        "DuplicatePredictionError": "DUPLICATE_PREDICTION",
        "InvalidPredictionRequest": "INVALID_PREDICTION_REQUEST",
        "ModelVersionNotFound": "MODEL_VERSION_NOT_FOUND",
        "ModelNotFound": "MODEL_VERSION_NOT_FOUND",
        "ModelVersionAlreadyExists": "MODEL_VERSION_ALREADY_EXISTS",
        "InvalidModelVersion": "INVALID_MODEL_VERSION",
        "PredictionExplanationNotFound": "PREDICTION_EXPLANATION_NOT_FOUND",
        "PredictionExplanationAlreadyExists": "PREDICTION_EXPLANATION_ALREADY_EXISTS",
        "ModelUnavailableError": "MODEL_UNAVAILABLE",
        "PredictionError": "PREDICTION_ERROR",
    }
    if name in mapping:
        return mapping[name]

    return re.sub(r"(?<!^)(?=[A-Z])", "_", name).upper()


def _log_exception(
    request: Request,
    exc: Exception,
    error_code: str,
    status_code: int,
) -> str:
    """Helper logging rich exception context including request_id, endpoint, and stacktrace."""
    ctx = get_request_context()
    request_id = getattr(request.state, "request_id", None) or ctx.get("request_id", "unknown")
    endpoint = request.url.path
    user_agent = request.headers.get("user-agent", "unknown")
    stacktrace = traceback.format_exc()
    exc_details = getattr(exc, "details", None)
    details_dict = exc_details if isinstance(exc_details, dict) else {}

    repository = (
        ctx.get("repository")
        or request.query_params.get("repo")
        or details_dict.get("repository")
        or "unknown"
    )
    model_version = (
        details_dict.get("model_version")
        or ctx.get("model_version")
        or "unknown"
    )

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
    """Registers application global exception handlers on a FastAPI application instance."""
    from backend.app.api.exceptions import (  # pyright: ignore[reportImportCycles]
        DomainException,
        ModelUnavailableError,
        PredictionError,
        RepositoryNotFoundError,
        SnapshotNotFoundError,
    )

    # 404 Not Found exceptions
    @app.exception_handler(RepositoryNotFound)
    @app.exception_handler(RepositoryNotFoundError)
    @app.exception_handler(SnapshotNotFound)
    @app.exception_handler(SnapshotNotFoundError)
    @app.exception_handler(PredictionNotFound)
    @app.exception_handler(ModelVersionNotFound)
    @app.exception_handler(PredictionExplanationNotFound)
    async def not_found_handler(request: Request, exc: Exception) -> JSONResponse:
        exc_type = exc.__class__.__name__
        error_code = _get_error_code(exc)
        msg = str(getattr(exc, "message", str(exc)))
        req_id = _log_exception(request, exc, error_code, status.HTTP_404_NOT_FOUND)
        details = getattr(exc, "details", {}) or {}
        return JSONResponse(
            status_code=status.HTTP_404_NOT_FOUND,
            content=ErrorResponse(
                error=ErrorDetail(type=exc_type, message=msg),
                error_code=error_code,
                message=msg,
                request_id=req_id,
                details=details if isinstance(details, dict) else {},
            ).model_dump(),
        )

    # 409 Conflict / Already Exists exceptions
    @app.exception_handler(RepositoryAlreadyExists)
    @app.exception_handler(DuplicateSnapshotError)
    @app.exception_handler(DuplicatePredictionError)
    @app.exception_handler(ModelVersionAlreadyExists)
    @app.exception_handler(PredictionExplanationAlreadyExists)
    async def conflict_handler(request: Request, exc: Exception) -> JSONResponse:
        exc_type = exc.__class__.__name__
        error_code = _get_error_code(exc)
        msg = str(getattr(exc, "message", str(exc)))
        req_id = _log_exception(request, exc, error_code, status.HTTP_409_CONFLICT)
        return JSONResponse(
            status_code=status.HTTP_409_CONFLICT,
            content=ErrorResponse(
                error=ErrorDetail(type=exc_type, message=msg),
                error_code=error_code,
                message=msg,
                request_id=req_id,
            ).model_dump(),
        )

    # 400 Bad Request / Invalid Request exceptions
    @app.exception_handler(InvalidPredictionRequest)
    @app.exception_handler(InvalidModelVersion)
    async def bad_request_handler(request: Request, exc: Exception) -> JSONResponse:
        exc_type = exc.__class__.__name__
        error_code = _get_error_code(exc)
        msg = str(getattr(exc, "message", str(exc)))
        req_id = _log_exception(request, exc, error_code, status.HTTP_400_BAD_REQUEST)
        return JSONResponse(
            status_code=status.HTTP_400_BAD_REQUEST,
            content=ErrorResponse(
                error=ErrorDetail(type=exc_type, message=msg),
                error_code=error_code,
                message=msg,
                request_id=req_id,
            ).model_dump(),
        )

    # 503 Service Unavailable
    @app.exception_handler(ModelUnavailableError)
    async def model_unavailable_handler(request: Request, exc: ModelUnavailableError) -> JSONResponse:
        exc_type = exc.__class__.__name__
        error_code = _get_error_code(exc)
        msg = str(getattr(exc, "message", str(exc)))
        req_id = _log_exception(request, exc, error_code, status.HTTP_503_SERVICE_UNAVAILABLE)
        return JSONResponse(
            status_code=status.HTTP_503_SERVICE_UNAVAILABLE,
            content=ErrorResponse(
                error=ErrorDetail(type=exc_type, message=msg),
                error_code=error_code,
                message=msg,
                request_id=req_id,
                details=exc.details,
            ).model_dump(),
        )

    # 500 Prediction Error
    @app.exception_handler(PredictionError)
    async def prediction_error_handler(request: Request, exc: PredictionError) -> JSONResponse:
        exc_type = exc.__class__.__name__
        error_code = _get_error_code(exc)
        msg = str(getattr(exc, "message", str(exc)))
        req_id = _log_exception(request, exc, error_code, status.HTTP_500_INTERNAL_SERVER_ERROR)
        return JSONResponse(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            content=ErrorResponse(
                error=ErrorDetail(type=exc_type, message=msg),
                error_code=error_code,
                message=msg,
                request_id=req_id,
                details=exc.details,
            ).model_dump(),
        )

    # Base DomainException fallback (500)
    @app.exception_handler(DomainException)
    async def domain_exception_handler(request: Request, exc: DomainException) -> JSONResponse:
        exc_type = exc.__class__.__name__
        error_code = _get_error_code(exc)
        msg = exc.message
        req_id = _log_exception(request, exc, error_code, status.HTTP_500_INTERNAL_SERVER_ERROR)
        return JSONResponse(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            content=ErrorResponse(
                error=ErrorDetail(type=exc_type, message=msg),
                error_code=error_code,
                message=msg,
                request_id=req_id,
                details=exc.details,
            ).model_dump(),
        )

    # Base ServiceError fallback (500)
    @app.exception_handler(ServiceError)
    async def service_error_handler(request: Request, exc: ServiceError) -> JSONResponse:
        exc_type = exc.__class__.__name__
        error_code = _get_error_code(exc)
        msg = exc.message
        req_id = _log_exception(request, exc, error_code, status.HTTP_500_INTERNAL_SERVER_ERROR)
        return JSONResponse(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            content=ErrorResponse(
                error=ErrorDetail(type=exc_type, message=msg),
                error_code=error_code,
                message=msg,
                request_id=req_id,
            ).model_dump(),
        )

    # Global Exception fallback (500)
    @app.exception_handler(Exception)
    async def unhandled_exception_handler(request: Request, exc: Exception) -> JSONResponse:
        req_id = _log_exception(request, exc, "INTERNAL_SERVER_ERROR", status.HTTP_500_INTERNAL_SERVER_ERROR)
        return JSONResponse(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            content=ErrorResponse(
                error=ErrorDetail(type="InternalServerError", message="An unexpected internal error occurred."),
                error_code="INTERNAL_SERVER_ERROR",
                message="An unexpected internal error occurred.",
                request_id=req_id,
            ).model_dump(),
        )
