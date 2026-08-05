from datetime import UTC, datetime

import pytest
from pydantic import ValidationError

from backend.app.database.models.explanation import PredictionExplanation
from backend.app.database.models.model_version import ModelVersion
from backend.app.database.models.prediction import Prediction
from backend.app.database.models.repository import Repository
from backend.app.database.models.snapshot import RepositorySnapshot
from backend.app.schemas import (
    BaseSchema,
    ModelVersionCreate,
    ModelVersionResponse,
    ModelVersionUpdate,
    PredictionCreate,
    PredictionExplanationCreate,
    PredictionExplanationResponse,
    PredictionExplanationUpdate,
    PredictionResponse,
    PredictionUpdate,
    RepositoryCreate,
    RepositoryResponse,
    RepositorySearch,
    RepositorySnapshotCreate,
    RepositorySnapshotResponse,
    RepositorySnapshotUpdate,
    RepositoryUpdate,
)


class SampleItemSchema(BaseSchema):
    name: str
    count: int


def test_base_schema_attributes():
    """Verify BaseSchema configuration: attribute population and extra field forbidding."""
    item = SampleItemSchema(name="repo", count=10)
    assert item.name == "repo"
    assert item.count == 10

    # Extra fields are forbidden
    with pytest.raises(ValidationError):
        SampleItemSchema(name="repo", count=10, extra_field="forbidden")  # type: ignore[call-arg]


def test_repository_schemas():
    """Verify Repository DTO schemas instantiation, defaults, and ORM conversion."""
    create_dto = RepositoryCreate(
        github_repository_id=12345,
        owner="octocat",
        name="Hello-World",
        full_name="octocat/Hello-World",
        language="Python",
    )
    assert create_dto.github_repository_id == 12345
    assert create_dto.default_branch == "main"
    assert create_dto.visibility == "public"

    update_dto = RepositoryUpdate(language="TypeScript", default_branch="develop")
    assert update_dto.language == "TypeScript"
    assert update_dto.owner is None

    search_dto = RepositorySearch(owner="octocat", language="Python")
    assert search_dto.owner == "octocat"

    # ORM conversion for RepositoryResponse
    now = datetime.now(UTC)
    repo_orm = Repository(
        id=1,
        github_repository_id=12345,
        owner="octocat",
        name="Hello-World",
        full_name="octocat/Hello-World",
        default_branch="main",
        language="Python",
        visibility="public",
        archived=False,
        fork=False,
        created_at=now,
        updated_at=now,
    )

    response_dto = RepositoryResponse.model_validate(repo_orm)
    assert response_dto.id == 1
    assert response_dto.full_name == "octocat/Hello-World"
    assert response_dto.created_at == now


def test_repository_snapshot_schemas():
    """Verify RepositorySnapshot DTO schemas instantiation and ORM validation."""
    now = datetime.now(UTC)
    create_dto = RepositorySnapshotCreate(
        repository_id=1,
        snapshot_time=now,
        stars=100,
        forks=20,
        watchers=100,
        open_issues=5,
        subscribers=15,
        network_count=20,
        size_kb=1024,
        license="MIT",
    )
    assert create_dto.stars == 100
    assert create_dto.repository_id == 1

    update_dto = RepositorySnapshotUpdate(stars=120)
    assert update_dto.stars == 120
    assert update_dto.forks is None

    snap_orm = RepositorySnapshot(
        id=10,
        repository_id=1,
        snapshot_time=now,
        stars=100,
        forks=20,
        watchers=100,
        open_issues=5,
        subscribers=15,
        network_count=20,
        size_kb=1024,
        license="MIT",
        default_branch="main",
        collected_at=now,
        created_at=now,
        updated_at=now,
    )

    response_dto = RepositorySnapshotResponse.model_validate(snap_orm)
    assert response_dto.id == 10
    assert response_dto.stars == 100
    assert response_dto.license == "MIT"


def test_prediction_schemas():
    """Verify Prediction DTO schemas instantiation, defaults, and ORM conversion."""
    now = datetime.now(UTC)
    create_dto = PredictionCreate(
        repository_snapshot_id=10,
        model_version_id=2,
        predicted_growth=15.5,
        confidence=0.92,
        prediction_timestamp=now,
    )
    assert create_dto.repository_snapshot_id == 10
    assert create_dto.model_version_id == 2
    assert create_dto.prediction_horizon_days == 30

    update_dto = PredictionUpdate(confidence=0.95)
    assert update_dto.confidence == 0.95
    assert update_dto.predicted_growth is None

    pred_orm = Prediction(
        id=100,
        repository_snapshot_id=10,
        model_version_id=2,
        predicted_growth=15.5,
        confidence=0.92,
        prediction_timestamp=now,
        prediction_horizon_days=30,
        created_at=now,
        updated_at=now,
    )

    response_dto = PredictionResponse.model_validate(pred_orm)
    assert response_dto.id == 100
    assert response_dto.predicted_growth == 15.5
    assert response_dto.confidence == 0.92


def test_model_version_schemas():
    """Verify ModelVersion DTO schemas instantiation, defaults, and ORM conversion."""
    now = datetime.now(UTC)
    create_dto = ModelVersionCreate(
        version="v1.0.0",
        algorithm="xgboost",
        training_dataset_hash="hash123",
        feature_schema_version="v1",
        accuracy=0.88,
        precision=0.87,
        recall=0.89,
        f1=0.88,
        auc=0.91,
        artifact_path="/models/v1.0.0.pkl",
        trained_at=now,
    )
    assert create_dto.version == "v1.0.0"
    assert create_dto.algorithm == "xgboost"
    assert create_dto.f1 == 0.88

    update_dto = ModelVersionUpdate(accuracy=0.90)
    assert update_dto.accuracy == 0.90
    assert update_dto.version is None

    model_orm = ModelVersion(
        id=5,
        version="v1.0.0",
        algorithm="xgboost",
        training_dataset_hash="hash123",
        feature_schema_version="v1",
        accuracy=0.88,
        precision=0.87,
        recall=0.89,
        f1=0.88,
        auc=0.91,
        artifact_path="/models/v1.0.0.pkl",
        trained_at=now,
        training_duration_seconds=12.5,
        created_at=now,
        updated_at=now,
    )

    response_dto = ModelVersionResponse.model_validate(model_orm)
    assert response_dto.id == 5
    assert response_dto.version == "v1.0.0"
    assert response_dto.training_duration_seconds == 12.5


def test_prediction_explanation_schemas():
    """Verify PredictionExplanation DTO schemas instantiation and ORM conversion."""
    now = datetime.now(UTC)
    create_dto = PredictionExplanationCreate(
        prediction_id=100,
        summary="Recent increase in star velocity driving growth.",
        top_positive_features={"star_growth_30d": 0.85},
        top_negative_features={"open_issue_ratio": -0.12},
        shap_json={"star_growth_30d": 0.85, "open_issue_ratio": -0.12},
    )
    assert create_dto.prediction_id == 100
    assert create_dto.summary == "Recent increase in star velocity driving growth."

    update_dto = PredictionExplanationUpdate(summary="Updated summary.")
    assert update_dto.summary == "Updated summary."
    assert update_dto.top_positive_features is None

    exp_orm = PredictionExplanation(
        id=50,
        prediction_id=100,
        summary="Recent increase in star velocity driving growth.",
        top_positive_features={"star_growth_30d": 0.85},
        top_negative_features={"open_issue_ratio": -0.12},
        shap_json={"star_growth_30d": 0.85, "open_issue_ratio": -0.12},
        generated_at=now,
        created_at=now,
        updated_at=now,
    )

    response_dto = PredictionExplanationResponse.model_validate(exp_orm)
    assert response_dto.id == 50
    assert response_dto.prediction_id == 100
    assert response_dto.top_positive_features == {"star_growth_30d": 0.85}
