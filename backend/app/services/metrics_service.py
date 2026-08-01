from typing import Any
from app.logging import logger


class MetricsService:
    """Prometheus-style metrics collector tracking request counts, latencies, cache hit ratios, and model version usage."""

    def __init__(self):
        self.request_count: int = 0
        self.prediction_failures: int = 0
        self.cache_hits: int = 0
        self.cache_misses: int = 0
        self.model_version_usage: dict[str, int] = {}
        self.latencies_ms: list[float] = []

    def record_request(self, model_version: str, latency_ms: float, success: bool = True) -> None:
        """Record an API request event."""
        self.request_count += 1
        self.latencies_ms.append(latency_ms)
        if len(self.latencies_ms) > 1000:
            self.latencies_ms = self.latencies_ms[-1000:]

        if not success:
            self.prediction_failures += 1

        self.model_version_usage[model_version] = self.model_version_usage.get(model_version, 0) + 1

    def record_cache_hit(self) -> None:
        """Record cache hit counter."""
        self.cache_hits += 1

    def record_cache_miss(self) -> None:
        """Record cache miss counter."""
        self.cache_misses += 1

    def get_metrics_summary(self) -> dict[str, Any]:
        """Returns structured metrics summary."""
        total_cache_ops = self.cache_hits + self.cache_misses
        cache_hit_ratio = round(self.cache_hits / total_cache_ops, 4) if total_cache_ops > 0 else 0.0
        avg_latency = round(sum(self.latencies_ms) / len(self.latencies_ms), 2) if self.latencies_ms else 0.0

        summary = {
            "request_count": self.request_count,
            "prediction_failures": self.prediction_failures,
            "cache_hits": self.cache_hits,
            "cache_misses": self.cache_misses,
            "cache_hit_ratio": cache_hit_ratio,
            "avg_latency_ms": avg_latency,
            "model_version_usage": self.model_version_usage,
        }

        logger.info("Metrics summary requested", extra=summary)
        return summary
