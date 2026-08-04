import hashlib
import time

from backend.app.api.models import ForecastResponse
from backend.app.features.pipeline import FeaturePipeline
from backend.app.logging import logger
from backend.app.ml.explainability.shap_service import ExplainabilityService
from backend.app.models.context import PredictionContext
from backend.app.narrative.synthesizer import NarrativeSynthesizer
from backend.app.services.inference_service import InferenceService
from backend.app.services.report_generator import ForecastReportGenerator
from backend.app.services.snapshot_service import RepositorySnapshotService
from backend.app.services.stages import (
    ExplainabilityStage,
    FeatureStage,
    InferenceStage,
    ResponseStage,
    SnapshotStage,
)


class PredictionCache:
    """In-memory idempotency cache keyed by request hash to prevent redundant computation."""

    def __init__(self, ttl_seconds: int = 300) -> None:
        self.ttl_seconds = ttl_seconds
        self._cache: dict[str, tuple[float, ForecastResponse]] = {}

    def compute_hash(self, owner: str, repo: str, horizon: int, model_version: str) -> str:
        raw_key = f"{owner.lower()}:{repo.lower()}:{horizon}:{model_version}"
        return hashlib.sha256(raw_key.encode("utf-8")).hexdigest()[:16]

    def get(self, request_hash: str) -> ForecastResponse | None:
        if request_hash not in self._cache:
            return None
        created_at, response = self._cache[request_hash]
        if time.time() - created_at > self.ttl_seconds:
            del self._cache[request_hash]
            return None
        return response

    def set(self, request_hash: str, response: ForecastResponse) -> None:
        self._cache[request_hash] = (time.time(), response)


class PredictionPipeline:
    """Modular orchestrator executing explicit PipelineStages:
    SnapshotStage -> FeatureStage -> InferenceStage -> ExplainabilityStage -> ResponseStage.
    """

    def __init__(
        self,
        snapshot_service: RepositorySnapshotService | None = None,
        feature_pipeline: FeaturePipeline | None = None,
        inference_service: InferenceService | None = None,
        explainability: ExplainabilityService | None = None,
        report_generator: ForecastReportGenerator | None = None,
        narrative_synthesizer: NarrativeSynthesizer | None = None,
        cache: PredictionCache | None = None,
    ):
        self.cache = cache or PredictionCache(ttl_seconds=300)

        # Instantiate explicit modular pipeline stages
        self.snapshot_stage = SnapshotStage(snapshot_service=snapshot_service)
        self.feature_stage = FeatureStage(feature_pipeline=feature_pipeline)
        self.inference_stage = InferenceStage(inference_service=inference_service)
        self.explainability_stage = ExplainabilityStage(
            explainability=explainability, narrative_synthesizer=narrative_synthesizer
        )
        self.response_stage = ResponseStage(report_generator=report_generator)

    async def execute_pipeline(
        self,
        owner: str,
        repo: str,
        horizon: int = 180,
        model_version: str = "v1.0",
        request_id: str | None = None,
    ) -> ForecastResponse:
        """Executes prediction pipeline using PredictionContext and modular stages."""
        start_time = time.time()

        # 1. Idempotency Check
        req_hash = self.cache.compute_hash(owner, repo, horizon, model_version)
        cached_response = self.cache.get(req_hash)
        if cached_response is not None:
            logger.info(
                "PredictionPipeline returned cached response (Idempotency HIT)",
                extra={"owner": owner, "repo": repo, "request_hash": req_hash},
            )
            return cached_response.model_copy(update={"cached": True})

        # 2. Instantiate PredictionContext
        context = PredictionContext(
            owner=owner,
            repo=repo,
            horizon=horizon,
            model_version=model_version,
            request_id=request_id
            or f"req_{hashlib.md5(f'{owner}/{repo}'.encode()).hexdigest()[:8]}",
        )

        logger.info(
            "Executing PredictionPipeline stages",
            extra={
                "owner": owner,
                "repo": repo,
                "request_id": context.request_id,
                "horizon": horizon,
            },
        )

        # Stage 1: SnapshotStage
        snapshot, context = await self.snapshot_stage.execute(context)

        # Stage 2: FeatureStage
        repo_features = await self.feature_stage.execute(snapshot, context)

        # Stage 3: InferenceStage (CPU thread offloading)
        prediction = await self.inference_stage.execute(repo_features, context)

        # Stage 4: ExplainabilityStage (CPU thread offloading)
        top_factors, narrative, top_factors_list = await self.explainability_stage.execute(
            prediction, repo_features, context
        )

        # Stage 5: ResponseStage
        response = self.response_stage.execute(
            prediction=prediction,
            snapshot=snapshot,
            repo_features=repo_features,
            top_factors=top_factors_list,
            narrative=narrative,
            context=context,
            start_time=start_time,
            cached=False,
        )

        # Store response in idempotency cache
        self.cache.set(req_hash, response)

        return response
