from datetime import datetime
from typing import Any

from app.features.pipeline import FeaturePipeline
from app.logging import logger
from app.models.snapshot import RepositorySnapshot
from datasets.dataset_validator import DatasetValidator
from datasets.export import DatasetExporter
from datasets.label_generator import LabelGenerator, PredictionHorizon
from datasets.split import ChronologicalSplitter


class DatasetBuilder:
    """Orchestrator building reproducible training datasets from pairs of historical snapshots (S(t_0), S(t_0 + H))."""

    def __init__(
        self,
        feature_pipeline: FeaturePipeline | None = None,
        label_generator: LabelGenerator | None = None,
        validator: DatasetValidator | None = None,
        splitter: ChronologicalSplitter | None = None,
        exporter: DatasetExporter | None = None,
    ):
        self.feature_pipeline = feature_pipeline or FeaturePipeline()
        self.label_generator = label_generator or LabelGenerator()
        self.validator = validator or DatasetValidator()
        self.splitter = splitter or ChronologicalSplitter()
        self.exporter = exporter or DatasetExporter()

    async def build_dataset_row(
        self,
        snapshot_t0: RepositorySnapshot,
        snapshot_future: RepositorySnapshot,
        horizon: PredictionHorizon = PredictionHorizon.DAYS_180,
    ) -> dict[str, Any]:
        """Assembles a single training dataset row from S(t_0) and S(t_0 + H)."""
        # 1. Compute features strictly from S(t_0)
        repo_features = await self.feature_pipeline.compute_features_async(snapshot_t0)
        feature_vector = repo_features.as_vector()

        # 2. Compute empirical target labels from S(t_0) and S(t_0 + H) with anti-leakage guard
        target_labels = self.label_generator.generate_labels(
            snapshot_t0=snapshot_t0,
            snapshot_future=snapshot_future,
            horizon=horizon,
        )
        label_vector = target_labels.as_dict()

        ts0_str = (
            snapshot_t0.snapshot_timestamp.isoformat()
            if isinstance(snapshot_t0.snapshot_timestamp, datetime)
            else str(snapshot_t0.snapshot_timestamp)
        )
        ts_future_str = (
            snapshot_future.snapshot_timestamp.isoformat()
            if isinstance(snapshot_future.snapshot_timestamp, datetime)
            else str(snapshot_future.snapshot_timestamp)
        )

        row: dict[str, Any] = {
            # Provenance Metadata
            "full_name": snapshot_t0.full_name,
            "snapshot_time": ts0_str,
            "label_future_time": ts_future_str,
            "prediction_horizon_days": int(horizon),
            "feature_schema_version": repo_features.schema_version,
            "label_schema_version": target_labels.schema_version,
        }

        # Add feature & label vectors
        row.update(feature_vector)
        row.update(label_vector)
        return row

    async def build_and_export_dataset(
        self,
        snapshot_pairs: list[tuple[RepositorySnapshot, RepositorySnapshot]],
        output_dir: str,
        horizon: PredictionHorizon = PredictionHorizon.DAYS_180,
        dataset_version: str = "v1.0",
        val_start_time: datetime | None = None,
        test_start_time: datetime | None = None,
    ) -> dict[str, Any]:
        """Builds dataset rows, runs validation, performs chronological split, and exports Parquet/Manifest files."""
        rows: list[dict[str, Any]] = []

        for snapshot_t0, snapshot_future in snapshot_pairs:
            row = await self.build_dataset_row(snapshot_t0, snapshot_future, horizon=horizon)
            rows.append(row)

        # 1. Run Pre-Export Quality Assertions
        self.validator.validate_dataset_rows(rows)

        # 2. Chronological Split if boundary timestamps provided
        split_results = {}
        if val_start_time and test_start_time:
            split_results = self.splitter.split_dataset(rows, val_start_time, test_start_time)

        # 3. Export Parquet Primary File & Metadata Manifest
        parquet_path, manifest_path = self.exporter.export_dataset(
            rows=rows,
            output_dir=output_dir,
            dataset_version=dataset_version,
            prediction_horizon_days=int(horizon),
        )

        logger.info(
            "Completed dataset build and export",
            extra={
                "num_rows": len(rows),
                "parquet_path": parquet_path,
                "manifest_path": manifest_path,
            },
        )

        return {
            "num_rows": len(rows),
            "parquet_path": parquet_path,
            "manifest_path": manifest_path,
            "splits": split_results,
        }
