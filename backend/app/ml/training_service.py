import json
from pathlib import Path
from typing import Any

from backend.app.logging import logger
from backend.app.ml.config import ModelConfig, TrainingConfig
from backend.app.ml.dataset_loader import DatasetLoader
from backend.app.ml.evaluator import ModelEvaluator
from backend.app.ml.experiments import ExperimentRegistry, ExperimentRun
from backend.app.ml.explainability.shap_service import ExplainabilityService
from backend.app.ml.manifest import TrainingManifest
from backend.app.ml.registry.model_registry import ModelRegistry
from backend.app.ml.reports import EvaluationReportGenerator
from backend.app.ml.schema_lock import FeatureSchemaLock
from backend.app.ml.tracker import ExperimentTracker
from backend.app.ml.trainer import XGBoostTrainer
from backend.app.ml.tuner import HyperparameterTuner
from backend.app.ml.validation_gate import ValidationGate


class TrainingService:
    """High-level application service orchestrating dataset loading, hyperparameter tuning, model training, evaluation, schema locking, report generation, and experiment registration."""

    def __init__(
        self,
        loader: DatasetLoader | None = None,
        trainer: XGBoostTrainer | None = None,
        evaluator: ModelEvaluator | None = None,
        gate: ValidationGate | None = None,
        registry: ModelRegistry | None = None,
        explainability: ExplainabilityService | None = None,
        tracker: ExperimentTracker | None = None,
        experiments: ExperimentRegistry | None = None,
        reports: EvaluationReportGenerator | None = None,
        tuner: HyperparameterTuner | None = None,
    ):
        self.loader = loader or DatasetLoader()
        self.trainer = trainer or XGBoostTrainer()
        self.evaluator = evaluator or ModelEvaluator()
        self.gate = gate or ValidationGate()
        self.registry = registry or ModelRegistry()
        self.explainability = explainability or ExplainabilityService()
        self.tracker = tracker or ExperimentTracker()
        self.experiments = experiments or ExperimentRegistry()
        self.reports = reports or EvaluationReportGenerator()
        self.tuner = tuner or HyperparameterTuner(trainer=self.trainer, evaluator=self.evaluator)

    def train_and_register_pipeline(
        self,
        dataset_rows: list[dict[str, Any]],
        feature_names: list[str],
        model_config: ModelConfig | None = None,
        training_config: TrainingConfig | None = None,
        dataset_version: str = "v1.0",
        dataset_hash: str = "",
        param_grid: dict[str, list[Any]] | None = None,
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

        # 2. Hyperparameter Search / Tuning (if param_grid provided)
        if param_grid:
            tuning_result = self.tuner.tune(dataset=in_memory_ds, param_grid=param_grid)
            m_config = tuning_result.best_config
            logger.info("Selected optimal Hyperparameters", extra={"best_config": m_config.model_dump()})

        # 3. Train model in-memory
        model = self.trainer.train(dataset=in_memory_ds, config=m_config)

        # 4. Evaluate model metrics
        metrics = self.evaluator.evaluate(model=model, test_dataset=in_memory_ds)

        # 5. Validation Gate Check
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
            # Register failed run in ExperimentRegistry
            failed_run = ExperimentRun(
                model_name=m_config.model_name,
                parameters=m_config.model_dump(),
                metrics=metrics,
                dataset_version=dataset_version,
                dataset_hash=dataset_hash,
                status="FAILED",
            )
            self.experiments.register_experiment(failed_run)
            return None, metrics

        # 6. Compute SHAP explainability feature importances
        shap_summary = self.explainability.compute_feature_importances(
            model=model, dataset=in_memory_ds
        )

        # 7. Register model artifacts
        version_dir = self.registry.register_model(
            model=model,
            model_config=m_config,
            training_config=t_config,
            metrics=metrics,
            feature_names=feature_names,
            shap_summary=shap_summary,
        )

        # 8. Create & Save Feature Schema Lock
        schema_lock = FeatureSchemaLock(
            model_name=m_config.model_name,
            schema_version=1,
            expected_features=feature_names,
        )
        lock_path = version_dir / "schema_lock.json"
        with open(lock_path, "w", encoding="utf-8") as f:
            f.write(schema_lock.model_dump_json(indent=2))

        # 9. Create & Save Training Manifest
        manifest = TrainingManifest(
            model_name=m_config.model_name,
            model_version=version_dir.name,
            dataset_version=dataset_version,
            dataset_hash=dataset_hash,
            parameters=m_config.model_dump(),
            metrics=metrics,
            feature_names=feature_names,
        )
        manifest_path = version_dir / "manifest.json"
        with open(manifest_path, "w", encoding="utf-8") as f:
            f.write(manifest.model_dump_json(indent=2))

        # 10. Generate Evaluation Report (HTML & JSON)
        eval_dir = str(version_dir / "evaluation")
        self.reports.generate_report(
            output_dir=eval_dir,
            metrics=metrics,
            shap_summary=shap_summary,
            model_name=m_config.model_name,
        )

        # 11. Register in ExperimentRegistry and promote to WINNER
        exp_run = ExperimentRun(
            model_name=m_config.model_name,
            parameters=m_config.model_dump(),
            metrics=metrics,
            dataset_version=dataset_version,
            dataset_hash=dataset_hash,
            artifacts_dir=str(version_dir),
            status="SUCCESS",
        )
        self.experiments.register_experiment(exp_run)
        self.experiments.set_winner(exp_run.experiment_id)

        logger.info(
            "TrainingService execution completed successfully",
            extra={
                "registered_version_dir": str(version_dir),
                "experiment_id": exp_run.experiment_id,
            },
        )
        return version_dir, metrics
