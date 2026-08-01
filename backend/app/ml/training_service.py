from pathlib import Path
from typing import Any

from app.logging import logger
from backend.app.ml.config import ModelConfig, TrainingConfig
from backend.app.ml.dataset_loader import DatasetLoader
from backend.app.ml.evaluator import ModelEvaluator
from backend.app.ml.explainability.shap_service import ExplainabilityService
from backend.app.ml.registry.model_registry import ModelRegistry
from backend.app.ml.tracker import ExperimentTracker
from backend.app.ml.trainer import XGBoostTrainer
from backend.app.ml.validation_gate import ValidationGate


class TrainingService:
    """High-level application service orchestrating dataset loading, model training, evaluation, validation gating, model registration, and explainability."""

    def __init__(
        self,
        loader: DatasetLoader | None = None,
        trainer: XGBoostTrainer | None = None,
        evaluator: ModelEvaluator | None = None,
        gate: ValidationGate | None = None,
        registry: ModelRegistry | None = None,
        explainability: ExplainabilityService | None = None,
        tracker: ExperimentTracker | None = None,
    ):
        self.loader = loader or DatasetLoader()
        self.trainer = trainer or XGBoostTrainer()
        self.evaluator = evaluator or ModelEvaluator()
        self.gate = gate or ValidationGate()
        self.registry = registry or ModelRegistry()
        self.explainability = explainability or ExplainabilityService()
        self.tracker = tracker or ExperimentTracker()

    def train_and_register_pipeline(
        self,
        dataset_rows: list[dict[str, Any]],
        feature_names: list[str],
        model_config: ModelConfig | None = None,
        training_config: TrainingConfig | None = None,
    ) -> tuple[Path | None, dict[str, Any]]:
        """Orchestrates end-to-end training pipeline execution for dataset rows."""
        m_config = model_config or ModelConfig()
        t_config = training_config or TrainingConfig()

        logger.info(
            "Starting TrainingService execution pipeline",
            extra={"model_name": m_config.model_name, "num_rows": len(dataset_rows)},
        )

        # 1. Load dataset into in-memory container
        in_memory_ds = self.loader.load_from_rows(
            rows=dataset_rows,
            feature_names=feature_names,
            target_name=t_config.target_label_name,
        )

        # 2. Train model in-memory
        model = self.trainer.train(dataset=in_memory_ds, config=m_config)

        # 3. Evaluate model metrics
        metrics = self.evaluator.evaluate(model=model, test_dataset=in_memory_ds)

        # 4. Validation Gate Check
        gate_result = self.gate.validate_model(
            model=model,
            metrics=metrics,
            dataset=in_memory_ds,
            config=t_config,
        )

        if not gate_result.passed:
            logger.warning(
                "Model failed ValidationGate quality checks. Aborting registration.",
                extra={"reasons": gate_result.reasons},
            )
            return None, metrics

        # 5. Compute SHAP explainability feature importances
        shap_summary = self.explainability.compute_feature_importances(
            model=model, dataset=in_memory_ds
        )

        # 6. Register model artifacts
        version_dir = self.registry.register_model(
            model=model,
            model_config=m_config,
            training_config=t_config,
            metrics=metrics,
            feature_names=feature_names,
            shap_summary=shap_summary,
        )

        logger.info(
            "TrainingService execution completed successfully",
            extra={"registered_version_dir": str(version_dir)},
        )
        return version_dir, metrics
