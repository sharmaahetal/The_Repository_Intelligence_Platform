import numpy as np
from backend.app.monitoring.drift import DriftDetector, DriftReport


def test_drift_detector_stable_distribution():
    np.random.seed(42)
    baseline = np.random.normal(loc=10.0, scale=2.0, size=500)
    current = baseline + np.random.normal(loc=0.0, scale=0.05, size=500)

    detector = DriftDetector()
    report: DriftReport = detector.detect_feature_drift("star_density_index", baseline, current)

    assert report.psi_value < 0.10
    assert report.has_drift is False
    assert report.drift_severity == "stable"


def test_drift_detector_severe_drift_alert():
    np.random.seed(42)
    baseline = np.random.normal(loc=10.0, scale=1.0, size=500)
    current = np.random.normal(loc=50.0, scale=5.0, size=500)  # Significant shift

    detector = DriftDetector()
    report: DriftReport = detector.detect_feature_drift("fork_to_star_ratio", baseline, current)

    assert report.psi_value >= 0.25
    assert report.has_drift is True
    assert report.drift_severity == "severe"
    assert len(report.alerts) > 0
    assert "SEVERE FEATURE DRIFT" in report.alerts[0]
