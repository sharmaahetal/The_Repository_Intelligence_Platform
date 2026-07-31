from app.monitoring.evaluator import OutcomeEvaluator
from app.monitoring.tracker import PredictionTracker

from datasets.label_generator import TargetLabels
from ml.inference.predictor import ForecastPrediction


def test_prediction_logging_and_drift_evaluation():
    # 1. Simulate live prediction at t_0
    prediction = ForecastPrediction(
        prediction_horizon_days=180,
        growth_probability=0.85,
        abandonment_probability=0.05,
        maintainer_retention_probability=0.90,
        model_version="v1.0",
    )

    # 2. Log live prediction
    tracker = PredictionTracker()
    record = tracker.log_prediction("facebook", "react", prediction)

    assert record.owner == "facebook"
    assert record.repo == "react"
    assert record.growth_probability == 0.85

    # 3. Simulate ground-truth outcome 180 days later at t_0 + 180d
    actual_labels = TargetLabels(
        snapshot_timestamp="2025-07-01T00:00:00Z",
        horizon_days=180,
        is_growth=True,  # Actual outcome: repo grew
        is_abandoned=False,  # Actual outcome: not abandoned
        is_retained=True,
        star_growth_percent=32.0,
    )

    # 4. Evaluate Brier calibration score drift
    evaluator = OutcomeEvaluator()
    metrics = evaluator.evaluate_prediction_error(record, actual_labels)

    # Brier Error for Growth = (0.85 - 1.0)^2 = 0.0225
    assert metrics["growth_brier_error"] == 0.0225
    # Brier Error for Abandonment = (0.05 - 0.0)^2 = 0.0025
    assert metrics["abandon_brier_error"] == 0.0025
