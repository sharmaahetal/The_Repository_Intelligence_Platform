from dataclasses import dataclass
from datetime import datetime

import numpy as np
from app.logging import logger
from backend.app.ml.dataset_loader import InMemoryDataset


@dataclass
class CrossValidationFold:
    """Represents a single chronological train/validation fold in walk-forward CV."""

    fold_index: int
    train_dataset: InMemoryDataset
    val_dataset: InMemoryDataset
    cutoff_time: datetime


class WalkForwardValidator:
    """Generates rolling-window time-series cross-validation folds strictly ordered by timestamp."""

    def generate_folds(
        self,
        dataset: InMemoryDataset,
        num_folds: int = 3,
    ) -> list[CrossValidationFold]:
        """Partitions InMemoryDataset into num_folds rolling time-series folds without overlap or future data leakage."""
        if len(dataset) < 4:
            raise ValueError(f"Insufficient dataset samples ({len(dataset)}) to construct {num_folds} folds.")

        sorted_indices = np.argsort(dataset.snapshot_times)
        X_sorted = dataset.X[sorted_indices]
        y_sorted = dataset.y[sorted_indices]
        times_sorted = [dataset.snapshot_times[i] for i in sorted_indices]
        names_sorted = [dataset.full_names[i] for i in sorted_indices]

        n = len(dataset)
        step = n // (num_folds + 1)
        folds = []

        for fold_i in range(1, num_folds + 1):
            train_end_idx = step * fold_i
            val_end_idx = min(n, train_end_idx + step)

            if train_end_idx >= n or train_end_idx == 0:
                break

            train_ds = InMemoryDataset(
                X=X_sorted[:train_end_idx],
                y=y_sorted[:train_end_idx],
                feature_names=dataset.feature_names,
                snapshot_times=times_sorted[:train_end_idx],
                full_names=names_sorted[:train_end_idx],
            )

            val_ds = InMemoryDataset(
                X=X_sorted[train_end_idx:val_end_idx],
                y=y_sorted[train_end_idx:val_end_idx],
                feature_names=dataset.feature_names,
                snapshot_times=times_sorted[train_end_idx:val_end_idx],
                full_names=names_sorted[train_end_idx:val_end_idx],
            )

            cutoff_time = times_sorted[train_end_idx - 1]

            # Verify no train/val timestamp overlap
            max_train_time = max(train_ds.snapshot_times)
            min_val_time = min(val_ds.snapshot_times)
            if max_train_time > min_val_time:
                raise ValueError(
                    f"Temporal leakage detected in Fold #{fold_i}: "
                    f"Max train time ({max_train_time}) > Min val time ({min_val_time})"
                )

            folds.append(
                CrossValidationFold(
                    fold_index=fold_i,
                    train_dataset=train_ds,
                    val_dataset=val_ds,
                    cutoff_time=cutoff_time,
                )
            )

        logger.info(
            "Generated walk-forward time-series cross-validation folds",
            extra={"num_folds_created": len(folds)},
        )
        return folds
