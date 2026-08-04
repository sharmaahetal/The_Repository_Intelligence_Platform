"""Public API exports for Repository Intelligence Platform service layer."""

from backend.app.services.exceptions import (
    DuplicatePredictionError,
    DuplicateSnapshotError,
    InvalidModelVersion,
    InvalidPredictionRequest,
    ModelNotFound,
    ModelNotFoundError,
    ModelVersionAlreadyExists,
    ModelVersionNotFound,
    PredictionExplanationAlreadyExists,
    PredictionExplanationNotFound,
    PredictionNotFound,
    PredictionNotFoundError,
    RepositoryAlreadyExists,
    RepositoryAlreadyExistsError,
    RepositoryNotFound,
    RepositoryNotFoundError,
    ServiceError,
    ServiceException,
    SnapshotNotFound,
    SnapshotNotFoundError,
)
from backend.app.services.model_service import ModelService
from backend.app.services.model_version_service import ModelVersionService
from backend.app.services.prediction_explanation_service import (
    PredictionExplanationService,
)
from backend.app.services.prediction_service import PredictionService
from backend.app.services.repository_service import RepositoryService
from backend.app.services.snapshot_service import (
    RepositorySnapshotService,
    SnapshotService,
)

__all__ = [
    # Services
    "RepositoryService",
    "SnapshotService",
    "RepositorySnapshotService",
    "PredictionService",
    "PredictionExplanationService",
    "ModelVersionService",
    "ModelService",
    # Base Exception
    "ServiceError",
    "ServiceException",
    # Repository Exceptions
    "RepositoryAlreadyExists",
    "RepositoryAlreadyExistsError",
    "RepositoryNotFound",
    "RepositoryNotFoundError",
    # Snapshot Exceptions
    "SnapshotNotFound",
    "SnapshotNotFoundError",
    "DuplicateSnapshotError",
    # Prediction Exceptions
    "PredictionNotFound",
    "PredictionNotFoundError",
    "DuplicatePredictionError",
    "InvalidPredictionRequest",
    # Model Exceptions
    "ModelVersionNotFound",
    "ModelNotFound",
    "ModelNotFoundError",
    "ModelVersionAlreadyExists",
    "InvalidModelVersion",
    # Explanation Exceptions
    "PredictionExplanationNotFound",
    "PredictionExplanationAlreadyExists",
]
