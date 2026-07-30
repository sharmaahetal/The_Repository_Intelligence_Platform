from typing import Any

from app.features.registry import FeatureRegistry

default_registry = FeatureRegistry(version="v1.0")


@default_registry.register("star_density_index")
def build_star_density(snapshot: dict[str, Any]) -> float:
    """Computes ratio of stars relative to repository size in MB."""
    size_mb = max(1.0, float(snapshot.get("size_kb", 0)) / 1024.0)
    stars = float(snapshot.get("stars_count", 0))
    return round(stars / size_mb, 4)


@default_registry.register("fork_to_star_ratio")
def build_fork_star_ratio(snapshot: dict[str, Any]) -> float:
    """Computes ratio of forks to stars (indicator of code usage vs bookmarking)."""
    stars = max(1.0, float(snapshot.get("stars_count", 0)))
    forks = float(snapshot.get("forks_count", 0))
    return round(forks / stars, 4)


@default_registry.register("open_issue_density")
def build_issue_density(snapshot: dict[str, Any]) -> float:
    """Computes open issue burden relative to total stars."""
    stars = max(1.0, float(snapshot.get("stars_count", 0)))
    issues = float(snapshot.get("open_issues_count", 0))
    return round(issues / stars, 4)


@default_registry.register("subscriber_engagement_ratio")
def build_subscriber_ratio(snapshot: dict[str, Any]) -> float:
    """Computes watchers/subscribers to stars ratio."""
    stars = max(1.0, float(snapshot.get("stars_count", 0)))
    subscribers = float(snapshot.get("subscribers_count", 0))
    return round(subscribers / stars, 4)
