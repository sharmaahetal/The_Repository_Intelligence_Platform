from backend.app.logging import logger
from ml.inference.predictor import ForecastPrediction


class NarrativeSynthesizer:
    """Translates ML probabilities and metrics into natural language narrative synthesis."""

    def synthesize(self, owner: str, repo: str, prediction: ForecastPrediction) -> str:
        """Constructs human-readable narrative string from prediction outputs."""
        horizon = prediction.prediction_horizon_days
        growth_pct = int(round(prediction.growth_probability * 100))
        abandon_pct = int(round(prediction.abandonment_probability * 100))
        retention_pct = int(round(prediction.maintainer_retention_probability * 100))

        if growth_pct >= 70:
            growth_trend = "likely to continue growing strongly"
        elif growth_pct >= 40:
            growth_trend = "expected to maintain steady development"
        else:
            growth_trend = "experiencing a growth slowdown"

        narrative = (
            f"This repository ({owner}/{repo}) is {growth_trend} over the next {horizon} days "
            f"with a {growth_pct}% growth probability and a {retention_pct}% "
            f"maintainer retention rate. Abandonment risk remains low at {abandon_pct}%."
        )

        logger.info(f"Synthesized report narrative for {owner}/{repo}")
        return narrative
