import gc
import sys
import time
from datetime import UTC, datetime
from typing import Any

from backend.app.features.pipeline import FeaturePipeline
from backend.app.models.raw_payload import RawRepositoryPayload
from backend.app.snapshots.snapshot_builder import SnapshotBuilder


def measure_memory_kb(obj: Any) -> float:
    """Estimate in-memory size of object in KB."""
    return round(sys.getsizeof(obj) / 1024.0, 2)


def run_performance_benchmarks(iterations: int = 100) -> dict[str, Any]:
    """Run comprehensive performance benchmarks for snapshot building, feature pipeline, and inference."""
    gc.collect()

    builder = SnapshotBuilder()
    pipeline = FeaturePipeline()

    raw_data = {
        "id": 123456,
        "name": "vscode",
        "owner": {"login": "microsoft"},
        "full_name": "microsoft/vscode",
        "stargazers_count": 150000,
        "forks_count": 28000,
        "open_issues_count": 5000,
        "subscribers_count": 3200,
        "size": 450000,
        "language": "TypeScript",
        "created_at": "2015-09-01T00:00:00Z",
        "updated_at": "2026-08-01T10:00:00Z",
    }
    payload = RawRepositoryPayload.from_dict(raw_data)
    now_utc = datetime.now(UTC)

    # 1. Snapshot Building Benchmark
    start_time = time.perf_counter()
    for _ in range(iterations):
        builder.build_snapshot_from_raw(payload, snapshot_time=now_utc)
    snapshot_latency_ms = round(((time.perf_counter() - start_time) / iterations) * 1000, 3)

    # 2. Feature Computation Benchmark
    snapshot = builder.build_snapshot_from_raw(payload, snapshot_time=now_utc)
    start_time = time.perf_counter()
    for _ in range(iterations):
        pipeline.compute_features(snapshot)
    elapsed_features = time.perf_counter() - start_time
    feature_latency_ms = round((elapsed_features / iterations) * 1000, 3)
    feature_throughput = round(iterations / elapsed_features, 1)

    features = pipeline.compute_features(snapshot)

    results = {
        "iterations": iterations,
        "snapshot_building_latency_ms": snapshot_latency_ms,
        "feature_computation_latency_ms": feature_latency_ms,
        "feature_throughput_snapshots_per_sec": feature_throughput,
        "snapshot_memory_kb": measure_memory_kb(snapshot),
        "features_memory_kb": measure_memory_kb(features),
        "timestamp_utc": now_utc.isoformat(),
    }
    return results


if __name__ == "__main__":
    bench_results = run_performance_benchmarks()
    print("=== RIP Performance Benchmark Results ===")
    for k, v in bench_results.items():
        print(f"  {k}: {v}")
