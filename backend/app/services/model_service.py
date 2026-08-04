"""Model Service implementing business rules for model versions."""

from __future__ import annotations

from backend.app.services.model_version_service import ModelVersionService

# Alias ModelService to ModelVersionService for complete backwards compatibility
ModelService = ModelVersionService

__all__ = [
    "ModelVersionService",
    "ModelService",
]
