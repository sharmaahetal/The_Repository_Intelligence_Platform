from datetime import UTC, datetime

from app.models.snapshot import RepositorySnapshot
from app.snapshots.snapshot_builder import SnapshotBuilder
from datasets.label_generator import LabelGenerator, PredictionHorizon
from ml.inference.predictor import RepositoryPredictor


def test_label_generator_and_inference_engine():
    builder = SnapshotBuilder()

    # 1. Mock snapshot at t_0
    t0 = datetime(2025, 1, 1, 0, 0, 0, tzinfo=UTC)
    raw_t0 = {
        "name": "react",
        "owner": {"login": "facebook"},
        "full_name": "facebook/react",
        "stargazers_count": 200000,
        "pushed_at": "2025-01-01T10:00:00Z",
    }
    snapshot_t0 = builder.build_snapshot_from_raw(raw_t0, snapshot_time=t0)

    # 2. Mock snapshot at t_0 + 180d
    t180 = datetime(2025, 7, 1, 0, 0, 0, tzinfo=UTC)
    raw_future = {
        "name": "react",
        "owner": {"login": "facebook"},
        "full_name": "facebook/react",
        "stargazers_count": 260000,  # 30% star growth
        "pushed_at": "2025-07-01T10:00:00Z",  # Pushes continued
    }
    snapshot_future = builder.build_snapshot_from_raw(raw_future, snapshot_time=t180)

    # Generate targets
    label_gen = LabelGenerator()
    labels = label_gen.generate_labels(snapshot_t0, snapshot_future, horizon=PredictionHorizon.DAYS_180)

    assert labels.get("is_growth") is True  # 30% > 25% threshold
    assert labels.get("is_abandoned") is False
    assert labels.get("is_retained") is True

    # 3. Test Pure ML Inference Predictor & Product Report Generator
    predictor = RepositoryPredictor(model_version="v1.0")
    features = {
        "fork_to_star_ratio": 0.22,
        "open_issue_density": 0.03,
        "subscriber_engagement_ratio": 0.03,
    }

    prediction = predictor.predict(features, horizon_days=180)

    assert prediction.prediction_horizon_days == 180
    assert 0.0 <= prediction.growth_probability <= 1.0
    assert 0.0 <= prediction.abandonment_probability <= 1.0

    # Test Product Report Generator
    from app.services.report_generator import ForecastReportGenerator

    report_gen = ForecastReportGenerator()
    report = report_gen.generate_report_data(prediction)
    assert 0 <= report.health_index <= 100
