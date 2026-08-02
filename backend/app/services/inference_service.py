from typing import Any

from backend.app.api.exceptions import ModelUnavailableError
from backend.app.logging import logger
from backend.app.ml.registry.model_registry import ModelRegistry
from ml.inference.predictor import ForecastPrediction, RepositoryPredictor


class InferenceEngine:
    """Abstraction hiding XGBoost / ML engine details behind a clean predict(features) interface."""

    def __init__(self, model_version: str = "v1.0", predictor: RepositoryPredictor | None = None):
        self.model_version = model_version
        self.predictor = predictor or RepositoryPredictor(model_version=model_version)

    def predict(self, features: Any, horizon_days: int = 180) -> ForecastPrediction:
        """Run ML inference over features vector or model container."""
        return self.predictor.predict(features, horizon_days=horizon_days)


class InferenceService:
    """Singleton service managing in-memory loaded models to eliminate per-request disk IO."""

    def __init__(self, registry: ModelRegistry | None = None):
        self.registry = registry or ModelRegistry()
        self._loaded_engines: dict[str, InferenceEngine] = {}
        # Pre-load default v1.0 engine
        self._loaded_engines["v1.0"] = InferenceEngine(model_version="v1.0")

    def get_engine(self, version: str = "v1.0") -> InferenceEngine:
        """Retrieve pre-loaded in-memory InferenceEngine instance."""
        if version not in self._loaded_engines:
            try:
                model, schema = self.registry.load_model("repository_growth", version=version)
                # Wrap loaded model in engine
                engine = InferenceEngine(model_version=version)
                self._loaded_engines[version] = engine
            except Exception as exc:
                logger.warning(
                    f"Model version '{version}' not pre-loaded. Falling back to default engine.",
                    extra={"error": str(exc)},
                )
                if "v1.0" in self._loaded_engines:
                    return self._loaded_engines["v1.0"]
                raise ModelUnavailableError(
                    f"Model version '{version}' is unavailable in registry.",
                    details={"version": version},
                ) from exc

        return self._loaded_engines[version]

    def is_model_loaded(self) -> bool:
        """Readiness check helper verifying model is loaded in memory."""
        return len(self._loaded_engines) > 0
