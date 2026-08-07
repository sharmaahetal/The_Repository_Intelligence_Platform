from datetime import UTC, datetime

import pytest
from fastapi.testclient import TestClient

from backend.app.api.deps import get_prediction_service
from backend.app.database.models.prediction import Prediction
from backend.app.main import app
from backend.app.services.exceptions import PredictionNotFound


class FakePredictionService:
    def __init__(self) -> None:
        now = datetime.now(UTC)
        self.predictions: dict[int, Prediction] = {
            1: Prediction(
                id=1,
                repository_snapshot_id=10,
                model_version_id=5,
                predicted_growth=42.5,
                confidence=0.92,
                prediction_timestamp=now,
                prediction_horizon_days=30,
                created_at=now,
                updated_at=now,
            )
        }

    async def create_prediction(self, **kwargs):
        now = datetime.now(UTC)
        new_id = max(self.predictions.keys(), default=0) + 1
        ts = kwargs.get("prediction_timestamp") or now
        prediction = Prediction(
            id=new_id,
            repository_snapshot_id=kwargs["repository_snapshot_id"],
            model_version_id=kwargs["model_version_id"],
            predicted_growth=kwargs["predicted_growth"],
            confidence=kwargs["confidence"],
            prediction_timestamp=ts,
            prediction_horizon_days=kwargs.get("prediction_horizon_days", 30),
            created_at=now,
            updated_at=now,
        )
        self.predictions[new_id] = prediction
        return prediction

    async def get_prediction(self, prediction_id: int):
        if prediction_id in self.predictions:
            return self.predictions[prediction_id]
        raise PredictionNotFound(prediction_id)

    async def update_prediction(self, prediction_id: int, **attributes):
        if prediction_id not in self.predictions:
            raise PredictionNotFound(prediction_id)
        pred = self.predictions[prediction_id]
        for k, v in attributes.items():
            setattr(pred, k, v)
        return pred

    async def delete_prediction(self, prediction_id: int):
        if prediction_id not in self.predictions:
            raise PredictionNotFound(prediction_id)
        del self.predictions[prediction_id]
        return True

    async def list_predictions_for_snapshot(self, repository_snapshot_id: int):
        return [p for p in self.predictions.values() if p.repository_snapshot_id == repository_snapshot_id]


@pytest.fixture
def client_with_fake_service():
    fake_service = FakePredictionService()
    app.dependency_overrides[get_prediction_service] = lambda: fake_service
    client = TestClient(app, raise_server_exceptions=False)
    yield client
    app.dependency_overrides.clear()


def test_create_prediction_endpoint(client_with_fake_service):
    now_iso = datetime.now(UTC).isoformat()
    payload = {
        "repository_snapshot_id": 10,
        "model_version_id": 5,
        "predicted_growth": 12.3,
        "confidence": 0.88,
        "prediction_timestamp": now_iso,
        "prediction_horizon_days": 30,
    }
    response = client_with_fake_service.post("/predictions", json=payload)
    assert response.status_code == 201
    data = response.json()
    assert data["predicted_growth"] == 12.3
    assert data["confidence"] == 0.88


def test_get_prediction_endpoint(client_with_fake_service):
    response = client_with_fake_service.get("/predictions/1")
    assert response.status_code == 200
    assert response.json()["predicted_growth"] == 42.5


def test_update_prediction_endpoint(client_with_fake_service):
    payload = {"predicted_growth": 50.0}
    response = client_with_fake_service.patch("/predictions/1", json=payload)
    assert response.status_code == 200
    assert response.json()["predicted_growth"] == 50.0


def test_delete_prediction_endpoint(client_with_fake_service):
    response = client_with_fake_service.delete("/predictions/1")
    assert response.status_code == 204

    # Verify deletion
    get_res = client_with_fake_service.get("/predictions/1")
    assert get_res.status_code in (404, 500)


def test_snapshot_predictions_endpoints(client_with_fake_service):
    res1 = client_with_fake_service.get("/predictions/snapshot/10")
    assert res1.status_code == 200
    assert len(res1.json()) == 1

    res2 = client_with_fake_service.get("/snapshots/10/predictions")
    assert res2.status_code == 200
    assert len(res2.json()) == 1
