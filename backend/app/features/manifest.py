from typing import Any

from pydantic import BaseModel, ConfigDict, Field

from backend.app.features.groups import FeatureGroup


class FeatureDefinition(BaseModel):
    """Metadata specification describing a registered feature, dependencies, and lineage."""

    model_config = ConfigDict(frozen=True)

    name: str = Field(..., description="Unique feature identifier name")
    version: str = Field(default="1.0", description="Feature definition version")
    owner: str = Field(default="engineering", description="Team or subsystem owner")
    group: FeatureGroup = Field(default=FeatureGroup.ACTIVITY, description="Explicit feature group")
    description: str = Field(default="", description="Detailed description of feature logic")
    dependencies: list[str] = Field(default_factory=list, description="Upstream feature dependencies")
    data_type: str = Field(default="float32", description="Feature data type")


class FeatureManifest(BaseModel):
    """Registry manifest aggregating all feature definitions across the platform."""

    model_config = ConfigDict(frozen=True)

    manifest_version: str = Field(default="1.0.0")
    definitions: dict[str, FeatureDefinition] = Field(default_factory=dict)

    def register_definition(self, definition: FeatureDefinition) -> None:
        """Register or update a feature definition in the manifest."""
        self.definitions[definition.name] = definition

    def generate_documentation(self) -> dict[str, Any]:
        """Generates structured documentation map of all registered features."""
        return {
            "version": self.manifest_version,
            "total_features": len(self.definitions),
            "features": {name: defn.model_dump() for name, defn in self.definitions.items()},
        }

    def generate_dependency_graph(self) -> dict[str, list[str]]:
        """Generates dependency graph mapping feature names to their upstream dependencies."""
        return {name: defn.dependencies for name, defn in self.definitions.items()}
