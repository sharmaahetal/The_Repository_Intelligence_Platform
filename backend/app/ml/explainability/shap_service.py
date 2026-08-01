from typing import Any
import numpy as np

from app.logging import logger
from backend.app.ml.dataset_loader import InMemoryDataset


class ExplainabilityService:
    """Independent service computing post-training SHAP feature importances and summary metrics."""

    def compute_feature_importances(
        self, model: Any, dataset: InMemoryDataset
    ) -> dict[str, float]:
        """Computes feature importance values for trained model."""
        if len(dataset) == 0:
            raise ValueError("Cannot compute feature importances on empty dataset.")

        feature_names = dataset.feature_names
        importances_dict: dict[str, float] = {}

        # 1. Try SHAP TreeExplainer if shap library is available
        try:
            import shap  # type: ignore

            explainer = shap.TreeExplainer(model)
            shap_values = explainer.shap_values(dataset.X)

            if isinstance(shap_values, list):
                # For classification, take class 1 SHAP values
                shap_matrix = np.abs(shap_values[1]).mean(axis=0)
            else:
                shap_matrix = np.abs(shap_values).mean(axis=0)

            for fname, score in zip(feature_names, shap_matrix):
                importances_dict[fname] = round(float(score), 4)

            logger.info("Computed SHAP feature importances successfully")
            return importances_dict

        except Exception as exc:
            logger.info(
                "SHAP explainer unavailable, falling back to model feature importances",
                extra={"reason": str(exc)},
            )

        # 2. Fallback to model.feature_importances_ if available
        if hasattr(model, "feature_importances_"):
            scores = model.feature_importances_
            for fname, score in zip(feature_names, scores):
                importances_dict[fname] = round(float(score), 4)
        else:
            # Equal weight fallback
            for fname in feature_names:
                importances_dict[fname] = round(1.0 / len(feature_names), 4)

        return importances_dict
