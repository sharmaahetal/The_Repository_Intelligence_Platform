import uuid
from datetime import UTC, datetime
from typing import Any

from pydantic import BaseModel, ConfigDict, Field

from backend.app.logging import logger


class ExperimentRun(BaseModel):
    """Pydantic model representing an immutable ML experiment run."""

    model_config = ConfigDict(frozen=True)

    experiment_id: str = Field(default_factory=lambda: f"exp_{uuid.uuid4().hex[:12]}")
    model_name: str = Field(default="rip-growth")
    model_type: str = Field(default="xgboost")
    parameters: dict[str, Any] = Field(default_factory=dict)
    metrics: dict[str, Any] = Field(default_factory=dict)
    dataset_version: str = Field(default="v1.0")
    dataset_hash: str = Field(default="")
    feature_schema_version: int = Field(default=1)
    artifacts_dir: str = Field(default="")
    status: str = Field(default="SUCCESS")  # 'SUCCESS', 'FAILED', 'WINNER'
    created_at: datetime = Field(default_factory=lambda: datetime.now(UTC))


class ExperimentRegistry:
    """Registry tracking all ML experiment executions, parameter configs, metrics, and winning artifacts."""

    def __init__(self) -> None:
        self._runs: list[ExperimentRun] = []
        self._winners: dict[str, str] = {}  # maps model_name -> winning experiment_id

    def register_experiment(self, run: ExperimentRun) -> ExperimentRun:
        """Register a completed ML experiment run."""
        self._runs.append(run)
        logger.info(
            "Registered experiment run in ExperimentRegistry",
            extra={
                "experiment_id": run.experiment_id,
                "model_name": run.model_name,
                "dataset_version": run.dataset_version,
            },
        )
        return run

    def list_experiments(self, model_name: str | None = None) -> list[ExperimentRun]:
        """List all experiment runs, optionally filtered by model_name."""
        if model_name:
            return [r for r in self._runs if r.model_name == model_name]
        return list(self._runs)

    def set_winner(self, experiment_id: str) -> ExperimentRun | None:
        """Promote an experiment run to be the winning model artifact for its model_name."""
        target_run = None
        for run in self._runs:
            if run.experiment_id == experiment_id:
                target_run = run
                break

        if target_run:
            self._winners[target_run.model_name] = experiment_id
            logger.info(
                "Promoted experiment run to WINNER",
                extra={"experiment_id": experiment_id, "model_name": target_run.model_name},
            )
        return target_run

    def get_winner(self, model_name: str) -> ExperimentRun | None:
        """Retrieve the winning experiment run for a given model_name."""
        winner_id = self._winners.get(model_name)
        if not winner_id:
            return None
        for run in self._runs:
            if run.experiment_id == winner_id:
                return run
        return None
