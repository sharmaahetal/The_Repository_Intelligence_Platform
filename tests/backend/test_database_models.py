from datetime import UTC, datetime

import pytest
from sqlalchemy.ext.asyncio import AsyncSession, async_sessionmaker

from backend.app.database import (
    Base,
    ModelVersion,
    Prediction,
    PredictionExplanation,
    Repository,
    RepositorySnapshot,
    create_engine,
)


def test_models_registered_in_metadata():
    """Verify all 5 tables are registered in Base.metadata with correct table names."""
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
    """Verify indexes and check constraints are defined on table schemas."""
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


@pytest.mark.asyncio
async def test_end_to_end_orm_persistence_flow(tmp_path):
    """Verify full end-to-end cascade persistence across all 5 entities."""
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
        assert repo.id is not None

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
        assert snapshot.id is not None
        assert snapshot.repository_id == repo.id

        # 3. Create ModelVersion
        model_ver = ModelVersion(
            version="v1.0.0",
            algorithm="xgboost",
            training_dataset_hash="a1b2c3d4e5f67890",
            feature_schema_version="1.0",
            accuracy=0.88,
            precision=0.86,
            recall=0.87,
            f1=0.865,
            auc=0.92,
            artifact_path="artifacts/registry/v1.0.0.json",
            trained_at=datetime.now(UTC),
        )
        session.add(model_ver)
        await session.commit()
        await session.refresh(model_ver)
        assert model_ver.id is not None

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
        assert prediction.id is not None

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
        assert explanation.id is not None
        assert explanation.prediction_id == prediction.id

    await test_engine.dispose()
