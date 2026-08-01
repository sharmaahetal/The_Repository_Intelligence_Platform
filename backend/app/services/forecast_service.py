from backend.app.api.models import ForecastResponse
from backend.app.logging import logger
from backend.app.services.cache_service import PredictionCache
from backend.app.services.metrics_service import MetricsService
from backend.app.services.prediction_pipeline import PredictionPipeline


class ForecastService:
    """High-level application service orchestrating prediction caching and pipeline execution."""

    def __init__(
        self,
        pipeline: PredictionPipeline | None = None,
        cache: PredictionCache | None = None,
        metrics: MetricsService | None = None,
    ):
        self.pipeline = pipeline or PredictionPipeline()
        self.cache = cache or PredictionCache()
        self.metrics = metrics or MetricsService()

    async def get_forecast(
        self,
        owner: str,
        repo: str,
        horizon: int = 180,
        model_version: str = "v1.0",
    ) -> ForecastResponse:
        """Fetch forecast prediction, checking prediction cache first."""
        cached_response = self.cache.get(owner, repo, model_version, horizon)
        if cached_response is not None:
            self.metrics.record_cache_hit()
            # Return copy with cached=True
            return cached_response.model_copy(update={"cached": True})

        self.metrics.record_cache_miss()

        # Execute Prediction Pipeline
        try:
            response = await self.pipeline.execute_pipeline(
                owner=owner,
                repo=repo,
                horizon=horizon,
                model_version=model_version,
            )
            # Store in cache
            self.cache.set(owner, repo, model_version, horizon, response)
            self.metrics.record_request(model_version=model_version, latency_ms=10.0, success=True)
            return response
        except Exception as exc:
            self.metrics.record_request(model_version=model_version, latency_ms=10.0, success=False)
            logger.error(
                f"Failed to compute forecast for {owner}/{repo}",
                extra={"owner": owner, "repo": repo, "error": str(exc)},
            )
            raise exc
