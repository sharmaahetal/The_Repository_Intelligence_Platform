from dataclasses import dataclass

from app.logging import logger


@dataclass
class ForecastPrediction:
    """Probabilistic predictions and derived health index for snapshot S(t_0)."""

    prediction_horizon_days: int
    growth_probability: float
    abandonment_probability: float
    maintainer_retention_probability: float
    derived_health_index: int
    model_version: str


class RepositoryPredictor:
    """Inference engine translating feature vectors into probabilistic forecasts."""

    def __init__(self, model_version: str = "v1.0"):
        self.model_version = model_version

    def predict(
        self,
        features: dict[str, float],
        horizon_days: int = 180,
    ) -> ForecastPrediction:
        """Computes probabilistic targets and derived health index from features."""
        # Baseline heuristic estimator (substituted by trained XGBoost weights)
        fork_ratio = features.get("fork_to_star_ratio", 0.1)
        issue_density = features.get("open_issue_density", 0.05)
        subscriber_ratio = features.get("subscriber_engagement_ratio", 0.02)

        # 1. Growth probability heuristic estimate
        growth_prob = min(0.95, max(0.10, 0.40 + (fork_ratio * 1.2) + (subscriber_ratio * 2.0)))

        # 2. Abandonment probability heuristic estimate
        abandon_prob = min(0.90, max(0.02, issue_density * 3.0))

        # 3. Maintainer retention probability heuristic estimate
        retention_prob = min(0.98, max(0.20, 1.0 - (abandon_prob * 1.5)))

        # 4. Deterministically derive Health Index H in [0, 100]
        raw_health = (
            (35.0 * retention_prob)
            + (35.0 * (1.0 - abandon_prob))
            + (30.0 * growth_prob)
        )
        health_index = max(0, min(100, int(round(raw_health))))

        prediction = ForecastPrediction(
            prediction_horizon_days=horizon_days,
            growth_probability=round(growth_prob, 3),
            abandonment_probability=round(abandon_prob, 3),
            maintainer_retention_probability=round(retention_prob, 3),
            derived_health_index=health_index,
            model_version=self.model_version,
        )

        logger.info(
            f"Forecast [H={horizon_days}d, Health={health_index}, "
            f"P(Growth)={prediction.growth_probability}, "
            f"P(Abandon)={prediction.abandonment_probability}]"
        )
        return prediction
