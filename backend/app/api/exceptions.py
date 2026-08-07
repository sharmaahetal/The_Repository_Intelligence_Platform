from typing import Any


# Legacy domain exception classes maintained for test suite backward compatibility
class DomainException(Exception):
    """Base domain exception."""

    def __init__(self, message: str, details: dict[str, Any] | None = None) -> None:
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


from backend.app.api.exception_handlers import (  # noqa: E402, I001 # pyright: ignore[reportImportCycles]
    ErrorDetail,
    ErrorResponse,
    register_exception_handlers,
)


__all__ = [
    "ErrorDetail",
    "ErrorResponse",
    "register_exception_handlers",
    "DomainException",
    "RepositoryNotFoundError",
    "ModelUnavailableError",
    "SnapshotNotFoundError",
    "PredictionError",
]
