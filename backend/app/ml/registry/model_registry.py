import hashlib
import json
import os
import shutil
import subprocess
import sys
from datetime import UTC, datetime
from pathlib import Path
from typing import Any

from backend.app.logging import logger
from backend.app.ml.config import ModelConfig, TrainingConfig


class ModelRegistry:
    """Manages versioned model artifact storage under registry/<model_name>/v<N>/."""

    def __init__(self, base_registry_dir: str | Path | None = None):
        if base_registry_dir is None:
            self.base_dir = Path(__file__).resolve().parent / "artifacts"
        else:
            self.base_dir = Path(base_registry_dir)
        self.base_dir.mkdir(parents=True, exist_ok=True)

    def _get_next_version(self, model_dir: Path) -> int:
        if not model_dir.exists():
            return 1
        existing_versions = []
        for item in model_dir.iterdir():
            if item.is_dir() and item.name.startswith("v") and item.name[1:].isdigit():
                existing_versions.append(int(item.name[1:]))
        return max(existing_versions) + 1 if existing_versions else 1

    def _get_git_commit(self) -> str:
        try:
            res = subprocess.run(
                ["git", "rev-parse", "--short", "HEAD"],
                capture_output=True,
                text=True,
                check=True,
            )
            return res.stdout.strip()
        except Exception:
            return "unknown"

    def register_model(
        self,
        model: Any,
        model_config: ModelConfig,
        training_config: TrainingConfig,
        metrics: dict[str, Any],
        feature_names: list[str],
        shap_summary: dict[str, float] | None = None,
    ) -> Path:
        """Saves complete versioned artifact package under registry/<model_name>/v<N>/."""
        model_dir = self.base_dir / model_config.model_name
        version_num = self._get_next_version(model_dir)
        version_dir = model_dir / f"v{version_num}"
        version_dir.mkdir(parents=True, exist_ok=True)

        # 1. Save model binary/JSON
        model_path = version_dir / "model.ubj"
        if hasattr(model, "save_model"):
            model.save_model(str(model_path))
        else:
            # Fallback pickle / joblib
            import pickle

            with open(version_dir / "model.pkl", "wb") as f:
                pickle.dump(model, f)
            model_path = version_dir / "model.pkl"

        # 2. Compute config hash for reproducibility
        config_bytes = json.dumps(model_config.model_dump(), sort_keys=True).encode("utf-8")
        config_hash = hashlib.sha256(config_bytes).hexdigest()[:12]

        # 3. Write metadata.json
        metadata = {
            "model_name": model_config.model_name,
            "version": f"v{version_num}",
            "created_at": datetime.now(UTC).isoformat(),
            "git_commit": self._get_git_commit(),
            "python_version": sys.version.split()[0],
            "random_seed": model_config.random_seed,
            "training_config_hash": config_hash,
        }
        with open(version_dir / "metadata.json", "w", encoding="utf-8") as f:
            json.dump(metadata, f, indent=2)

        # 4. Write metrics.json
        with open(version_dir / "metrics.json", "w", encoding="utf-8") as f:
            json.dump(metrics, f, indent=2)

        # 5. Write training_config.json
        with open(version_dir / "training_config.json", "w", encoding="utf-8") as f:
            json.dump(training_config.model_dump(), f, indent=2)

        # 6. Write feature_schema.json
        feature_schema = {
            "schema_version": training_config.feature_schema_version,
            "num_features": len(feature_names),
            "feature_names": feature_names,
        }
        with open(version_dir / "feature_schema.json", "w", encoding="utf-8") as f:
            json.dump(feature_schema, f, indent=2)

        # 7. Write label_schema.json
        label_schema = {
            "schema_version": training_config.label_schema_version,
            "target_label": training_config.target_label_name,
        }
        with open(version_dir / "label_schema.json", "w", encoding="utf-8") as f:
            json.dump(label_schema, f, indent=2)

        # 8. Write shap_summary.json if provided
        if shap_summary:
            with open(version_dir / "shap_summary.json", "w", encoding="utf-8") as f:
                json.dump(shap_summary, f, indent=2)

        # 9. Write manifest.json
        manifest = {
            "version_dir": str(version_dir),
            "model_path": str(model_path),
            "metadata": metadata,
            "metrics": metrics,
        }
        with open(version_dir / "manifest.json", "w", encoding="utf-8") as f:
            json.dump(manifest, f, indent=2)

        # Update 'latest' pointer
        import contextlib

        latest_link = model_dir / "latest"
        if (latest_link.exists() or latest_link.is_symlink()) and (
            latest_link.is_symlink() or os.name == "nt"
        ):
            with contextlib.suppress(Exception):
                latest_link.unlink()

        try:
            latest_link.symlink_to(version_dir.name, target_is_directory=True)
        except Exception:
            # Fallback copy manifest file into latest directory if symlinks fail
            latest_dir = model_dir / "latest_dir"
            latest_dir.mkdir(exist_ok=True)
            shutil.copy(version_dir / "manifest.json", latest_dir / "manifest.json")

        logger.info(
            "Successfully registered model artifacts",
            extra={"model_name": model_config.model_name, "version": f"v{version_num}"},
        )
        return version_dir

    def load_model(self, model_name: str, version: str = "latest") -> tuple[Any, dict[str, Any]]:
        """Loads versioned model artifact and feature schema."""
        model_dir = self.base_dir / model_name
        if version == "latest":
            latest_link = model_dir / "latest"
            if latest_link.exists() and latest_link.is_symlink():
                target_version_dir = model_dir / os.readlink(latest_link)
            else:
                # Find max version directory
                existing_versions = [
                    int(item.name[1:])
                    for item in model_dir.iterdir()
                    if item.is_dir() and item.name.startswith("v") and item.name[1:].isdigit()
                ]
                if not existing_versions:
                    raise FileNotFoundError(f"No versioned models found for '{model_name}'")
                target_version_dir = model_dir / f"v{max(existing_versions)}"
        else:
            target_version_dir = model_dir / version

        if not target_version_dir.exists():
            raise FileNotFoundError(f"Model version directory not found: {target_version_dir}")

        # Load feature schema
        with open(target_version_dir / "feature_schema.json", encoding="utf-8") as f:
            feature_schema = json.load(f)

        # Load model
        model_path = target_version_dir / "model.ubj"
        if model_path.exists():
            try:
                import xgboost as xgb  # type: ignore

                model = xgb.XGBClassifier()
                model.load_model(str(model_path))
                return model, feature_schema
            except Exception:
                pass

        pkl_path = target_version_dir / "model.pkl"
        if pkl_path.exists():
            import pickle

            with open(pkl_path, "rb") as f:
                model = pickle.load(f)
            return model, feature_schema

        raise FileNotFoundError(f"No valid model binary found in {target_version_dir}")
