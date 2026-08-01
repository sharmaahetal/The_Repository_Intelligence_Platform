from dataclasses import dataclass

from backend.app.logging import logger
from ml.inference.predictor import ForecastPrediction


@dataclass
class ProductReportData:
    """Product-level intelligence report derived from ML probabilities."""

    health_index: int
    growth_probability: float
    abandonment_probability: float
    maintainer_retention_probability: float


class ForecastReportGenerator:
    """Product service layer deriving user-facing metrics from ML predictions."""

    def generate_report_data(self, prediction: ForecastPrediction) -> ProductReportData:
        """Derives deterministic Health Index from ML probabilities."""
        growth = prediction.growth_probability
        abandon = prediction.abandonment_probability
        retention = prediction.maintainer_retention_probability

        # Product-level Health Index formula: H in [0, 100]
        raw_health = (35.0 * retention) + (35.0 * (1.0 - abandon)) + (30.0 * growth)
        health_index = max(0, min(100, int(round(raw_health))))

        logger.info(f"Derived Product Health Index: {health_index} / 100")
        return ProductReportData(
            health_index=health_index,
            growth_probability=growth,
            abandonment_probability=abandon,
            maintainer_retention_probability=retention,
        )
