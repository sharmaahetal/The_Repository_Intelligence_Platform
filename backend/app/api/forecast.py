from datetime import UTC, datetime
from app.collectors.validator import RawPayloadValidator
from app.features.builders.temporal.activity import default_registry
from app.narrative.synthesizer import NarrativeSynthesizer
from app.services.report_generator import ForecastReportGenerator
from app.snapshots.snapshot_builder import SnapshotBuilder
from fastapi import APIRouter, Query
from pydantic import BaseModel

from ml.inference.predictor import RepositoryPredictor

router = APIRouter(tags=["Forecast"])


class ForecastReportResponse(BaseModel):
    owner: str
    repo: str
    prediction_horizon_days: int
    derived_health_index: int
    growth_probability: float
    abandonment_probability: float
    maintainer_retention_probability: float
    narrative_summary: str
    top_drivers: list[str]
    top_risks: list[str]
    model_version: str


@router.get("/forecast/{owner}/{repo}", response_model=ForecastReportResponse)
async def get_repository_forecast(
    owner: str,
    repo: str,
    horizon: int = Query(default=180, description="Forecast horizon in days (90, 180, 365)"),
):
    """Generate probabilistic forecast report for a GitHub repository."""
    # 1. Mock raw snapshot payload (in production, loaded from RawPayloadRepository / GitHub API)
    raw_payload_dict = {
        "name": repo,
        "owner": {"login": owner},
        "full_name": f"{owner}/{repo}",
        "stargazers_count": 120000,
        "forks_count": 22000,
        "open_issues_count": 3500,
        "subscribers_count": 1800,
        "size": 350000,
        "language": "Python",
        "default_branch": "main",
    }

    validator = RawPayloadValidator()
    raw_payload = validator.validate_repository_payload(raw_payload_dict)

    # 2. Build snapshot S(t_0) with deterministic UTC snapshot_time
    t_now = datetime.now(UTC)
    builder = SnapshotBuilder()
    snapshot = builder.build_snapshot_from_raw(raw_payload, snapshot_time=t_now)

    # 3. Extract temporal feature vector
    features = default_registry.compute_all(snapshot)

    # 4. Generate pure ML probabilities
    predictor = RepositoryPredictor(model_version="v1.0")
    prediction = predictor.predict(features, horizon_days=horizon)

    # 5. Compute Product-level Health Index in Product Service Layer
    report_generator = ForecastReportGenerator()
    report_data = report_generator.generate_report_data(prediction)

    # 6. Synthesize natural language narrative
    synthesizer = NarrativeSynthesizer()
    narrative = synthesizer.synthesize(owner, repo, prediction)

    return ForecastReportResponse(
        owner=owner,
        repo=repo,
        prediction_horizon_days=horizon,
        derived_health_index=report_data.health_index,
        growth_probability=prediction.growth_probability,
        abandonment_probability=prediction.abandonment_probability,
        maintainer_retention_probability=prediction.maintainer_retention_probability,
        narrative_summary=narrative,
        top_drivers=[
            "Sustained core contributor retention rate",
            "High fork-to-star activity density ratio",
            "Consistent commit acceleration",
        ],
        top_risks=[
            "Minor increase in open issue turnaround queue",
        ],
        model_version=prediction.model_version,
    )
