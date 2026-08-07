from datetime import UTC, datetime

import pytest
from fastapi.testclient import TestClient
from sqlalchemy.ext.asyncio import AsyncSession, async_sessionmaker

from backend.app.database import Base, create_engine
from backend.app.main import app


@pytest.fixture
async def test_session_factory(tmp_path, monkeypatch):
    """Fixture initializing a SQLite database with all tables and monkeypatching UnitOfWork."""
    db_file = tmp_path / "smoke_test.db"
    test_engine = create_engine(f"sqlite+aiosqlite:///{db_file}")

    async with test_engine.begin() as conn:
        await conn.run_sync(Base.metadata.create_all)

    session_maker = async_sessionmaker(bind=test_engine, class_=AsyncSession, expire_on_commit=False)
    monkeypatch.setattr("backend.app.database.unit_of_work.AsyncSessionLocal", session_maker)

    yield session_maker

    await test_engine.dispose()


@pytest.mark.asyncio
async def test_e2e_smoke_test_complete_flow(test_session_factory):
    """Smoke test validating full end-to-end creation flow across all entities and API endpoints:

    Repository -> Snapshot -> ModelVersion -> Prediction -> Explanation.
    """
    client = TestClient(app, raise_server_exceptions=False)
    now_iso = datetime.now(UTC).isoformat()

    # 1. Create Repository
    repo_payload = {
        "github_repository_id": 999001,
        "owner": "deepmind",
        "name": "antigravity-core",
        "full_name": "deepmind/antigravity-core",
        "default_branch": "main",
        "language": "Python",
        "visibility": "public",
        "archived": False,
        "fork": False,
    }
    repo_res = client.post("/repositories", json=repo_payload)
    assert repo_res.status_code == 201, f"Create Repository failed: {repo_res.text}"
    repo_data = repo_res.json()
    repo_id = repo_data["id"]
    assert repo_data["owner"] == "deepmind"
    assert repo_data["name"] == "antigravity-core"

    # 2. Create Repository Snapshot
    snapshot_payload = {
        "repository_id": repo_id,
        "snapshot_time": now_iso,
        "stars": 15000,
        "forks": 1200,
        "open_issues": 45,
        "watchers": 15000,
        "subscribers": 350,
        "network_count": 1200,
        "size_kb": 51200,
        "license": "Apache-2.0",
        "default_branch": "main",
    }
    snapshot_res = client.post("/snapshots", json=snapshot_payload)
    assert snapshot_res.status_code == 201, f"Create Snapshot failed: {snapshot_res.text}"
    snapshot_data = snapshot_res.json()
    snapshot_id = snapshot_data["id"]
    assert snapshot_data["repository_id"] == repo_id
    assert snapshot_data["stars"] == 15000

    # 3. Register Model Version
    model_payload = {
        "version": "1.0.0-smoke",
        "algorithm": "GradientBoostingRegressor",
        "training_dataset_hash": "e3b0c44298fc1c149afbf4c8996fb92427ae41e4649b934ca495991b7852b855",
        "feature_schema_version": "v1",
        "accuracy": 0.942,
        "precision": 0.931,
        "recall": 0.925,
        "f1": 0.928,
        "auc": 0.965,
        "artifact_path": "s3://models/antigravity-gbr-v1.tar.gz",
        "trained_at": now_iso,
    }
    model_res = client.post("/model-versions", json=model_payload)
    assert model_res.status_code == 201, f"Register Model failed: {model_res.text}"
    model_data = model_res.json()
    model_id = model_data["id"]
    assert model_data["version"] == "1.0.0-smoke"

    # 4. Create Prediction
    prediction_payload = {
        "repository_snapshot_id": snapshot_id,
        "model_version_id": model_id,
        "predicted_growth": 28.5,
        "confidence": 0.915,
        "prediction_timestamp": now_iso,
        "prediction_horizon_days": 30,
    }
    pred_res = client.post("/predictions", json=prediction_payload)
    assert pred_res.status_code == 201, f"Create Prediction failed: {pred_res.text}"
    pred_data = pred_res.json()
    prediction_id = pred_data["id"]
    assert pred_data["repository_snapshot_id"] == snapshot_id
    assert pred_data["model_version_id"] == model_id
    assert pred_data["predicted_growth"] == 28.5

    # 5. Create Prediction Explanation
    explanation_payload = {
        "prediction_id": prediction_id,
        "summary": "Growth driven by star momentum and active contributor commits",
        "top_positive_features": {"stars_30d_growth": 0.45, "commit_frequency": 0.30},
        "top_negative_features": {"open_issues_count": 0.05},
        "shap_json": {"base_value": 15.0, "values": [0.45, 0.30, -0.05]},
    }
    expl_res = client.post("/explanations", json=explanation_payload)
    assert expl_res.status_code == 201, f"Create Explanation failed: {expl_res.text}"
    expl_data = expl_res.json()
    explanation_id = expl_data["id"]
    assert expl_data["prediction_id"] == prediction_id

    # 6. Verify Read endpoints across entire chain
    fetch_repo = client.get(f"/repositories/{repo_id}")
    assert fetch_repo.status_code == 200
    assert fetch_repo.json()["full_name"] == "deepmind/antigravity-core"

    fetch_snapshot = client.get(f"/snapshots/{snapshot_id}")
    assert fetch_snapshot.status_code == 200
    assert fetch_snapshot.json()["stars"] == 15000

    fetch_model = client.get(f"/model-versions/{model_id}")
    assert fetch_model.status_code == 200
    assert fetch_model.json()["algorithm"] == "GradientBoostingRegressor"

    fetch_pred = client.get(f"/predictions/{prediction_id}")
    assert fetch_pred.status_code == 200
    assert fetch_pred.json()["confidence"] == 0.915

    fetch_expl = client.get(f"/explanations/{explanation_id}")
    assert fetch_expl.status_code == 200
    assert fetch_expl.json()["prediction_id"] == prediction_id

    # 7. Verify Relational Subpath endpoints
    repo_history = client.get(f"/repositories/{repo_id}/snapshots")
    assert repo_history.status_code == 200
    assert len(repo_history.json()) == 1

    snapshot_preds = client.get(f"/snapshots/{snapshot_id}/predictions")
    assert snapshot_preds.status_code == 200
    assert len(snapshot_preds.json()) == 1

    pred_expl = client.get(f"/predictions/{prediction_id}/explanation")
    assert pred_expl.status_code == 200
    assert pred_expl.json()["id"] == explanation_id
