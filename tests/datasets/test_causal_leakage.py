from datetime import UTC, datetime


def compute_mock_features(events: list[dict], snapshot_time: datetime) -> dict[str, float]:
    """Mock feature builder asserting timestamp cutting."""
    filtered_events = [e for e in events if e["timestamp"] <= snapshot_time]
    commits = [e for e in filtered_events if e["type"] == "commit"]
    return {
        "commit_count": float(len(commits)),
        "total_events": float(len(filtered_events)),
    }


def test_causal_leakage_assertion():
    t_snapshot = datetime(2025, 1, 1, 0, 0, 0, tzinfo=UTC)

    historical_events = [
        {"type": "commit", "timestamp": datetime(2024, 12, 1, 0, 0, 0, tzinfo=UTC)},
        {"type": "commit", "timestamp": datetime(2024, 12, 15, 0, 0, 0, tzinfo=UTC)},
    ]

    features_before_future = compute_mock_features(historical_events, t_snapshot)

    # Inject future events after t_snapshot
    future_events = historical_events + [
        {"type": "commit", "timestamp": datetime(2025, 1, 15, 0, 0, 0, tzinfo=UTC)},
        {"type": "commit", "timestamp": datetime(2025, 2, 1, 0, 0, 0, tzinfo=UTC)},
    ]

    features_after_future = compute_mock_features(future_events, t_snapshot)

    # Features calculated for snapshot t_snapshot MUST be identical regardless of future events
    assert features_before_future == features_after_future
    assert features_after_future["commit_count"] == 2.0
