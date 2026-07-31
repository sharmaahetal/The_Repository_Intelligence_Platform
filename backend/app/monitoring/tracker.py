from dataclasses import dataclass
from datetime import UTC, datetime

from app.logging import logger

from ml.inference.predictor import ForecastPrediction


@dataclass
class LoggedPredictionRecord:
    """Persistent record of live prediction for post-horizon verification."""

    prediction_id: str
    owner: str
    repo: str
    snapshot_timestamp: str
    horizon_days: int
    growth_probability: float
    abandonment_probability: float
    maintainer_retention_probability: float
    model_version: str


class PredictionTracker:
    """Logs live predictions into monitoring storage."""

    def log_prediction(
        self,
        owner: str,
        repo: str,
        prediction: ForecastPrediction,
    ) -> LoggedPredictionRecord:
        """Persists live prediction for future 180-day outcome evaluation."""
        now = datetime.now(UTC)
        record = LoggedPredictionRecord(
            prediction_id=f"{owner}-{repo}-{now.strftime('%Y%m%d%H%M%S')}",
            owner=owner,
            repo=repo,
            snapshot_timestamp=now.isoformat(),
            horizon_days=prediction.prediction_horizon_days,
            growth_probability=prediction.growth_probability,
            abandonment_probability=prediction.abandonment_probability,
            maintainer_retention_probability=prediction.maintainer_retention_probability,
            model_version=prediction.model_version,
        )

        logger.info(
            f"Logged prediction [ID={record.prediction_id}] for {owner}/{repo} "
            f"over {record.horizon_days}d horizon for future calibration verification."
        )
        return record
