from collections import defaultdict, deque

from backend.app.features.manifest import FeatureDefinition


class FeatureCycleError(ValueError):
    """Raised when circular dependencies exist in feature definition DAG."""

    pass


class FeatureDAG:
    """DAG resolution engine for feature dependencies supporting topological sorting."""

    def __init__(self, definitions: list[FeatureDefinition] | None = None) -> None:
        self.definitions: dict[str, FeatureDefinition] = {d.name: d for d in (definitions or [])}

    def add_definition(self, definition: FeatureDefinition) -> None:
        """Add feature definition to DAG engine."""
        self.definitions[definition.name] = definition

    def topological_sort(self) -> list[str]:
        """Performs topological sort of features based on declared dependencies.

        Returns list of feature names in executable dependency order.
        Raises FeatureCycleError if a circular dependency is detected.
        """
        in_degree: dict[str, int] = dict.fromkeys(self.definitions, 0)
        graph: dict[str, list[str]] = defaultdict(list)

        # Build adjacency graph
        for name, defn in self.definitions.items():
            for dep in defn.dependencies:
                if dep in self.definitions:
                    graph[dep].append(name)
                    in_degree[name] += 1

        queue = deque([name for name, deg in in_degree.items() if deg == 0])
        execution_order = []

        while queue:
            node = queue.popleft()
            execution_order.append(node)

            for neighbor in graph[node]:
                in_degree[neighbor] -= 1
                if in_degree[neighbor] == 0:
                    queue.append(neighbor)

        if len(execution_order) != len(self.definitions):
            raise FeatureCycleError("Circular dependency detected in Feature DAG!")

        return execution_order
