from fastapi import APIRouter, Depends
from fastapi.responses import PlainTextResponse

from backend.app.api.dependencies import get_metrics_service
from backend.app.services.metrics_service import MetricsService

router = APIRouter(prefix="/metrics", tags=["Metrics"])


@router.get("", response_class=PlainTextResponse)
async def get_prometheus_metrics(
    metrics_service: MetricsService = Depends(get_metrics_service),
) -> str:
    """Exposes Prometheus-formatted text metrics for system observability."""
    summary = metrics_service.get_metrics_summary()

    lines = [
        "# HELP rip_requests_total Total number of API requests handled.",
        "# TYPE rip_requests_total counter",
        f"rip_requests_total {summary['request_count']}",
        "",
        "# HELP rip_prediction_failures_total Total number of prediction pipeline failures.",
        "# TYPE rip_prediction_failures_total counter",
        f"rip_prediction_failures_total {summary['prediction_failures']}",
        "",
        "# HELP rip_cache_hits_total Total number of prediction cache hits.",
        "# TYPE rip_cache_hits_total counter",
        f"rip_cache_hits_total {summary['cache_hits']}",
        "",
        "# HELP rip_cache_misses_total Total number of prediction cache misses.",
        "# TYPE rip_cache_misses_total counter",
        f"rip_cache_misses_total {summary['cache_misses']}",
        "",
        "# HELP rip_cache_hit_ratio Ratio of prediction cache hits over total ops.",
        "# TYPE rip_cache_hit_ratio gauge",
        f"rip_cache_hit_ratio {summary['cache_hit_ratio']:.4f}",
        "",
        "# HELP rip_request_latency_avg_ms Average request latency in milliseconds.",
        "# TYPE rip_request_latency_avg_ms gauge",
        f"rip_request_latency_avg_ms {summary['avg_latency_ms']:.2f}",
        "",
    ]

    for model_ver, usage_count in summary["model_version_usage"].items():
        lines.extend([
            f'rip_model_version_usage_total{{version="{model_ver}"}} {usage_count}',
        ])

    return "\n".join(lines) + "\n"
