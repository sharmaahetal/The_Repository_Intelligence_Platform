import time
from typing import Any

from backend.app.logging import logger


class PredictionCache:
    """In-memory cache for repository forecast predictions with configurable TTL expiry."""

    def __init__(self, ttl_seconds: int = 900):  # Default 15 minutes TTL
        self.ttl_seconds = ttl_seconds
        self._cache: dict[tuple[str, str, str, int], tuple[float, Any]] = {}

    def get(self, owner: str, repo: str, model_version: str, horizon: int) -> Any | None:
        """Returns cached forecast payload if valid and not expired."""
        key = (owner.lower(), repo.lower(), model_version, horizon)
        if key in self._cache:
            timestamp, payload = self._cache[key]
            if time.time() - timestamp <= self.ttl_seconds:
                logger.info(
                    "PredictionCache HIT",
                    extra={"owner": owner, "repo": repo, "horizon": horizon},
                )
                return payload
            else:
                # Expired
                del self._cache[key]

        logger.info(
            "PredictionCache MISS",
            extra={"owner": owner, "repo": repo, "horizon": horizon},
        )
        return None

    def set(self, owner: str, repo: str, model_version: str, horizon: int, payload: Any) -> None:
        """Store forecast payload in cache with current timestamp."""
        key = (owner.lower(), repo.lower(), model_version, horizon)
        self._cache[key] = (time.time(), payload)
        logger.info(
            "PredictionCache STORED",
            extra={"owner": owner, "repo": repo, "horizon": horizon},
        )

    def clear(self) -> None:
        """Flushes all entries from cache."""
        self._cache.clear()
