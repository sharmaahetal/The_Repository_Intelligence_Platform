from datetime import datetime, timezone

from datasets.label_generator import LabelGenerator
from ml.inference.predictor import RepositoryPredictor


def test_label_generator_and_inference_engine():
    # 1. Mock snapshot at t_0
    t0 = datetime(2025, 1, 1, 0, 0, 0, tzinfo=timezone.utc)
    snapshot_t0 = {
        "full_name": "facebook/react",
        "snapshot_timestamp": t0.isoformat(),
        "stars_count": 200000,
        "pushed_at": "2025-01-01T10:00:00Z",
    }

    # 2. Mock snapshot at t_0 + 180d
    t180 = datetime(2025, 7, 1, 0, 0, 0, tzinfo=timezone.utc)
    snapshot_future = {
        "full_name": "facebook/react",
        "snapshot_timestamp": t180.isoformat(),
        "stars_count": 260000,  # 30% star growth
        "pushed_at": "2025-07-01T10:00:00Z",  # Pushes continued
    }

    # Generate targets
    label_gen = LabelGenerator()
    labels = label_gen.generate_labels(snapshot_t0, snapshot_future, horizon_days=180)

    assert labels.is_growth is True  # 30% > 25% threshold
    assert labels.is_abandoned is False
    assert labels.is_retained is True

    # 3. Test Inference Predictor
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
    assert 0 <= prediction.derived_health_index <= 100
