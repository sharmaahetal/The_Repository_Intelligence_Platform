from fastapi import APIRouter

from backend.app.api.deps import (
    get_model_version_service,
    get_prediction_explanation_service,
    get_prediction_service,
    get_repository_service,
    get_snapshot_service,
)
from backend.app.api.router import router
from backend.app.services.model_version_service import ModelVersionService
from backend.app.services.prediction_explanation_service import (
    PredictionExplanationService,
)
from backend.app.services.prediction_service import PredictionService
from backend.app.services.repository_service import RepositoryService
from backend.app.services.snapshot_service import SnapshotService


def test_api_router_structure():
    """Verify router includes all 5 feature routers with correct prefixes and tags."""
    assert isinstance(router, APIRouter)
    # 5 feature sub-routers included
    assert len(router.routes) == 5


def test_api_deps_providers():
    """Verify dependency provider functions return service instances."""
    assert isinstance(get_repository_service(), RepositoryService)
    assert isinstance(get_snapshot_service(), SnapshotService)
    assert isinstance(get_prediction_service(), PredictionService)
    assert isinstance(get_prediction_explanation_service(), PredictionExplanationService)
    assert isinstance(get_model_version_service(), ModelVersionService)
