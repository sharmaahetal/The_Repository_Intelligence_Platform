import json
from pathlib import Path
from typing import Any


class ModelRegistryManager:
    """Production Model Registry Manager for tracking versioned ML artifacts."""

    def __init__(self, registry_dir: str | Path | None = None):
        if registry_dir is None:
            self.registry_dir = Path(__file__).parent / "manifests"
        else:
            self.registry_dir = Path(registry_dir)
        self.registry_dir.mkdir(parents=True, exist_ok=True)

    def register_model(
        self,
        model_id: str,
        model_type: str,
        prediction_horizon_days: int,
        snapshot_version: str,
        feature_version: str,
        dataset_version: str,
        git_commit: str,
        metrics: dict[str, float],
    ) -> Path:
        manifest_payload = {
            "model_id": model_id,
            "model_type": model_type,
            "prediction_horizon_days": prediction_horizon_days,
            "snapshot_version": snapshot_version,
            "feature_version": feature_version,
            "dataset_version": dataset_version,
            "git_commit": git_commit,
            "metrics": metrics,
        }

        target_file = self.registry_dir / f"{model_id}.json"
        with open(target_file, "w", encoding="utf-8") as f:
            json.dump(manifest_payload, f, indent=2)

        return target_file

    def load_manifest(self, model_id: str) -> dict[str, Any]:
        target_file = self.registry_dir / f"{model_id}.json"
        if not target_file.exists():
            raise FileNotFoundError(f"Model manifest not found: {target_file}")

        with open(target_file, "r", encoding="utf-8") as f:
            return json.load(f)
