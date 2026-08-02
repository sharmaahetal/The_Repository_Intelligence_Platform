from datetime import datetime
from enum import IntEnum
from typing import Any

from pydantic import BaseModel, ConfigDict, Field

from backend.app.logging import logger
from backend.app.models.snapshot import RepositorySnapshot


class PredictionHorizon(IntEnum):
    """Explicit prediction horizon choices in days to avoid magic numbers."""

    DAYS_30 = 30
    DAYS_90 = 90
    DAYS_180 = 180
    DAYS_365 = 365


class Label(BaseModel):
    """Immutable model representing a single versioned ground-truth target label with metadata."""

    model_config = ConfigDict(frozen=True)

    name: str
    value: float | int | bool
    dtype: str = Field(default="bool")  # 'bool', 'float32', 'int32'
    version: int = Field(default=1)
    description: str = Field(default="")

    @property
    def label_key(self) -> str:
        """Returns versioned label identifier, e.g., 'is_growth:v1'."""
        return f"{self.name}:v{self.version}"


class TargetLabels(BaseModel):
    """Immutable container holding empirical ground-truth target labels for snapshot S(t_0) over horizon H."""

    model_config = ConfigDict(frozen=True)

    schema_version: int = Field(default=1, frozen=True)
    snapshot_timestamp: datetime
    horizon: PredictionHorizon
    labels: dict[str, Label] = Field(default_factory=dict)

    def as_dict(self) -> dict[str, Any]:
        """Extract flat dictionary mapping label names to values for model training."""
        return {label.name: label.value for label in self.labels.values()}

    def get(self, name: str, default: Any = None) -> Any:
        """Convenience accessor for label values by name or label_key."""
        if name in self.labels:
            return self.labels[name].value
        for label in self.labels.values():
            if label.name == name:
                return label.value
        return default


class LabelGenerator:
    """Pure, deterministic generator computing ground-truth targets by observing outcomes in forward window [t_0, t_0 + H]."""

    def generate_labels(
        self,
        snapshot_t0: RepositorySnapshot,
        snapshot_future: RepositorySnapshot,
        horizon: PredictionHorizon = PredictionHorizon.DAYS_180,
    ) -> TargetLabels:
        """Computes empirical labels strictly by comparing S(t_0) with S(t_0 + H).

        Enforces strict temporal anti-leakage: snapshot_future.snapshot_timestamp MUST exceed snapshot_t0.snapshot_timestamp.
        """
        if not isinstance(snapshot_t0, RepositorySnapshot) or not isinstance(
            snapshot_future, RepositorySnapshot
        ):
            raise TypeError(
                "generate_labels requires RepositorySnapshot instances for both t0 and future snapshots."
            )

        # Temporal Causal Leakage Guard
        if snapshot_future.snapshot_timestamp <= snapshot_t0.snapshot_timestamp:
            raise ValueError(
                f"Temporal leakage detected: snapshot_future timestamp ({snapshot_future.snapshot_timestamp.isoformat()}) "
                f"must strictly exceed snapshot_t0 timestamp ({snapshot_t0.snapshot_timestamp.isoformat()})."
            )

        stars_t0 = max(1.0, float(snapshot_t0.stars_count))
        stars_future = float(snapshot_future.stars_count)

        star_growth_pct = round(((stars_future - stars_t0) / stars_t0) * 100.0, 2)
        is_growth = star_growth_pct >= 25.0

        # Abandonment check: zero pushes recorded in forward window
        pushed_at_t0 = snapshot_t0.pushed_at
        pushed_at_future = snapshot_future.pushed_at
        is_abandoned = (pushed_at_t0 == pushed_at_future) and (pushed_at_t0 is not None)

        # Maintainer retention check: proxy from activity continuity
        is_retained = not is_abandoned

        label_growth = Label(
            name="is_growth",
            value=is_growth,
            dtype="bool",
            version=1,
            description="Flag indicating star growth >= 25% over prediction horizon",
        )
        label_abandoned = Label(
            name="is_abandoned",
            value=is_abandoned,
            dtype="bool",
            version=1,
            description="Flag indicating zero push activity over prediction horizon",
        )
        label_retained = Label(
            name="is_retained",
            value=is_retained,
            dtype="bool",
            version=1,
            description="Flag indicating maintainer retention over prediction horizon",
        )
        label_growth_pct = Label(
            name="star_growth_percent",
            value=star_growth_pct,
            dtype="float32",
            version=1,
            description="Percentage star growth over prediction horizon",
        )

        labels_dict = {
            label_growth.label_key: label_growth,
            label_abandoned.label_key: label_abandoned,
            label_retained.label_key: label_retained,
            label_growth_pct.label_key: label_growth_pct,
        }

        target_labels = TargetLabels(
            schema_version=1,
            snapshot_timestamp=snapshot_t0.snapshot_timestamp,
            horizon=horizon,
            labels=labels_dict,
        )

        logger.info(
            "Generated target labels for repository snapshot",
            extra={
                "full_name": snapshot_t0.full_name,
                "horizon_days": int(horizon),
                "is_growth": is_growth,
                "star_growth_percent": star_growth_pct,
                "is_abandoned": is_abandoned,
            },
        )
        return target_labels
