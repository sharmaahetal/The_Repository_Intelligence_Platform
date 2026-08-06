"""API dependency injection module for Repository Intelligence Platform."""

from backend.app.services.model_version_service import ModelVersionService
from backend.app.services.prediction_explanation_service import (
    PredictionExplanationService,
)
from backend.app.services.prediction_service import PredictionService
from backend.app.services.repository_service import RepositoryService
from backend.app.services.snapshot_service import SnapshotService


def get_repository_service() -> RepositoryService:
    """Dependency provider returning RepositoryService instance."""
    return RepositoryService()


def get_snapshot_service() -> SnapshotService:
    """Dependency provider returning SnapshotService instance."""
    return SnapshotService()


def get_prediction_service() -> PredictionService:
    """Dependency provider returning PredictionService instance."""
    return PredictionService()


def get_prediction_explanation_service() -> PredictionExplanationService:
    """Dependency provider returning PredictionExplanationService instance."""
    return PredictionExplanationService()


def get_model_version_service() -> ModelVersionService:
    """Dependency provider returning ModelVersionService instance."""
    return ModelVersionService()
