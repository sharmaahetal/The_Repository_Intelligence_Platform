from datetime import UTC, datetime, timedelta

import pytest
from sqlalchemy.ext.asyncio import AsyncSession, async_sessionmaker

from backend.app.database import Base, create_engine
from backend.app.database.unit_of_work import UnitOfWork
from backend.app.services import (
    DuplicateSnapshotError,
    InvalidPredictionRequest,
    ModelNotFound,
    ModelService,
    ModelVersionAlreadyExists,
    ModelVersionNotFound,
    PredictionService,
    RepositoryAlreadyExists,
    RepositoryNotFound,
    RepositoryService,
    SnapshotNotFound,
    SnapshotService,
)


@pytest.fixture
async def test_session_factory(tmp_path, monkeypatch):
    """Fixture initializing in-memory SQLite database and returning an async_sessionmaker bound to it."""
    db_file = tmp_path / "test_services.db"
    test_engine = create_engine(f"sqlite+aiosqlite:///{db_file}")

    async with test_engine.begin() as conn:
        await conn.run_sync(Base.metadata.create_all)

    session_maker = async_sessionmaker(bind=test_engine, class_=AsyncSession, expire_on_commit=False)

    # Monkeypatch session factory for default UnitOfWork constructor calls
    monkeypatch.setattr("backend.app.database.unit_of_work.AsyncSessionLocal", session_maker)

    yield session_maker

    await test_engine.dispose()


@pytest.mark.asyncio
async def test_repository_service_lifecycle(test_session_factory):
    """Verify RepositoryService business rules: creation, uniqueness enforcement, search, update, and delete."""
    uow = UnitOfWork(session_factory=test_session_factory)
    repo_service = RepositoryService(uow=uow)

    # Create repository
    r1 = await repo_service.create_repository(
        owner="django",
        name="django",
        full_name="django/django",
        github_repository_id=8801,
        language="Python",
    )
    assert r1.id is not None
    assert r1.full_name == "django/django"

    # Duplicate full_name rejected
    with pytest.raises(RepositoryAlreadyExists, match="Repository 'django/django' already exists."):
        await repo_service.create_repository(
            owner="django",
            name="django",
            full_name="django/django",
            github_repository_id=8802,
        )

    # Duplicate github_repository_id rejected
    with pytest.raises(RepositoryAlreadyExists, match="Repository '8801' already exists."):
        await repo_service.create_repository(
            owner="django-fork",
            name="django",
            full_name="other/django",
            github_repository_id=8801,
        )

    # Get existing repository
    fetched = await repo_service.get_repository(repository_id=r1.id)
    assert fetched.full_name == "django/django"

    # Non-existent repository raises RepositoryNotFound
    with pytest.raises(RepositoryNotFound, match="Repository '99999' was not found."):
        await repo_service.get_repository(repository_id=99999)

    # Search
    results = await repo_service.search(owner="django")
    assert len(results) == 1

    # Update
    updated = await repo_service.update(r1.id, default_branch="master")
    assert updated.default_branch == "master"

    # Delete
    assert await repo_service.delete(r1.id) is True
    with pytest.raises(RepositoryNotFound):
        await repo_service.get_repository(repository_id=r1.id)


@pytest.mark.asyncio
async def test_snapshot_service_lifecycle(test_session_factory):
    """Verify SnapshotService business rules: invalid repo protection, duplicate timestamp rejection, history listing."""
    repo_service = RepositoryService()
    snap_service = SnapshotService()

    repo = await repo_service.create_repository(
        owner="pallets",
        name="flask",
        full_name="pallets/flask",
        github_repository_id=7701,
        language="Python",
    )

    now = datetime.now(UTC)
    s1 = await snap_service.create_snapshot(
        repository_id=repo.id,
        snapshot_time=now,
        stars=60000,
        forks=15000,
    )
    assert s1.id is not None

    # Creating snapshot for non-existent repo raises RepositoryNotFound
    with pytest.raises(RepositoryNotFound, match="Repository '9999' was not found."):
        await snap_service.create_snapshot(
            repository_id=9999,
            snapshot_time=now,
        )

    # Duplicate snapshot at exact timestamp raises DuplicateSnapshotError
    with pytest.raises(DuplicateSnapshotError, match=f"Snapshot for repository '{repo.id}'"):
        await snap_service.create_snapshot(
            repository_id=repo.id,
            snapshot_time=now,
        )

    # Get latest snapshot
    latest = await snap_service.get_latest_snapshot(repo.id)
    assert latest.id == s1.id

    # History listing
    history = await snap_service.list_history(repo.id)
    assert len(history) == 1

    # Delete history before future timestamp
    deleted_count = await snap_service.delete_history_before(repo.id, now + timedelta(hours=1))
    assert deleted_count == 1


@pytest.mark.asyncio
async def test_model_service_lifecycle(test_session_factory):
    """Verify ModelService business rules: model registration, version uniqueness, latest/best lookup."""
    model_service = ModelService()
    now = datetime.now(UTC)

    m1 = await model_service.register_model(
        version="v1.0.0",
        algorithm="random_forest",
        training_dataset_hash="hash_rf",
        feature_schema_version="v1",
        accuracy=0.82,
        precision=0.80,
        recall=0.81,
        f1=0.80,
        auc=0.88,
        artifact_path="/models/v1.pkl",
        trained_at=now - timedelta(days=1),
    )
    assert m1.id is not None

    # Registering duplicate version raises ModelVersionAlreadyExists
    with pytest.raises(ModelVersionAlreadyExists, match="Model version 'v1.0.0' already exists."):
        await model_service.register_model(
            version="v1.0.0",
            algorithm="random_forest",
            training_dataset_hash="hash_rf",
            feature_schema_version="v1",
            accuracy=0.82,
            precision=0.80,
            recall=0.81,
            f1=0.80,
            auc=0.88,
            artifact_path="/models/v1.pkl",
        )

    m2 = await model_service.register_model(
        version="v2.0.0",
        algorithm="xgboost",
        training_dataset_hash="hash_xgb",
        feature_schema_version="v2",
        accuracy=0.94,
        precision=0.92,
        recall=0.93,
        f1=0.92,
        auc=0.97,
        artifact_path="/models/v2.pkl",
        trained_at=now,
    )

    # Latest model
    latest = await model_service.get_latest_model()
    assert latest.id == m2.id

    # Best model by metric
    best_auc = await model_service.get_best_model(metric="auc")
    assert best_auc.id == m2.id

    # Get model by version
    by_version = await model_service.get_model_by_version("v1.0.0")
    assert by_version.id == m1.id

    # Non-existent version raises ModelVersionNotFound
    with pytest.raises(ModelVersionNotFound, match="Model version 'v9.9.9' was not found."):
        await model_service.get_model_by_version("v9.9.9")


@pytest.mark.asyncio
async def test_prediction_service_lifecycle(test_session_factory):
    """Verify PredictionService business rules: prediction creation, SHAP explanation creation, snapshot/model validation."""
    repo_service = RepositoryService()
    snap_service = SnapshotService()
    model_service = ModelService()
    pred_service = PredictionService()

    now = datetime.now(UTC)
    repo = await repo_service.create_repository(
        owner="psf",
        name="requests",
        full_name="psf/requests",
        github_repository_id=6601,
    )
    snap = await snap_service.create_snapshot(repository_id=repo.id, snapshot_time=now)
    model = await model_service.register_model(
        version="v1.0.0",
        algorithm="lightgbm",
        training_dataset_hash="hash_lgb",
        feature_schema_version="v1",
        accuracy=0.88,
        precision=0.85,
        recall=0.86,
        f1=0.85,
        auc=0.91,
        artifact_path="/models/lgb.pkl",
    )

    # Invalid prediction horizon days raises InvalidPredictionRequest
    with pytest.raises(InvalidPredictionRequest, match="prediction_horizon_days must be greater than 0"):
        await pred_service.create_prediction(
            repository_snapshot_id=snap.id,
            model_version_id=model.id,
            predicted_growth=15.0,
            confidence=0.90,
            prediction_horizon_days=0,
        )

    # Invalid confidence raises InvalidPredictionRequest
    with pytest.raises(InvalidPredictionRequest, match="confidence must be between 0.0 and 1.0"):
        await pred_service.create_prediction(
            repository_snapshot_id=snap.id,
            model_version_id=model.id,
            predicted_growth=15.0,
            confidence=1.5,
        )

    # Invalid snapshot ID raises SnapshotNotFound
    with pytest.raises(SnapshotNotFound, match="Snapshot '9999' was not found."):
        await pred_service.create_prediction(
            repository_snapshot_id=9999,
            model_version_id=model.id,
            predicted_growth=15.0,
            confidence=0.90,
        )

    # Invalid model version ID raises ModelNotFound / ModelVersionNotFound
    with pytest.raises(ModelNotFound, match="Model version '9999' was not found."):
        await pred_service.create_prediction(
            repository_snapshot_id=snap.id,
            model_version_id=9999,
            predicted_growth=15.0,
            confidence=0.90,
        )

    # Create valid prediction with explanation
    pred = await pred_service.create_prediction(
        repository_snapshot_id=snap.id,
        model_version_id=model.id,
        predicted_growth=18.5,
        confidence=0.93,
        explanation_summary="Strong star velocity",
        top_positive_features={"stars_growth": 0.4},
        shap_json={"stars_growth": 0.4},
    )
    assert pred.id is not None
    assert pred.predicted_growth == 18.5

    # Retrieve latest prediction
    latest_pred = await pred_service.get_latest_prediction(snap.id)
    assert latest_pred.id == pred.id

    # High confidence predictions
    high_conf = await pred_service.get_high_confidence_predictions(minimum_confidence=0.90)
    assert len(high_conf) == 1

    # Invalid minimum confidence raises InvalidPredictionRequest
    with pytest.raises(InvalidPredictionRequest):
        await pred_service.get_high_confidence_predictions(minimum_confidence=-0.5)
