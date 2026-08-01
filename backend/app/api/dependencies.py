from backend.app.services.cache_service import PredictionCache
from backend.app.services.forecast_service import ForecastService
from backend.app.services.inference_service import InferenceService
from backend.app.services.metrics_service import MetricsService
from backend.app.services.prediction_pipeline import PredictionPipeline
from backend.app.services.snapshot_service import RepositorySnapshotService

# Global singletons
_PREDICTION_CACHE = PredictionCache()
_METRICS_SERVICE = MetricsService()
_INFERENCE_SERVICE = InferenceService()
_SNAPSHOT_SERVICE = RepositorySnapshotService()


def get_prediction_cache() -> PredictionCache:
    """Dependency provider for PredictionCache instance."""
    return _PREDICTION_CACHE


def get_metrics_service() -> MetricsService:
    """Dependency provider for MetricsService instance."""
    return _METRICS_SERVICE


def get_inference_service() -> InferenceService:
    """Dependency provider for pre-loaded InferenceService instance."""
    return _INFERENCE_SERVICE


def get_snapshot_service() -> RepositorySnapshotService:
    """Dependency provider for RepositorySnapshotService instance."""
    return _SNAPSHOT_SERVICE


def get_forecast_service() -> ForecastService:
    """Dependency provider for ForecastService instance."""
    pipeline = PredictionPipeline(
        snapshot_service=_SNAPSHOT_SERVICE,
        inference_service=_INFERENCE_SERVICE,
    )
    return ForecastService(
        pipeline=pipeline,
        cache=_PREDICTION_CACHE,
        metrics=_METRICS_SERVICE,
    )
