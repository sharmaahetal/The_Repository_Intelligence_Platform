from typing import Any
from app.logging import logger


class ExperimentTracker:
    """Abstract experiment tracking interface logging parameters, metrics, and artifacts."""

    def __init__(self, experiment_name: str = "repository_growth_experiment"):
        self.experiment_name = experiment_name
        self.params: dict[str, Any] = {}
        self.metrics: dict[str, float] = {}
        self.artifacts: list[str] = []

    def log_param(self, key: str, value: Any) -> None:
        """Log hyper-parameter or configuration setting."""
        self.params[key] = value
        logger.info("Logged experiment param", extra={"key": key, "value": str(value)})

    def log_metric(self, key: str, value: float) -> None:
        """Log numerical metric value."""
        self.metrics[key] = float(value)
        logger.info("Logged experiment metric", extra={"key": key, "value": value})

    def log_artifact(self, artifact_path: str) -> None:
        """Log saved artifact path."""
        self.artifacts.append(artifact_path)
        logger.info("Logged experiment artifact", extra={"artifact_path": artifact_path})
