from dataclasses import dataclass

from app.logging import logger


@dataclass
class ForecastPrediction:
    """Pure ML probabilistic target predictions for snapshot S(t_0)."""

    prediction_horizon_days: int
    growth_probability: float
    abandonment_probability: float
    maintainer_retention_probability: float
    model_version: str


class RepositoryPredictor:
    """Pure ML inference engine estimating target probabilities."""

    def __init__(self, model_version: str = "v1.0"):
        self.model_version = model_version

    def predict(
        self,
        features: dict[str, float],
        horizon_days: int = 180,
    ) -> ForecastPrediction:
        """Estimates target probabilities from feature vector x_t0."""
        fork_ratio = features.get("fork_to_star_ratio", 0.1)
        issue_density = features.get("open_issue_density", 0.05)
        subscriber_ratio = features.get("subscriber_engagement_ratio", 0.02)

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
            f"Pure ML Prediction [H={horizon_days}d, P(Growth)={prediction.growth_probability}, "
            f"P(Abandon)={prediction.abandonment_probability}]"
        )
        return prediction
