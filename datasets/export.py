import hashlib
import json
import os
import subprocess
from datetime import UTC, datetime
from typing import Any

from pydantic import BaseModel, ConfigDict, Field

from backend.app.logging import logger


class DatasetManifest(BaseModel):
    """Immutable metadata manifest exported alongside Parquet datasets for full reproducibility."""

    model_config = ConfigDict(frozen=True)

    dataset_version: str = Field(default="v1.0")
    dataset_hash: str = Field(default="", description="SHA-256 cryptographic content digest")
    snapshot_schema: int = Field(default=1)
    feature_schema: int = Field(default=1)
    label_schema: int = Field(default=1)
    created_at: str = Field(default_factory=lambda: datetime.now(UTC).isoformat())
    num_rows: int
    prediction_horizon_days: int = Field(default=180)
    git_commit: str = Field(default="unknown")
    provenance_columns: list[str] = Field(
        default_factory=lambda: [
            "full_name",
            "snapshot_time",
            "label_future_time",
            "feature_schema_version",
            "label_schema_version",
        ]
    )


class DatasetExporter:
    """Exports dataset rows to Parquet primary format and writes DatasetManifest JSON."""

    def _get_git_commit(self) -> str:
        try:
            res = subprocess.run(
                ["git", "rev-parse", "--short", "HEAD"],
                capture_output=True,
                text=True,
                check=True,
            )
            return res.stdout.strip()
        except Exception:
            return "unknown"

    def _compute_file_hash(self, file_path: str) -> str:
        hasher = hashlib.sha256()
        with open(file_path, "rb") as f:
            while chunk := f.read(8192):
                hasher.update(chunk)
        return hasher.hexdigest()

    def export_dataset(
        self,
        rows: list[dict[str, Any]],
        output_dir: str,
        dataset_version: str = "v1.0",
        prediction_horizon_days: int = 180,
    ) -> tuple[str, str]:
        """Exports dataset rows to output_dir/dataset.parquet and output_dir/manifest.json.

        Returns tuple of (parquet_path, manifest_path).
        """
        os.makedirs(output_dir, exist_ok=True)
        parquet_path = os.path.join(output_dir, "dataset.parquet")
        manifest_path = os.path.join(output_dir, "manifest.json")

        # 1. Write Parquet file using pandas
        try:
            import pandas as pd  # type: ignore

            df = pd.DataFrame(rows)
            df.to_parquet(parquet_path, index=False)
            logger.info(
                "Exported dataset to Parquet format",
                extra={"parquet_path": parquet_path, "num_rows": len(rows)},
            )
        except Exception as exc:
            logger.warning(
                "Pandas/PyArrow export failed, falling back to JSON serialization",
                extra={"error": str(exc)},
            )
            parquet_path = os.path.join(output_dir, "dataset.json")
            with open(parquet_path, "w", encoding="utf-8") as f:
                json.dump(rows, f, indent=2)

        # Compute SHA-256 content hash of exported dataset file
        file_hash = self._compute_file_hash(parquet_path)

        # 2. Write Manifest JSON
        manifest = DatasetManifest(
            dataset_version=dataset_version,
            dataset_hash=file_hash,
            snapshot_schema=1,
            feature_schema=1,
            label_schema=1,
            created_at=datetime.now(UTC).isoformat(),
            num_rows=len(rows),
            prediction_horizon_days=prediction_horizon_days,
            git_commit=self._get_git_commit(),
        )

        with open(manifest_path, "w", encoding="utf-8") as f:
            f.write(manifest.model_dump_json(indent=2))

        logger.info(
            "Exported DatasetManifest metadata",
            extra={"manifest_path": manifest_path, "dataset_hash": file_hash[:12]},
        )
        return parquet_path, manifest_path
