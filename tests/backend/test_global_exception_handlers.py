import pytest
from fastapi.testclient import TestClient

from backend.app.api.deps import get_repository_service
from backend.app.main import app
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
    SnapshotNotFound,
)


class RaisingRepositoryService:
    def __init__(self, exc_to_raise: Exception) -> None:
        self.exc_to_raise = exc_to_raise

    async def get_repository(self, repository_id: int):
        raise self.exc_to_raise


@pytest.mark.parametrize(
    "exception_instance,expected_status,expected_type",
    [
        (RepositoryNotFound(42), 404, "RepositoryNotFound"),
        (SnapshotNotFound(10), 404, "SnapshotNotFound"),
        (PredictionNotFound(99), 404, "PredictionNotFound"),
        (ModelVersionNotFound("v1.0"), 404, "ModelVersionNotFound"),
        (PredictionExplanationNotFound(5), 404, "PredictionExplanationNotFound"),
        (RepositoryAlreadyExists("octocat/hello"), 409, "RepositoryAlreadyExists"),
        (DuplicateSnapshotError(1, "2026-01-01"), 409, "DuplicateSnapshotError"),
        (DuplicatePredictionError("snap_1_model_1"), 409, "DuplicatePredictionError"),
        (ModelVersionAlreadyExists("v1.0"), 409, "ModelVersionAlreadyExists"),
        (PredictionExplanationAlreadyExists(5), 409, "PredictionExplanationAlreadyExists"),
        (InvalidPredictionRequest("Horizon must be positive"), 400, "InvalidPredictionRequest"),
        (InvalidModelVersion("Missing artifact path"), 400, "InvalidModelVersion"),
    ],
)
def test_global_exception_handlers_formatting(exception_instance, expected_status, expected_type):
    """Verify that domain exceptions are mapped to the correct HTTP status code and JSON error payload."""
    app.dependency_overrides[get_repository_service] = lambda: RaisingRepositoryService(exception_instance)
    client = TestClient(app, raise_server_exceptions=False)

    try:
        response = client.get("/repositories/42")
        assert response.status_code == expected_status
        data = response.json()
        assert "error" in data
        assert data["error"]["type"] == expected_type
        assert "message" in data["error"]
        assert len(data["error"]["message"]) > 0
    finally:
        app.dependency_overrides.clear()
