import os
import tempfile

import pytest

from backend.app.ml.experiments import ExperimentRegistry, ExperimentRun
from backend.app.ml.reports import EvaluationReportGenerator
from backend.app.ml.schema_lock import FeatureSchemaLock, FeatureSchemaMismatchError
from datasets.export import DatasetExporter, DatasetManifest


def test_experiment_registry_winner_promotion():
    registry = ExperimentRegistry()

    run1 = ExperimentRun(
        model_name="rip-growth",
        parameters={"max_depth": 3, "learning_rate": 0.1},
        metrics={"roc_auc": 0.82},
        dataset_version="v1.0",
        dataset_hash="hash_111",
    )
    run2 = ExperimentRun(
        model_name="rip-growth",
        parameters={"max_depth": 6, "learning_rate": 0.05},
        metrics={"roc_auc": 0.88},
        dataset_version="v1.0",
        dataset_hash="hash_111",
    )

    registry.register_experiment(run1)
    registry.register_experiment(run2)

    assert len(registry.list_experiments("rip-growth")) == 2

    # Promote run2 to WINNER
    registry.set_winner(run2.experiment_id)
    winner = registry.get_winner("rip-growth")
    assert winner is not None
    assert winner.experiment_id == run2.experiment_id
    assert winner.metrics["roc_auc"] == 0.88


def test_dataset_exporter_sha256_content_hashing():
    exporter = DatasetExporter()
    rows = [
        {"full_name": "owner/repo1", "stars": 100, "label_growth": 1},
        {"full_name": "owner/repo2", "stars": 200, "label_growth": 0},
    ]

    with tempfile.TemporaryDirectory() as tmp_dir:
        parquet_path, manifest_path = exporter.export_dataset(
            rows=rows,
            output_dir=tmp_dir,
            dataset_version="v2.0",
        )

        assert os.path.exists(parquet_path)
        assert os.path.exists(manifest_path)

        with open(manifest_path, encoding="utf-8") as f:
            manifest_json = f.read()

        manifest = DatasetManifest.model_validate_json(manifest_json)
        assert manifest.dataset_version == "v2.0"
        assert len(manifest.dataset_hash) == 64  # Valid SHA-256 hex digest
        assert manifest.num_rows == 2


def test_feature_schema_lock_validation():
    lock = FeatureSchemaLock(
        model_name="rip-growth",
        schema_version=1,
        expected_features=["stars", "forks", "open_issues"],
    )

    # Valid schema
    lock.validate_schema(["stars", "forks", "open_issues", "extra_col"])

    # Invalid schema (missing open_issues)
    with pytest.raises(FeatureSchemaMismatchError, match="Missing required features"):
        lock.validate_schema(["stars", "forks"])


def test_evaluation_report_generator():
    generator = EvaluationReportGenerator()
    metrics = {"roc_auc": 0.87, "pr_auc": 0.81, "accuracy": 0.85}
    shap_summary = {"stars": 0.35, "forks": 0.22, "issues": 0.10}

    with tempfile.TemporaryDirectory() as tmp_dir:
        artifacts = generator.generate_report(
            output_dir=tmp_dir,
            metrics=metrics,
            shap_summary=shap_summary,
            model_name="rip-growth",
        )

        assert os.path.exists(artifacts["report_html"])
        assert os.path.exists(artifacts["metrics_json"])
        assert os.path.exists(artifacts["feature_importance_json"])

        with open(artifacts["report_html"], encoding="utf-8") as f:
            html = f.read()

        assert "ML Model Evaluation Report: rip-growth" in html
        assert "0.8700" in html
