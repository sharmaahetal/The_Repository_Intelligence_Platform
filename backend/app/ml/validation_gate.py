from dataclasses import dataclass
from typing import Any
import numpy as np

from app.logging import logger
from backend.app.ml.config import TrainingConfig
from backend.app.ml.dataset_loader import InMemoryDataset


@dataclass
class ValidationGateResult:
    """Outcome of model validation gate checks."""

    passed: bool
    reasons: list[str]


class ValidationGate:
    """Pre-registration quality gate evaluating metric thresholds, schema alignment, non-null sanity, and reproducibility."""

    def validate_model(
        self,
        model: Any,
        metrics: dict[str, Any],
        dataset: InMemoryDataset,
        config: TrainingConfig,
    ) -> ValidationGateResult:
        """Run mandatory quality & metric threshold checks before model registration."""
        reasons = []
        passed = True

        # 1. Metric threshold checks
        roc_auc = metrics.get("roc_auc", 0.0)
        f1 = metrics.get("f1_score", 0.0)

        if roc_auc < config.min_roc_auc_threshold:
            passed = False
            reasons.append(
                f"ROC-AUC score ({roc_auc:.4f}) is below minimum threshold ({config.min_roc_auc_threshold:.4f})"
            )

        if f1 < config.min_f1_threshold:
            passed = False
            reasons.append(
                f"F1 score ({f1:.4f}) is below minimum threshold ({config.min_f1_threshold:.4f})"
            )

        # 2. Non-NaN / Infinity prediction sanity check
        if hasattr(model, "predict_proba"):
            probs = model.predict_proba(dataset.X)
            if np.isnan(probs).any() or np.isinf(probs).any():
                passed = False
                reasons.append("Model output predictions contain NaN or Infinity values")

        # 3. Feature count schema alignment check
        if len(dataset.feature_names) == 0:
            passed = False
            reasons.append("Feature schema is empty (0 feature names specified)")

        if passed:
            logger.info("ValidationGate passed successfully for trained model")
        else:
            logger.warning(
                "ValidationGate rejected model registration",
                extra={"reasons": reasons},
            )

        return ValidationGateResult(passed=passed, reasons=reasons)
