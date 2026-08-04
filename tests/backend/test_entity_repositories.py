from datetime import UTC, datetime, timedelta

import pytest
from sqlalchemy.ext.asyncio import AsyncSession, async_sessionmaker

from backend.app.database import (
    Base,
    ModelVersionRepository,
    PredictionExplanationRepository,
    PredictionRepository,
    RepositoryRepository,
    SnapshotRepository,
    create_engine,
)


@pytest.mark.asyncio
async def test_entity_repositories_custom_methods(tmp_path):
    """Verify custom repository methods on Repository, Snapshot, Prediction, ModelVersion, and Explanation repositories."""
    db_file = tmp_path / "test_entities.db"
    test_engine = create_engine(f"sqlite+aiosqlite:///{db_file}")

    async with test_engine.begin() as conn:
        await conn.run_sync(Base.metadata.create_all)

    session_maker = async_sessionmaker(bind=test_engine, class_=AsyncSession, expire_on_commit=False)

    async with session_maker() as session:
        repo_dao = RepositoryRepository(session)
        snap_dao = SnapshotRepository(session)
        pred_dao = PredictionRepository(session)
        model_dao = ModelVersionRepository(session)
        expl_dao = PredictionExplanationRepository(session)

        # 1. Test RepositoryRepository
        r1 = await repo_dao.create(
            github_repository_id=9901,
            owner="facebook",
            name="react",
            full_name="facebook/react",
            default_branch="main",
            language="JavaScript",
            visibility="public",
            archived=False,
        )
        r2 = await repo_dao.create(
            github_repository_id=9902,
            owner="facebook",
            name="flux",
            full_name="facebook/flux",
            default_branch="main",
            language="JavaScript",
            visibility="public",
            archived=True,
        )
        assert r2.id is not None

        assert (await repo_dao.get_by_full_name("facebook/react")).id == r1.id
        assert (await repo_dao.get_by_github_id(9901)).id == r1.id
        assert await repo_dao.exists_by_full_name("facebook/react") is True
        assert await repo_dao.exists_by_full_name("nonexistent/repo") is False

        search_active = await repo_dao.search(owner="facebook", archived=False)
        assert len(search_active) == 1
        assert search_active[0].name == "react"

        # 2. Test SnapshotRepository
        now = datetime.now(UTC)
        t1 = now - timedelta(hours=2)
        t2 = now - timedelta(hours=1)

        s1 = await snap_dao.create(
            repository_id=r1.id,
            snapshot_time=t1,
            stars=100,
            forks=20,
        )
        s2 = await snap_dao.create(
            repository_id=r1.id,
            snapshot_time=t2,
            stars=150,
            forks=25,
        )

        latest_snap = await snap_dao.get_latest_snapshot(r1.id)
        assert latest_snap.id == s2.id

        history = await snap_dao.list_repository_history(r1.id)
        assert len(history) == 2
        assert history[0].id == s1.id
        assert history[1].id == s2.id

        snap_at = await snap_dao.get_snapshot_at(r1.id, t1)
        assert snap_at.id == s1.id

        assert await snap_dao.count_snapshots(r1.id) == 2

        # 3. Test ModelVersionRepository
        mv1 = await model_dao.create(
            version="v1.0.0",
            algorithm="xgboost",
            training_dataset_hash="hash123",
            feature_schema_version="v1",
            accuracy=0.85,
            precision=0.80,
            recall=0.82,
            f1=0.81,
            auc=0.90,
            artifact_path="/path/v1.pkl",
            trained_at=now - timedelta(days=1),
        )
        mv2 = await model_dao.create(
            version="v2.0.0",
            algorithm="lightgbm",
            training_dataset_hash="hash456",
            feature_schema_version="v2",
            accuracy=0.92,
            precision=0.88,
            recall=0.90,
            f1=0.89,
            auc=0.95,
            artifact_path="/path/v2.pkl",
            trained_at=now,
        )

        assert (await model_dao.latest_version()).id == mv2.id
        assert (await model_dao.get_version("v1.0.0")).id == mv1.id

        best_f1 = await model_dao.best_model(metric="f1")
        assert best_f1.id == mv2.id

        with pytest.raises(ValueError, match="Invalid metric"):
            await model_dao.best_model(metric="invalid_metric")

        versions = await model_dao.list_versions()
        assert len(versions) == 2
        assert versions[0].id == mv2.id

        # 4. Test PredictionRepository
        p1 = await pred_dao.create(
            repository_snapshot_id=s2.id,
            model_version_id=mv2.id,
            predicted_growth=12.5,
            confidence=0.91,
            prediction_timestamp=now,
            prediction_horizon_days=30,
        )

        assert (await pred_dao.latest_prediction(s2.id)).id == p1.id
        assert len(await pred_dao.list_predictions(repository_snapshot_id=s2.id)) == 1
        assert (await pred_dao.latest_by_model(mv2.id)).id == p1.id
        assert len(await pred_dao.prediction_history(model_version_id=mv2.id)) == 1
        assert len(await pred_dao.high_confidence_predictions(minimum_confidence=0.90)) == 1
        assert len(await pred_dao.high_confidence_predictions(minimum_confidence=0.95)) == 0

        with pytest.raises(ValueError, match="minimum_confidence must be between 0.0 and 1.0"):
            await pred_dao.high_confidence_predictions(minimum_confidence=1.5)

        # 5. Test PredictionExplanationRepository
        e1 = await expl_dao.create(
            prediction_id=p1.id,
            summary="High commit velocity driven growth.",
            top_positive_features={"stars_growth": 0.45},
            top_negative_features={"open_issues": -0.05},
            shap_json={"stars_growth": 0.45, "open_issues": -0.05},
        )

        assert (await expl_dao.get_for_prediction(p1.id)).id == e1.id
        assert await expl_dao.exists_for_prediction(p1.id) is True
        assert await expl_dao.delete_for_prediction(p1.id) is True
        assert await expl_dao.exists_for_prediction(p1.id) is False

        # Test SnapshotRepository delete_before
        target_repo_id = r1.id
        session.expire_all()
        deleted_snapshots = await snap_dao.delete_before(t2)
        assert deleted_snapshots == 1
        assert await snap_dao.count_snapshots(target_repo_id) == 1

    await test_engine.dispose()
