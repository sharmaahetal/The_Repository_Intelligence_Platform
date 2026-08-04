from datetime import UTC, datetime

import pytest
from sqlalchemy.ext.asyncio import AsyncSession, async_sessionmaker

from backend.app.database import (
    Base,
    UnitOfWork,
    create_engine,
)


@pytest.mark.asyncio
async def test_unit_of_work_atomic_commit(tmp_path):
    """Verify UnitOfWork manages atomic multi-repository creation across a single AsyncSession and commits changes."""
    db_file = tmp_path / "test_uow_commit.db"
    test_engine = create_engine(f"sqlite+aiosqlite:///{db_file}")

    async with test_engine.begin() as conn:
        await conn.run_sync(Base.metadata.create_all)

    session_maker = async_sessionmaker(bind=test_engine, class_=AsyncSession, expire_on_commit=False)

    now = datetime.now(UTC)
    async with UnitOfWork(session_factory=session_maker) as uow:
        repo = await uow.repositories.create(
            github_repository_id=5001,
            owner="fastapi",
            name="fastapi",
            full_name="fastapi/fastapi",
            default_branch="main",
            language="Python",
        )
        snap = await uow.snapshots.create(
            repository_id=repo.id,
            snapshot_time=now,
            stars=75000,
            forks=6000,
        )
        model = await uow.model_versions.create(
            version="v1.0.0",
            algorithm="xgboost",
            training_dataset_hash="hash_uow",
            feature_schema_version="v1",
            accuracy=0.90,
            precision=0.88,
            recall=0.89,
            f1=0.88,
            auc=0.94,
            artifact_path="/artifacts/model_v1.pkl",
            trained_at=now,
        )
        pred = await uow.predictions.create(
            repository_snapshot_id=snap.id,
            model_version_id=model.id,
            predicted_growth=25.0,
            confidence=0.95,
            prediction_timestamp=now,
            prediction_horizon_days=30,
        )
        expl = await uow.explanations.create(
            prediction_id=pred.id,
            summary="Atomic transaction verification explanation",
            top_positive_features={"stars": 0.5},
            top_negative_features={"issues": -0.1},
            shap_json={"stars": 0.5, "issues": -0.1},
        )

        assert repo.id is not None
        assert snap.id is not None
        assert model.id is not None
        assert pred.id is not None
        assert expl.id is not None

    # Verify persistent state after context exit (commit)
    async with UnitOfWork(session_factory=session_maker) as uow:
        fetched_repo = await uow.repositories.get_by_full_name("fastapi/fastapi")
        assert fetched_repo is not None
        assert fetched_repo.github_repository_id == 5001

        fetched_snap = await uow.snapshots.get_latest_snapshot(fetched_repo.id)
        assert fetched_snap is not None
        assert fetched_snap.stars == 75000

        fetched_pred = await uow.predictions.latest_prediction(fetched_snap.id)
        assert fetched_pred is not None
        assert fetched_pred.confidence == 0.95

    await test_engine.dispose()


@pytest.mark.asyncio
async def test_unit_of_work_automatic_rollback_on_exception(tmp_path):
    """Verify UnitOfWork automatically rolls back all uncommitted mutations when an exception is raised."""
    db_file = tmp_path / "test_uow_rollback.db"
    test_engine = create_engine(f"sqlite+aiosqlite:///{db_file}")

    async with test_engine.begin() as conn:
        await conn.run_sync(Base.metadata.create_all)

    session_maker = async_sessionmaker(bind=test_engine, class_=AsyncSession, expire_on_commit=False)

    with pytest.raises(RuntimeError, match="Simulated service failure"):
        async with UnitOfWork(session_factory=session_maker) as uow:
            await uow.repositories.create(
                github_repository_id=6001,
                owner="golang",
                name="go",
                full_name="golang/go",
                default_branch="master",
                language="Go",
            )
            raise RuntimeError("Simulated service failure")

    # Verify no record was committed
    async with UnitOfWork(session_factory=session_maker) as uow:
        assert await uow.repositories.count() == 0
        assert await uow.repositories.get_by_full_name("golang/go") is None

    await test_engine.dispose()


@pytest.mark.asyncio
async def test_unit_of_work_unentered_property_access():
    """Verify accessing UnitOfWork properties prior to entering context raises RuntimeError."""
    uow = UnitOfWork()
    with pytest.raises(RuntimeError, match="UnitOfWork context has not been entered."):
        _ = uow.repositories
