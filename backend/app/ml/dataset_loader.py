from dataclasses import dataclass
from datetime import datetime
from typing import Any

import numpy as np


@dataclass
class InMemoryDataset:
    """In-memory dataset container decoupling model training from file I/O operations."""

    X: np.ndarray
    y: np.ndarray
    feature_names: list[str]
    snapshot_times: list[datetime]
    full_names: list[str]

    def __len__(self) -> int:
        return len(self.y)


class DatasetLoader:
    """Loader converting raw dataset rows or pandas DataFrames into InMemoryDataset containers."""

    def load_from_rows(
        self,
        rows: list[dict[str, Any]],
        feature_names: list[str],
        target_name: str = "is_growth",
    ) -> InMemoryDataset:
        """Convert a list of dataset dictionaries into an InMemoryDataset."""
        if not rows:
            raise ValueError("Cannot load empty dataset rows.")

        X_list = []
        y_list = []
        snapshot_times = []
        full_names = []

        for row in rows:
            feat_vector = [float(row.get(fname, 0.0)) for fname in feature_names]
            target_val = 1.0 if bool(row.get(target_name, False)) else 0.0

            raw_ts = row.get("snapshot_time") or row.get("snapshot_timestamp")
            if isinstance(raw_ts, datetime):
                dt = raw_ts
            elif isinstance(raw_ts, str):
                dt = datetime.fromisoformat(raw_ts)
            else:
                dt = datetime.now()

            X_list.append(feat_vector)
            y_list.append(target_val)
            snapshot_times.append(dt)
            full_names.append(str(row.get("full_name", "unknown")))

        return InMemoryDataset(
            X=np.array(X_list, dtype=np.float32),
            y=np.array(y_list, dtype=np.float32),
            feature_names=feature_names,
            snapshot_times=snapshot_times,
            full_names=full_names,
        )
