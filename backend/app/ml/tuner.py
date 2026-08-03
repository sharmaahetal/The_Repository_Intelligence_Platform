import itertools
from typing import Any

from pydantic import BaseModel, ConfigDict, Field

from backend.app.logging import logger
from backend.app.ml.config import ModelConfig
from backend.app.ml.dataset_loader import InMemoryDataset
from backend.app.ml.evaluator import ModelEvaluator
from backend.app.ml.trainer import XGBoostTrainer


class TuningResult(BaseModel):
    """Container holding hyperparameter tuning search results."""

    model_config = ConfigDict(frozen=True)

    best_config: ModelConfig
    best_metric_score: float
    total_trials: int
    trials: list[dict[str, Any]] = Field(default_factory=list)


class HyperparameterTuner:
    """Executes hyperparameter grid search across candidate spaces to select optimal ModelConfig."""

    def __init__(
        self,
        trainer: XGBoostTrainer | None = None,
        evaluator: ModelEvaluator | None = None,
    ) -> None:
        self.trainer = trainer or XGBoostTrainer()
        self.evaluator = evaluator or ModelEvaluator()

    def tune(
        self,
        dataset: InMemoryDataset,
        param_grid: dict[str, list[Any]] | None = None,
        target_metric: str = "roc_auc",
    ) -> TuningResult:
        """Evaluates hyperparameter candidates against dataset and selects optimal candidate config."""
        grid = param_grid or {
            "max_depth": [3, 6],
            "learning_rate": [0.05, 0.1],
            "n_estimators": [50, 100],
        }

        keys, values = zip(*grid.items(), strict=True)
        combinations = [dict(zip(keys, v, strict=True)) for v in itertools.product(*values)]

        trials = []
        best_score = -float("inf")
        best_config = ModelConfig()

        logger.info(
            "Starting hyperparameter tuning grid search",
            extra={"num_candidates": len(combinations), "target_metric": target_metric},
        )

        for i, params in enumerate(combinations):
            cfg = ModelConfig(**params)
            model = self.trainer.train(dataset=dataset, config=cfg)
            metrics = self.evaluator.evaluate(model=model, test_dataset=dataset)

            score = metrics.get(target_metric, 0.0)
            trial_record = {
                "trial": i + 1,
                "params": params,
                "metrics": metrics,
                "score": score,
            }
            trials.append(trial_record)

            if score > best_score:
                best_score = score
                best_config = cfg

        logger.info(
            "Hyperparameter tuning completed",
            extra={"best_score": best_score, "total_trials": len(trials)},
        )

        return TuningResult(
            best_config=best_config,
            best_metric_score=best_score,
            total_trials=len(trials),
            trials=trials,
        )
