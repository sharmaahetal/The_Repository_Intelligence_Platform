import math
from typing import Any

from app.logging import logger


class DatasetValidator:
    """Validator performing pre-export quality & anti-leakage integrity checks on dataset rows."""

    def validate_dataset_rows(self, rows: list[dict[str, Any]]) -> None:
        """Runs quality assertions against all dataset rows before exporting.
        
        Raises ValueError or TypeError if dataset integrity criteria are violated.
        """
        if not rows:
            raise ValueError("Dataset is empty. Cannot validate 0 rows.")

        seen_keys: set[tuple[str, str]] = set()

        for idx, row in enumerate(rows):
            full_name = row.get("full_name") or row.get("repository_id")
            snapshot_time = row.get("snapshot_time")
            label_future_time = row.get("label_future_time")
            horizon_days = row.get("prediction_horizon_days", 180)

            if not full_name or not snapshot_time:
                raise ValueError(f"Row #{idx} missing required provenance key 'full_name' or 'snapshot_time'")

            # 1. Uniqueness check: (repo_id, snapshot_time) pair
            key = (str(full_name), str(snapshot_time))
            if key in seen_keys:
                raise ValueError(f"Duplicate (repository_id, snapshot_time) pair detected in dataset: {key}")
            seen_keys.add(key)

            # 2. Strict temporal order check: snapshot_time < label_future_time
            if label_future_time:
                if str(snapshot_time) >= str(label_future_time):
                    raise ValueError(
                        f"Temporal integrity violation at row #{idx} ({full_name}): "
                        f"snapshot_time ({snapshot_time}) >= label_future_time ({label_future_time})"
                    )

            # 3. Horizon validity
            if isinstance(horizon_days, (int, float)) and horizon_days <= 0:
                raise ValueError(f"Prediction horizon must be positive, got {horizon_days} at row #{idx}")

            # 4. Check for NaNs or Infinities in features and labels
            for k, v in row.items():
                if isinstance(v, float):
                    if math.isnan(v) or math.isinf(v):
                        raise ValueError(f"Invalid non-finite value '{v}' for key '{k}' at row #{idx} ({full_name})")

        logger.info(
            "Dataset pre-export validation completed successfully",
            extra={"num_rows": len(rows), "unique_repos": len({r.get('full_name') for r in rows})},
        )
