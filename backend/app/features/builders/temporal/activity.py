from app.features.registry import FeatureRegistry
from app.models.snapshot import RepositorySnapshot

default_registry = FeatureRegistry(version="v1.0")


@default_registry.register("star_density_index")
def build_star_density(snapshot: RepositorySnapshot) -> float:
    """Computes ratio of stars relative to repository size in MB."""
    size_mb = max(1.0, float(snapshot.size_kb) / 1024.0)
    stars = float(snapshot.stars_count)
    return round(stars / size_mb, 4)


@default_registry.register("fork_to_star_ratio")
def build_fork_star_ratio(snapshot: RepositorySnapshot) -> float:
    """Computes ratio of forks to stars (indicator of code usage vs bookmarking)."""
    stars = max(1.0, float(snapshot.stars_count))
    forks = float(snapshot.forks_count)
    return round(forks / stars, 4)


@default_registry.register("open_issue_density")
def build_issue_density(snapshot: RepositorySnapshot) -> float:
    """Computes open issue burden relative to total stars."""
    stars = max(1.0, float(snapshot.stars_count))
    issues = float(snapshot.open_issues_count)
    return round(issues / stars, 4)


@default_registry.register("subscriber_engagement_ratio")
def build_subscriber_ratio(snapshot: RepositorySnapshot) -> float:
    """Computes watchers/subscribers to stars ratio."""
    stars = max(1.0, float(snapshot.stars_count))
    subscribers = float(snapshot.subscribers_count)
    return round(subscribers / stars, 4)
