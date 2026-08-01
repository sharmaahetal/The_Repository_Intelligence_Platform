import random
from typing import Any

from backend.app.logging import logger


class CanaryDeploymentManager:
    """Traffic splitting manager executing Champion-Challenger canary deployments in production."""

    def __init__(self, challenger_traffic_pct: float = 0.05) -> None:
        self.challenger_pct = max(0.0, min(1.0, challenger_traffic_pct))
        self._traffic_counts: dict[str, int] = {"champion": 0, "challenger": 0}

    def route_request(self, champion_version: str = "v1.0", challenger_version: str = "v2.0-candidate") -> tuple[str, str]:
        """Routes a single inference request. Returns tuple of (selected_version, deployment_role)."""
        if random.random() < self.challenger_pct:
            selected_version = challenger_version
            role = "challenger"
        else:
            selected_version = champion_version
            role = "champion"

        self._traffic_counts[role] += 1
        logger.debug(
            "Canary traffic routed",
            extra={"selected_version": selected_version, "role": role, "traffic_counts": self._traffic_counts},
        )
        return selected_version, role

    def get_traffic_metrics(self) -> dict[str, Any]:
        """Return traffic distribution summary."""
        total = sum(self._traffic_counts.values())
        return {
            "challenger_target_pct": self.challenger_pct,
            "total_requests_routed": total,
            "counts": self._traffic_counts,
            "actual_challenger_ratio": round(self._traffic_counts["challenger"] / total, 4) if total > 0 else 0.0,
        }
