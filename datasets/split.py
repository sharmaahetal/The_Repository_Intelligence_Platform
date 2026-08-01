from datetime import datetime
from typing import Any

from backend.app.logging import logger


class ChronologicalSplitter:
    """Splits time-series datasets strictly based on snapshot_time boundaries to prevent temporal data leakage."""

    def split_dataset(
        self,
        rows: list[dict[str, Any]],
        val_start_time: datetime,
        test_start_time: datetime,
    ) -> dict[str, list[dict[str, Any]]]:
        """Chronologically partitions dataset rows into train, validation, and test sets.

        `val_start_time` must be strictly earlier than `test_start_time`.
        """
        if val_start_time >= test_start_time:
            raise ValueError(
                f"Chronological split error: val_start_time ({val_start_time.isoformat()}) "
                f"must be strictly earlier than test_start_time ({test_start_time.isoformat()})."
            )

        train_rows: list[dict[str, Any]] = []
        val_rows: list[dict[str, Any]] = []
        test_rows: list[dict[str, Any]] = []

        for row in rows:
            raw_ts = row.get("snapshot_time") or row.get("snapshot_timestamp")
            if isinstance(raw_ts, datetime):
                dt = raw_ts
            elif isinstance(raw_ts, str):
                dt = datetime.fromisoformat(raw_ts)
            else:
                raise TypeError(f"Invalid timestamp type for row split: {type(raw_ts)}")

            if dt < val_start_time:
                train_rows.append(row)
            elif dt < test_start_time:
                val_rows.append(row)
            else:
                test_rows.append(row)

        logger.info(
            "Chronological dataset split completed",
            extra={
                "total_rows": len(rows),
                "train_count": len(train_rows),
                "val_count": len(val_rows),
                "test_count": len(test_rows),
            },
        )

        return {
            "train": train_rows,
            "validation": val_rows,
            "test": test_rows,
        }
