from datetime import UTC, datetime

import pytest
from app.snapshots.snapshot_builder import SnapshotBuilder
from datasets.label_generator import LabelGenerator, PredictionHorizon


def test_label_generator_temporal_anti_leakage_guard():
    builder = SnapshotBuilder()

    t0 = datetime(2025, 1, 1, 0, 0, 0, tzinfo=UTC)
    raw_t0 = {
        "name": "vscode",
        "owner": {"login": "microsoft"},
        "full_name": "microsoft/vscode",
        "stargazers_count": 100000,
    }
    snapshot_t0 = builder.build_snapshot_from_raw(raw_t0, snapshot_time=t0)

    # 1. Invalid temporal order: t_future == t_0
    snapshot_same_time = builder.build_snapshot_from_raw(raw_t0, snapshot_time=t0)

    label_gen = LabelGenerator()

    with pytest.raises(ValueError, match="Temporal leakage detected"):
        label_gen.generate_labels(
            snapshot_t0=snapshot_t0,
            snapshot_future=snapshot_same_time,
            horizon=PredictionHorizon.DAYS_180,
        )

    # 2. Invalid temporal order: t_future < t_0 (past snapshot passed as future)
    t_past = datetime(2024, 12, 1, 0, 0, 0, tzinfo=UTC)
    snapshot_past = builder.build_snapshot_from_raw(raw_t0, snapshot_time=t_past)

    with pytest.raises(ValueError, match="Temporal leakage detected"):
        label_gen.generate_labels(
            snapshot_t0=snapshot_t0,
            snapshot_future=snapshot_past,
            horizon=PredictionHorizon.DAYS_180,
        )


def test_valid_temporal_label_generation():
    builder = SnapshotBuilder()

    t0 = datetime(2025, 1, 1, 0, 0, 0, tzinfo=UTC)
    t180 = datetime(2025, 7, 1, 0, 0, 0, tzinfo=UTC)

    raw_t0 = {"name": "react", "owner": {"login": "facebook"}, "full_name": "facebook/react", "stargazers_count": 200000}
    raw_future = {"name": "react", "owner": {"login": "facebook"}, "full_name": "facebook/react", "stargazers_count": 260000}

    snapshot_t0 = builder.build_snapshot_from_raw(raw_t0, snapshot_time=t0)
    snapshot_future = builder.build_snapshot_from_raw(raw_future, snapshot_time=t180)

    label_gen = LabelGenerator()
    target_labels = label_gen.generate_labels(snapshot_t0, snapshot_future, horizon=PredictionHorizon.DAYS_180)

    assert target_labels.horizon == PredictionHorizon.DAYS_180
    assert target_labels.get("is_growth") is True
    assert target_labels.get("star_growth_percent") == 30.0
