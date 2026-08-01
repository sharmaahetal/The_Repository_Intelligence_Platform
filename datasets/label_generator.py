from dataclasses import dataclass
from datetime import datetime

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
        snapshot_t0: RepositorySnapshot,
        snapshot_future: RepositorySnapshot,
        horizon_days: int = 180,
    ) -> TargetLabels:
        """Computes empirical labels by comparing S(t_0) with S(t_0 + H)."""
        if not isinstance(snapshot_t0, RepositorySnapshot) or not isinstance(snapshot_future, RepositorySnapshot):
            raise TypeError("generate_labels requires RepositorySnapshot instances for both t0 and future snapshots.")

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

        ts_str = snapshot_t0.snapshot_timestamp.isoformat() if isinstance(snapshot_t0.snapshot_timestamp, datetime) else str(snapshot_t0.snapshot_timestamp)

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
                "full_name": snapshot_t0.full_name,
                "horizon_days": horizon_days,
                "is_growth": is_growth,
                "star_growth_percent": star_growth_pct,
                "is_abandoned": is_abandoned,
            },
        )
        return labels
