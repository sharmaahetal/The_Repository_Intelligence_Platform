import json
import os
import tempfile
from datetime import UTC, datetime

import pytest

import app.features.builders.temporal.activity  # noqa: F401
from app.snapshots.snapshot_builder import SnapshotBuilder
from datasets.dataset_builder import DatasetBuilder
from datasets.dataset_validator import DatasetValidator
from datasets.export import DatasetExporter
from datasets.label_generator import PredictionHorizon
from datasets.split import ChronologicalSplitter


@pytest.fixture
def snapshot_pairs():
    builder = SnapshotBuilder()

    t0_a = datetime(2023, 1, 1, 0, 0, 0, tzinfo=UTC)
    tf_a = datetime(2023, 7, 1, 0, 0, 0, tzinfo=UTC)

    t0_b = datetime(2024, 1, 1, 0, 0, 0, tzinfo=UTC)
    tf_b = datetime(2024, 7, 1, 0, 0, 0, tzinfo=UTC)

    t0_c = datetime(2025, 1, 1, 0, 0, 0, tzinfo=UTC)
    tf_c = datetime(2025, 7, 1, 0, 0, 0, tzinfo=UTC)

    snap_t0_a = builder.build_snapshot_from_raw({"name": "repo_a", "owner": {"login": "dev"}, "stargazers_count": 100}, snapshot_time=t0_a)
    snap_tf_a = builder.build_snapshot_from_raw({"name": "repo_a", "owner": {"login": "dev"}, "stargazers_count": 150}, snapshot_time=tf_a)

    snap_t0_b = builder.build_snapshot_from_raw({"name": "repo_b", "owner": {"login": "dev"}, "stargazers_count": 200}, snapshot_time=t0_b)
    snap_tf_b = builder.build_snapshot_from_raw({"name": "repo_b", "owner": {"login": "dev"}, "stargazers_count": 220}, snapshot_time=tf_b)

    snap_t0_c = builder.build_snapshot_from_raw({"name": "repo_c", "owner": {"login": "dev"}, "stargazers_count": 500}, snapshot_time=t0_c)
    snap_tf_c = builder.build_snapshot_from_raw({"name": "repo_c", "owner": {"login": "dev"}, "stargazers_count": 700}, snapshot_time=tf_c)

    return [
        (snap_t0_a, snap_tf_a),
        (snap_t0_b, snap_tf_b),
        (snap_t0_c, snap_tf_c),
    ]


@pytest.mark.asyncio
async def test_dataset_builder_end_to_end(snapshot_pairs):
    with tempfile.TemporaryDirectory() as tmp_dir:
        dataset_builder = DatasetBuilder()

        val_start = datetime(2024, 1, 1, 0, 0, 0, tzinfo=UTC)
        test_start = datetime(2025, 1, 1, 0, 0, 0, tzinfo=UTC)

        result = await dataset_builder.build_and_export_dataset(
            snapshot_pairs=snapshot_pairs,
            output_dir=tmp_dir,
            horizon=PredictionHorizon.DAYS_180,
            dataset_version="v1.2",
            val_start_time=val_start,
            test_start_time=test_start,
        )

        assert result["num_rows"] == 3
        assert os.path.exists(result["parquet_path"])
        assert os.path.exists(result["manifest_path"])

        # Verify Manifest JSON
        with open(result["manifest_path"], "r", encoding="utf-8") as f:
            manifest = json.load(f)

        assert manifest["dataset_version"] == "v1.2"
        assert manifest["num_rows"] == 3
        assert manifest["prediction_horizon_days"] == 180

        # Verify Chronological Splitter
        splits = result["splits"]
        assert len(splits["train"]) == 1
        assert len(splits["validation"]) == 1
        assert len(splits["test"]) == 1


def test_dataset_validator_rejects_duplicates_and_nan():
    validator = DatasetValidator()

    bad_duplicate_rows = [
        {"full_name": "owner/repo", "snapshot_time": "2025-01-01T00:00:00+00:00", "prediction_horizon_days": 180},
        {"full_name": "owner/repo", "snapshot_time": "2025-01-01T00:00:00+00:00", "prediction_horizon_days": 180},
    ]

    with pytest.raises(ValueError, match="Duplicate"):
        validator.validate_dataset_rows(bad_duplicate_rows)

    bad_nan_rows = [
        {"full_name": "owner/repo1", "snapshot_time": "2025-01-01T00:00:00+00:00", "star_ratio": float("nan")}
    ]

    with pytest.raises(ValueError, match="non-finite"):
        validator.validate_dataset_rows(bad_nan_rows)
