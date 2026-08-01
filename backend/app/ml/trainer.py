from typing import Any

from backend.app.logging import logger
from backend.app.ml.config import ModelConfig
from backend.app.ml.dataset_loader import InMemoryDataset


class XGBoostTrainer:
    """Pure, deterministic in-memory model trainer operating strictly on InMemoryDataset instances."""

    def train(self, dataset: InMemoryDataset, config: ModelConfig) -> Any:
        """Trains XGBoost (or Scikit-Learn fallback) classifier on in-memory dataset with fixed random seed."""
        if len(dataset) == 0:
            raise ValueError("Cannot train on an empty dataset.")

        logger.info(
            "Starting model training",
            extra={
                "model_name": config.model_name,
                "num_samples": len(dataset),
                "num_features": len(dataset.feature_names),
                "random_seed": config.random_seed,
            },
        )

        try:
            import xgboost as xgb  # type: ignore

            model = xgb.XGBClassifier(
                n_estimators=config.n_estimators,
                max_depth=config.max_depth,
                learning_rate=config.learning_rate,
                subsample=config.subsample,
                colsample_bytree=config.colsample_bytree,
                random_state=config.random_seed,
                eval_metric="logloss",
            )
        except ImportError:
            logger.warning("XGBoost library not found. Falling back to Scikit-Learn GradientBoostingClassifier.")
            from sklearn.ensemble import GradientBoostingClassifier  # type: ignore

            model = GradientBoostingClassifier(
                n_estimators=config.n_estimators,
                max_depth=config.max_depth,
                learning_rate=config.learning_rate,
                random_state=config.random_seed,
            )

        model.fit(dataset.X, dataset.y)

        logger.info(
            "Completed model training successfully",
            extra={"model_name": config.model_name},
        )
        return model
