from datetime import UTC, datetime

import pytest
from fastapi.testclient import TestClient

from backend.app.api.deps import (
    get_model_version_service,
    get_prediction_explanation_service,
)
from backend.app.database.models.explanation import PredictionExplanation
from backend.app.database.models.model_version import ModelVersion
from backend.app.main import app
from backend.app.services.exceptions import (
    ModelVersionAlreadyExists,
    ModelVersionNotFound,
    PredictionExplanationNotFound,
)


class FakeExplanationService:
    def __init__(self) -> None:
        now = datetime.now(UTC)
        self.explanations: dict[int, PredictionExplanation] = {
            1: PredictionExplanation(
                id=1,
                prediction_id=10,
                summary="High star growth driven by commits",
                top_positive_features={"stars": 0.8},
                top_negative_features={"issues": 0.1},
                shap_json={"base_value": 0.5},
                created_at=now,
                updated_at=now,
            )
        }

    async def create_explanation(self, **kwargs):
        now = datetime.now(UTC)
        new_id = max(self.explanations.keys(), default=0) + 1
        expl = PredictionExplanation(
            id=new_id,
            created_at=now,
            updated_at=now,
            **kwargs,
        )
        self.explanations[new_id] = expl
        return expl

    async def get_explanation(self, explanation_id: int):
        if explanation_id in self.explanations:
            return self.explanations[explanation_id]
        raise PredictionExplanationNotFound(explanation_id)

    async def get_by_prediction(self, prediction_id: int):
        for expl in self.explanations.values():
            if expl.prediction_id == prediction_id:
                return expl
        raise PredictionExplanationNotFound(prediction_id)

    async def update_explanation(self, explanation_id: int, **attributes):
        if explanation_id not in self.explanations:
            raise PredictionExplanationNotFound(explanation_id)
        expl = self.explanations[explanation_id]
        for k, v in attributes.items():
            setattr(expl, k, v)
        return expl

    async def delete_explanation(self, explanation_id: int):
        if explanation_id not in self.explanations:
            raise PredictionExplanationNotFound(explanation_id)
        del self.explanations[explanation_id]
        return True


class FakeModelVersionService:
    def __init__(self) -> None:
        now = datetime.now(UTC)
        self.models: dict[int, ModelVersion] = {
            1: ModelVersion(
                id=1,
                version="1.0.0",
                algorithm="RandomForest",
                training_dataset_hash="hash123",
                feature_schema_version="v1",
                accuracy=0.9,
                precision=0.88,
                recall=0.87,
                f1=0.875,
                auc=0.92,
                artifact_path="/artifacts/v1.joblib",
                trained_at=now,
                created_at=now,
                updated_at=now,
            )
        }

    async def register_model(self, **kwargs):
        version = kwargs["version"]
        if any(m.version == version for m in self.models.values()):
            raise ModelVersionAlreadyExists(version)
        now = datetime.now(UTC)
        new_id = max(self.models.keys(), default=0) + 1
        trained_at = kwargs.get("trained_at") or now
        model_kwargs = {k: v for k, v in kwargs.items() if k != "trained_at"}
        model = ModelVersion(
            id=new_id,
            trained_at=trained_at,
            created_at=now,
            updated_at=now,
            **model_kwargs,
        )
        self.models[new_id] = model
        return model

    async def list_models(self):
        return list(self.models.values())

    async def get_model(self, model_id: int | None = None, version: str | None = None):
        if model_id in self.models:
            return self.models[model_id]
        raise ModelVersionNotFound(model_id or version or "unknown")

    async def latest_model(self):
        if self.models:
            return list(self.models.values())[-1]
        raise ModelVersionNotFound("latest")

    async def best_model(self, metric: str = "f1"):
        if self.models:
            return max(self.models.values(), key=lambda m: getattr(m, metric, 0.0))
        raise ModelVersionNotFound("best")

    async def update_model(self, model_id: int, **attributes):
        if model_id not in self.models:
            raise ModelVersionNotFound(model_id)
        m = self.models[model_id]
        for k, v in attributes.items():
            setattr(m, k, v)
        return m

    async def delete_model(self, model_id: int):
        if model_id not in self.models:
            raise ModelVersionNotFound(model_id)
        del self.models[model_id]
        return True


@pytest.fixture
def client_with_fakes():
    fake_expl_service = FakeExplanationService()
    fake_model_service = FakeModelVersionService()
    app.dependency_overrides[get_prediction_explanation_service] = lambda: fake_expl_service
    app.dependency_overrides[get_model_version_service] = lambda: fake_model_service
    client = TestClient(app, raise_server_exceptions=False)
    yield client
    app.dependency_overrides.clear()


def test_explanations_endpoints(client_with_fakes):
    payload = {
        "prediction_id": 20,
        "summary": "Test explanation",
        "top_positive_features": {"stars": 0.9},
        "top_negative_features": {},
        "shap_json": {"base": 0.1},
    }
    create_res = client_with_fakes.post("/explanations", json=payload)
    assert create_res.status_code == 201
    exp_id = create_res.json()["id"]

    get_res = client_with_fakes.get(f"/explanations/{exp_id}")
    assert get_res.status_code == 200
    assert get_res.json()["summary"] == "Test explanation"

    by_pred_res = client_with_fakes.get("/explanations/prediction/20")
    assert by_pred_res.status_code == 200

    patch_res = client_with_fakes.patch(f"/explanations/{exp_id}", json={"summary": "Updated"})
    assert patch_res.status_code == 200
    assert patch_res.json()["summary"] == "Updated"

    del_res = client_with_fakes.delete(f"/explanations/{exp_id}")
    assert del_res.status_code == 204


def test_model_versions_endpoints(client_with_fakes):
    payload = {
        "version": "2.0.0",
        "algorithm": "XGBoost",
        "training_dataset_hash": "hash456",
        "feature_schema_version": "v2",
        "accuracy": 0.95,
        "precision": 0.94,
        "recall": 0.93,
        "f1": 0.935,
        "auc": 0.97,
        "artifact_path": "/artifacts/v2.joblib",
    }
    create_res = client_with_fakes.post("/model-versions", json=payload)
    assert create_res.status_code == 201
    model_id = create_res.json()["id"]

    list_res = client_with_fakes.get("/model-versions")
    assert list_res.status_code == 200
    assert len(list_res.json()) == 2

    latest_res = client_with_fakes.get("/model-versions/latest")
    assert latest_res.status_code == 200

    best_res = client_with_fakes.get("/model-versions/best?metric=f1")
    assert best_res.status_code == 200

    get_res = client_with_fakes.get(f"/model-versions/{model_id}")
    assert get_res.status_code == 200
    assert get_res.json()["algorithm"] == "XGBoost"

    patch_res = client_with_fakes.patch(f"/model-versions/{model_id}", json={"algorithm": "LightGBM"})
    assert patch_res.status_code == 200
    assert patch_res.json()["algorithm"] == "LightGBM"

    del_res = client_with_fakes.delete(f"/model-versions/{model_id}")
    assert del_res.status_code == 204
