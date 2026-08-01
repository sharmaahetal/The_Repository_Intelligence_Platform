from dataclasses import dataclass
from datetime import datetime
from typing import Any

from app.logging import logger
from app.models.snapshot import RepositorySnapshot


@dataclass
class TargetLabels:
    """Empirical ground-truth labels for snapshot S(t_0) over horizon H."""

    snapshot_timestamp: str
    horizon_days: int
    is_growth: bool  # Stars increased >= 25%
    is_abandoned: bool  # Zero commits in forward window
    is_retained: bool  # Maintainer retention >= 50%
    star_growth_percent: float


class LabelGenerator:
    """Generates ground-truth targets by observing outcomes in forward window [t_0, t_0 + H]."""

    def generate_labels(
        self,
        snapshot_t0: RepositorySnapshot | dict[str, Any],
        snapshot_future: RepositorySnapshot | dict[str, Any],
        horizon_days: int = 180,
    ) -> TargetLabels:
        """Computes empirical labels by comparing S(t_0) with S(t_0 + H)."""
        stars_t0 = max(1.0, float(snapshot_t0.get("stars_count", 0)))
        stars_future = float(snapshot_future.get("stars_count", 0))

        star_growth_pct = round(((stars_future - stars_t0) / stars_t0) * 100.0, 2)
        is_growth = star_growth_pct >= 25.0

        # Abandonment check: zero pushes recorded in forward window
        pushed_at_t0 = snapshot_t0.get("pushed_at")
        pushed_at_future = snapshot_future.get("pushed_at")
        is_abandoned = (pushed_at_t0 == pushed_at_future) and (pushed_at_t0 is not None)

        # Maintainer retention check: proxy from activity continuity
        is_retained = not is_abandoned

        raw_ts = snapshot_t0.get("snapshot_timestamp", "")
        ts_str = raw_ts.isoformat() if isinstance(raw_ts, datetime) else str(raw_ts)

        labels = TargetLabels(
            snapshot_timestamp=ts_str,
            horizon_days=horizon_days,
            is_growth=is_growth,
            is_abandoned=is_abandoned,
            is_retained=is_retained,
            star_growth_percent=star_growth_pct,
        )

        logger.info(
            "Generated target labels for repository snapshot",
            extra={
                "full_name": snapshot_t0.get("full_name"),
                "horizon_days": horizon_days,
                "is_growth": is_growth,
                "star_growth_percent": star_growth_pct,
                "is_abandoned": is_abandoned,
            },
        )
        return labels
