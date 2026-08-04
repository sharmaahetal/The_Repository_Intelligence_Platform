"""Domain-specific business exceptions for Repository Intelligence Platform service layer."""

from __future__ import annotations

from typing import Any


class ServiceError(Exception):
    """Base class for all business/service layer exceptions."""

    def __init__(self, message: str = "A service layer error occurred.") -> None:
        """Initialize ServiceError with formatted detail message."""
        super().__init__(message)
        self.message = message


class RepositoryAlreadyExists(ServiceError):
    """Raised when attempting to create a repository that already exists."""

    def __init__(self, identifier: str | int) -> None:
        """Format repository already exists exception message."""
        super().__init__(f"Repository '{identifier}' already exists.")
        self.identifier = identifier


class RepositoryNotFound(ServiceError):
    """Raised when a requested repository entity cannot be found."""

    def __init__(self, identifier: str | int) -> None:
        """Format repository not found exception message."""
        super().__init__(f"Repository '{identifier}' was not found.")
        self.identifier = identifier


class SnapshotNotFound(ServiceError):
    """Raised when a requested repository snapshot entity cannot be found."""

    def __init__(self, identifier: str | int) -> None:
        """Format snapshot not found exception message."""
        super().__init__(f"Snapshot '{identifier}' was not found.")
        self.identifier = identifier


class DuplicateSnapshotError(ServiceError):
    """Raised when attempting to record a duplicate snapshot at the same timestamp."""

    def __init__(self, repository_id: int, snapshot_time: Any) -> None:
        """Format duplicate snapshot exception message."""
        super().__init__(f"Snapshot for repository '{repository_id}' at '{snapshot_time}' already exists.")
        self.repository_id = repository_id
        self.snapshot_time = snapshot_time


class PredictionNotFound(ServiceError):
    """Raised when a requested prediction entity cannot be found."""

    def __init__(self, identifier: str | int) -> None:
        """Format prediction not found exception message."""
        super().__init__(f"Prediction '{identifier}' was not found.")
        self.identifier = identifier


class DuplicatePredictionError(ServiceError):
    """Raised when attempting to generate a duplicate prediction for a snapshot."""

    def __init__(self, identifier: str | int) -> None:
        """Format duplicate prediction exception message."""
        super().__init__(f"Prediction for '{identifier}' already exists.")
        self.identifier = identifier


class InvalidPredictionRequest(ServiceError):
    """Raised when prediction input parameters violate business validation rules."""

    def __init__(self, reason: str) -> None:
        """Format invalid prediction request exception message."""
        super().__init__(f"Invalid prediction request: {reason}")
        self.reason = reason


class ModelVersionNotFound(ServiceError):
    """Raised when a requested trained model version entity cannot be found."""

    def __init__(self, version: str | int) -> None:
        """Format model version not found exception message."""
        super().__init__(f"Model version '{version}' was not found.")
        self.version = version


class ModelVersionAlreadyExists(ServiceError):
    """Raised when attempting to register a model version string that already exists."""

    def __init__(self, version: str) -> None:
        """Format model version already exists exception message."""
        super().__init__(f"Model version '{version}' already exists.")
        self.version = version


class InvalidModelVersion(ServiceError):
    """Raised when a model version object or configuration is invalid."""

    def __init__(self, reason: str) -> None:
        """Format invalid model version exception message."""
        super().__init__(f"Invalid model version: {reason}")
        self.reason = reason


class PredictionExplanationNotFound(ServiceError):
    """Raised when a requested prediction explanation entity cannot be found."""

    def __init__(self, prediction_id: int) -> None:
        """Format prediction explanation not found exception message."""
        super().__init__(f"Explanation for prediction '{prediction_id}' was not found.")
        self.prediction_id = prediction_id


class PredictionExplanationAlreadyExists(ServiceError):
    """Raised when attempting to add a duplicate explanation for a prediction."""

    def __init__(self, prediction_id: int) -> None:
        """Format prediction explanation already exists exception message."""
        super().__init__(f"Explanation for prediction '{prediction_id}' already exists.")
        self.prediction_id = prediction_id


# Alias for backward compatibility across pipeline callers
ModelNotFound = ModelVersionNotFound

__all__ = [
    "ServiceError",
    "RepositoryAlreadyExists",
    "RepositoryNotFound",
    "SnapshotNotFound",
    "DuplicateSnapshotError",
    "PredictionNotFound",
    "DuplicatePredictionError",
    "InvalidPredictionRequest",
    "ModelVersionNotFound",
    "ModelNotFound",
    "ModelVersionAlreadyExists",
    "InvalidModelVersion",
    "PredictionExplanationNotFound",
    "PredictionExplanationAlreadyExists",
]
