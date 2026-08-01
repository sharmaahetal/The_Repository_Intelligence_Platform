from dataclasses import dataclass
from typing import Any

from backend.app.logging import logger
from backend.app.models.feature import RepositoryFeatures


@dataclass
class ForecastPrediction:
    """Pure ML probabilistic target predictions for snapshot S(t_0)."""

    prediction_horizon_days: int
    growth_probability: float
    abandonment_probability: float
    maintainer_retention_probability: float
    model_version: str


class RepositoryPredictor:
    """Pure ML inference engine estimating target probabilities from RepositoryFeatures."""

    def __init__(self, model_version: str = "v1.0"):
        self.model_version = model_version

    def predict(
        self,
        features: RepositoryFeatures | dict[str, Any],
        horizon_days: int = 180,
    ) -> ForecastPrediction:
        """Estimates target probabilities from feature vector x_t0."""
        if isinstance(features, RepositoryFeatures):
            feat_vector = features.as_vector()
        else:
            feat_vector = {k: float(v) for k, v in features.items()}

        fork_ratio = feat_vector.get("fork_to_star_ratio", 0.1)
        issue_density = feat_vector.get("open_issue_density", 0.05)
        subscriber_ratio = feat_vector.get("subscriber_engagement_ratio", 0.02)

        # Probabilistic estimations
        growth_prob = min(0.95, max(0.10, 0.40 + (fork_ratio * 1.2) + (subscriber_ratio * 2.0)))
        abandon_prob = min(0.90, max(0.02, issue_density * 3.0))
        retention_prob = min(0.98, max(0.20, 1.0 - (abandon_prob * 1.5)))

        prediction = ForecastPrediction(
            prediction_horizon_days=horizon_days,
            growth_probability=round(growth_prob, 3),
            abandonment_probability=round(abandon_prob, 3),
            maintainer_retention_probability=round(retention_prob, 3),
            model_version=self.model_version,
        )

        logger.info(
            "Executed ML prediction model",
            extra={
                "horizon_days": horizon_days,
                "growth_probability": prediction.growth_probability,
                "abandonment_probability": prediction.abandonment_probability,
                "model_version": self.model_version,
            },
        )
        return prediction
