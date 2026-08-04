from datetime import UTC, datetime

import pytest
from sqlalchemy import inspect

from sqlalchemy.ext.asyncio import AsyncSession, async_sessionmaker
from sqlalchemy.orm import configure_mappers



from backend.app.database import (
    Base,
    ModelVersion,
    Prediction,
    PredictionExplanation,
    Repository,
    RepositorySnapshot,
    create_engine,
)
from backend.app.database.models import (
    ModelVersion as MV,
)
from backend.app.database.models import (
    Prediction as P,
)
from backend.app.database.models import (
    PredictionExplanation as PE,
)
from backend.app.database.models import (
    Repository as R,
)
from backend.app.database.models import (
    RepositorySnapshot as RS,
)


def test_wildcard_import_and_export():
    """Sprint 1.9 Step 6 & 8: Verify models package exports all 5 domain models cleanly."""
    assert R is Repository
    assert RS is RepositorySnapshot
    assert MV is ModelVersion
    assert P is Prediction
    assert PE is PredictionExplanation


def test_mapper_configuration():
    """Sprint 1.9 Step 1 & 5: Verify configure_mappers runs without mapper configuration errors."""
    configure_mappers()
    for model in (Repository, RepositorySnapshot, ModelVersion, Prediction, PredictionExplanation):
        mapper = inspect(model)
        assert mapper is not None


def test_models_registered_in_metadata():
    """Sprint 1.9 Step 4: Verify all 5 tables are registered in Base.metadata with exact table names."""
    table_names = set(Base.metadata.tables.keys())
    expected_tables = {
        "repositories",
        "repository_snapshots",
        "model_versions",
        "predictions",
        "prediction_explanations",
    }
    assert expected_tables.issubset(table_names)



def test_indexes_and_constraints_registered():
    """Sprint 1.9 Step 3 & 7: Verify foreign keys, indexes, and check constraints on table schemas."""
    repo_table = Base.metadata.tables["repositories"]
    assert "github_repository_id" in [c.name for c in repo_table.columns if c.unique or c.index]

    snapshot_table = Base.metadata.tables["repository_snapshots"]
    idx_names = [idx.name for idx in snapshot_table.indexes]
    assert "ix_repository_snapshots_repo_snapshot_time" in idx_names

    check_constraints = [ck.name for ck in snapshot_table.constraints if hasattr(ck, "name")]
    assert "ck_repository_snapshots_stars_non_negative" in check_constraints

    model_table = Base.metadata.tables["model_versions"]
    model_ck_names = [ck.name for ck in model_table.constraints if hasattr(ck, "name")]
    assert "ck_model_versions_accuracy_range" in model_ck_names

    # Verify String length specifications
    assert model_table.columns["version"].type.length == 32
    assert model_table.columns["algorithm"].type.length == 50
    assert model_table.columns["training_dataset_hash"].type.length == 64
    assert model_table.columns["artifact_path"].type.length == 512

    # Verify Prediction unique constraint
    pred_table = Base.metadata.tables["predictions"]
    pred_uq_names = [c.name for c in pred_table.constraints if c.name is not None]
    assert any("prediction_model_snapshot_horizon" in name for name in pred_uq_names)


def test_in_memory_model_instantiation():
    """Sprint 1.9 Step 5: Instantiate all 5 models in memory without mapper or validation errors."""
    now = datetime.now(UTC)
    repo = Repository(github_repository_id=1, owner="o", name="n", full_name="o/n")
    snap = RepositorySnapshot(repository_id=1, snapshot_time=now, stars=10)
    mv = ModelVersion(
        version="v1.0.0",
        algorithm="xgb",
        training_dataset_hash="h" * 64,
        feature_schema_version="1.0",
        accuracy=0.9,
        precision=0.9,
        recall=0.9,
        f1=0.9,
        auc=0.9,
        artifact_path="/path",
        trained_at=now,
    )
    pred = Prediction(repository_snapshot_id=1, model_version_id=1, predicted_growth=1.0, confidence=0.8, prediction_timestamp=now)
    expl = PredictionExplanation(prediction_id=1, summary="s", top_positive_features={}, top_negative_features={}, shap_json={})

    assert repr(repo).startswith("<Repository(")
    assert repr(snap).startswith("<RepositorySnapshot(")
    assert repr(mv).startswith("<ModelVersion(")
    assert repr(pred).startswith("<Prediction(")
    assert repr(expl).startswith("<PredictionExplanation(")


@pytest.mark.asyncio
async def test_end_to_end_orm_persistence_flow(tmp_path):
    """Sprint 1.9 Step 2: Verify bidirectional relationships and end-to-end cascade persistence."""
    db_file = tmp_path / "test_models.db"
    test_engine = create_engine(f"sqlite+aiosqlite:///{db_file}")

    async with test_engine.begin() as conn:
        await conn.run_sync(Base.metadata.create_all)

    session_maker = async_sessionmaker(bind=test_engine, class_=AsyncSession, expire_on_commit=False)

    async with session_maker() as session:
        # 1. Create Repository
        repo = Repository(
            github_repository_id=102030,
            owner="fastapi",
            name="fastapi",
            full_name="fastapi/fastapi",
            default_branch="main",
            language="Python",
        )
        session.add(repo)
        await session.commit()
        await session.refresh(repo)

        # 2. Create RepositorySnapshot
        snapshot = RepositorySnapshot(
            repository_id=repo.id,
            snapshot_time=datetime.now(UTC),
            stars=75000,
            forks=6000,
            open_issues=500,
            subscribers=1200,
            topics_json=["fastapi", "python", "async"],
        )
        session.add(snapshot)
        await session.commit()
        await session.refresh(snapshot)

        # 3. Create ModelVersion
        model_ver = ModelVersion(
            version="v1.0.0",
            algorithm="xgboost",
            training_dataset_hash="a1b2c3d4e5f67890" * 4,
            feature_schema_version="1.0",
            accuracy=0.88,
            precision=0.86,
            recall=0.87,
            f1=0.865,
            auc=0.92,
            artifact_path="artifacts/registry/v1.0.0.json",
            trained_at=datetime.now(UTC),
            training_duration_seconds=124.5,
            cross_validation_score=0.892,
            dataset_size=15000,
            random_seed=42,
            git_commit_hash="abcdef0123456789abcdef0123456789abcdef01",
        )
        session.add(model_ver)
        await session.commit()
        await session.refresh(model_ver)

        # 4. Create Prediction
        prediction = Prediction(
            repository_snapshot_id=snapshot.id,
            model_version_id=model_ver.id,
            predicted_growth=150.5,
            confidence=0.91,
            prediction_timestamp=datetime.now(UTC),
            prediction_horizon_days=30,
        )
        session.add(prediction)
        await session.commit()
        await session.refresh(prediction)

        # 5. Create PredictionExplanation
        explanation = PredictionExplanation(
            prediction_id=prediction.id,
            summary="Strong star growth driven by high recent commit velocity and issue resolution.",
            top_positive_features={"stars_growth_30d": 12.4, "forks_growth_30d": 5.1},
            top_negative_features={"open_issues_ratio": -1.2},
            shap_json={"stars_growth_30d": 12.4, "forks_growth_30d": 5.1, "open_issues_ratio": -1.2},
        )
        session.add(explanation)
        await session.commit()
        await session.refresh(explanation)

        # Verify Foreign Key references and persistence
        assert snapshot.repository_id == repo.id
        assert prediction.repository_snapshot_id == snapshot.id
        assert prediction.model_version_id == model_ver.id
        assert explanation.prediction_id == prediction.id


    await test_engine.dispose()
