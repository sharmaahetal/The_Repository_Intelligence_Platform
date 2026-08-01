import tempfile
from datetime import UTC, datetime

import numpy as np
import pytest

from backend.app.ml.config import ModelConfig, TrainingConfig
from backend.app.ml.dataset_loader import DatasetLoader
from backend.app.ml.evaluator import ModelEvaluator
from backend.app.ml.explainability.shap_service import ExplainabilityService
from backend.app.ml.registry.model_registry import ModelRegistry
from backend.app.ml.training_service import TrainingService
from backend.app.ml.validation_gate import ValidationGate
from backend.app.ml.walk_forward import WalkForwardValidator


@pytest.fixture
def sample_dataset_rows():
    rows = []
    feature_names = ["star_density_index", "fork_to_star_ratio", "open_issue_density"]

    for i in range(30):
        t = datetime(2023 + (i // 10), (i % 12) + 1, 1, tzinfo=UTC)
        is_growth = (i % 2) == 0
        rows.append(
            {
                "full_name": f"org/repo_{i}",
                "snapshot_time": t.isoformat(),
                "star_density_index": float(i * 1.5),
                "fork_to_star_ratio": float(0.1 + (i * 0.02)),
                "open_issue_density": float(0.05 + (i * 0.01)),
                "is_growth": is_growth,
            }
        )
    return rows, feature_names


def test_xgboost_trainer_seed_determinism(sample_dataset_rows):
    rows, feature_names = sample_dataset_rows
    loader = DatasetLoader()
    ds = loader.load_from_rows(rows, feature_names)

    from backend.app.ml.trainer import XGBoostTrainer

    trainer = XGBoostTrainer()

    cfg1 = ModelConfig(random_seed=42)
    cfg2 = ModelConfig(random_seed=42)

    m1 = trainer.train(ds, cfg1)
    m2 = trainer.train(ds, cfg2)

    p1 = m1.predict(ds.X)
    p2 = m2.predict(ds.X)

    np.testing.assert_array_equal(p1, p2)


def test_validation_gate_thresholds(sample_dataset_rows):
    rows, feature_names = sample_dataset_rows
    loader = DatasetLoader()
    ds = loader.load_from_rows(rows, feature_names)

    gate = ValidationGate()
    t_config_strict = TrainingConfig(min_roc_auc_threshold=0.99, min_f1_threshold=0.99)
    t_config_lenient = TrainingConfig(min_roc_auc_threshold=0.10, min_f1_threshold=0.10)

    from backend.app.ml.trainer import XGBoostTrainer

    trainer = XGBoostTrainer()
    model = trainer.train(ds, ModelConfig())

    evaluator = ModelEvaluator()
    metrics = evaluator.evaluate(model, ds)

    result_strict = gate.validate_model(model, metrics, ds, t_config_strict)
    assert result_strict.passed is False

    result_lenient = gate.validate_model(model, metrics, ds, t_config_lenient)
    assert result_lenient.passed is True


def test_model_registry_save_load_predict(sample_dataset_rows):
    rows, feature_names = sample_dataset_rows
    loader = DatasetLoader()
    ds = loader.load_from_rows(rows, feature_names)

    from backend.app.ml.trainer import XGBoostTrainer

    trainer = XGBoostTrainer()
    m_config = ModelConfig(model_name="test_growth_model")
    t_config = TrainingConfig()

    model = trainer.train(ds, m_config)

    with tempfile.TemporaryDirectory() as tmp_dir:
        registry = ModelRegistry(base_registry_dir=tmp_dir)
        v_dir = registry.register_model(
            model=model,
            model_config=m_config,
            training_config=t_config,
            metrics={"roc_auc": 0.85, "f1_score": 0.80},
            feature_names=feature_names,
        )

        assert v_dir.exists()
        assert (v_dir / "metadata.json").exists()
        assert (v_dir / "feature_schema.json").exists()

        # Load back
        loaded_model, feature_schema = registry.load_model("test_growth_model", version="v1")
        assert feature_schema["num_features"] == len(feature_names)

        p_orig = model.predict(ds.X)
        p_loaded = loaded_model.predict(ds.X)
        np.testing.assert_array_equal(p_orig, p_loaded)


def test_walk_forward_validator(sample_dataset_rows):
    rows, feature_names = sample_dataset_rows
    loader = DatasetLoader()
    ds = loader.load_from_rows(rows, feature_names)

    wf_validator = WalkForwardValidator()
    folds = wf_validator.generate_folds(ds, num_folds=3)

    assert len(folds) >= 2
    for fold in folds:
        # Verify no temporal overlap: max train time < min val time
        max_train = max(fold.train_dataset.snapshot_times)
        min_val = min(fold.val_dataset.snapshot_times)
        assert max_train <= min_val


def test_explainability_service_dimensions(sample_dataset_rows):
    rows, feature_names = sample_dataset_rows
    loader = DatasetLoader()
    ds = loader.load_from_rows(rows, feature_names)

    from backend.app.ml.trainer import XGBoostTrainer

    trainer = XGBoostTrainer()
    model = trainer.train(ds, ModelConfig())

    explainability = ExplainabilityService()
    importances = explainability.compute_feature_importances(model, ds)

    assert len(importances) == len(feature_names)
    for fname in feature_names:
        assert fname in importances


def test_training_service_end_to_end(sample_dataset_rows):
    rows, feature_names = sample_dataset_rows
    with tempfile.TemporaryDirectory() as tmp_dir:
        registry = ModelRegistry(base_registry_dir=tmp_dir)
        service = TrainingService(registry=registry)

        t_config = TrainingConfig(min_roc_auc_threshold=0.10, min_f1_threshold=0.10)
        v_dir, metrics = service.train_and_register_pipeline(
            dataset_rows=rows,
            feature_names=feature_names,
            training_config=t_config,
        )

        assert v_dir is not None
        assert v_dir.exists()
        assert "roc_auc" in metrics
