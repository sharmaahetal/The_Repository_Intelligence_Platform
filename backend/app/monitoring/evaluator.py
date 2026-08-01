from app.logging import logger
from app.monitoring.tracker import LoggedPredictionRecord
from datasets.label_generator import TargetLabels


class OutcomeEvaluator:
    """Evaluates prediction error & calibration drift once horizon H expires [t_0 + H]."""

    def evaluate_prediction_error(
        self,
        logged_record: LoggedPredictionRecord,
        actual_labels: TargetLabels,
    ) -> dict[str, float]:
        """Calculates Brier Score calibration error."""
        is_growth = actual_labels.get("is_growth")
        is_abandoned = actual_labels.get("is_abandoned")

        growth_actual = 1.0 if is_growth else 0.0
        abandon_actual = 1.0 if is_abandoned else 0.0

        # Brier Score = (predicted_prob - actual_outcome)^2
        growth_brier_error = (logged_record.growth_probability - growth_actual) ** 2
        abandon_brier_error = (logged_record.abandonment_probability - abandon_actual) ** 2

        logger.info(
            "Evaluated prediction drift & calibration score",
            extra={
                "prediction_id": logged_record.prediction_id,
                "growth_brier_error": round(growth_brier_error, 4),
                "abandon_brier_error": round(abandon_brier_error, 4),
            },
        )

        return {
            "growth_brier_error": round(growth_brier_error, 4),
            "abandon_brier_error": round(abandon_brier_error, 4),
        }
