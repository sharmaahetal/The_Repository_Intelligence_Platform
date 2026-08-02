from enum import Enum


class FeatureGroup(str, Enum):
    """Explicit domain feature grouping categories."""

    ACTIVITY = "activity"
    GROWTH = "growth"
    POPULARITY = "popularity"
    COMMUNITY = "community"
    MAINTENANCE = "maintenance"
    QUALITY = "quality"
    SECURITY = "security"
    DEPENDENCIES = "dependencies"
    RELEASES = "releases"
    CI_CD = "ci_cd"
    TEMPORAL = "temporal"
