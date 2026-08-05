from datetime import UTC, datetime

import pytest
from pydantic import ValidationError

from backend.app.database.models.repository import Repository
from backend.app.database.models.snapshot import RepositorySnapshot
from backend.app.schemas import (
    BaseSchema,
    RepositoryCreate,
    RepositoryResponse,
    RepositorySearch,
    RepositorySnapshotCreate,
    RepositorySnapshotResponse,
    RepositorySnapshotUpdate,
    RepositoryUpdate,
)


class SampleItemSchema(BaseSchema):
    name: str
    count: int


def test_base_schema_attributes():
    """Verify BaseSchema configuration: attribute population and extra field forbidding."""
    item = SampleItemSchema(name="repo", count=10)
    assert item.name == "repo"
    assert item.count == 10

    # Extra fields are forbidden
    with pytest.raises(ValidationError):
        SampleItemSchema(name="repo", count=10, extra_field="forbidden")  # type: ignore[call-arg]


def test_repository_schemas():
    """Verify Repository DTO schemas instantiation, defaults, and ORM conversion."""
    create_dto = RepositoryCreate(
        github_repository_id=12345,
        owner="octocat",
        name="Hello-World",
        full_name="octocat/Hello-World",
        language="Python",
    )
    assert create_dto.github_repository_id == 12345
    assert create_dto.default_branch == "main"
    assert create_dto.visibility == "public"

    update_dto = RepositoryUpdate(language="TypeScript", default_branch="develop")
    assert update_dto.language == "TypeScript"
    assert update_dto.owner is None

    search_dto = RepositorySearch(owner="octocat", language="Python")
    assert search_dto.owner == "octocat"

    # ORM conversion for RepositoryResponse
    now = datetime.now(UTC)
    repo_orm = Repository(
        id=1,
        github_repository_id=12345,
        owner="octocat",
        name="Hello-World",
        full_name="octocat/Hello-World",
        default_branch="main",
        language="Python",
        visibility="public",
        archived=False,
        fork=False,
        created_at=now,
        updated_at=now,
    )

    response_dto = RepositoryResponse.model_validate(repo_orm)
    assert response_dto.id == 1
    assert response_dto.full_name == "octocat/Hello-World"
    assert response_dto.created_at == now


def test_repository_snapshot_schemas():
    """Verify RepositorySnapshot DTO schemas instantiation and ORM validation."""
    now = datetime.now(UTC)
    create_dto = RepositorySnapshotCreate(
        repository_id=1,
        snapshot_time=now,
        stars=100,
        forks=20,
        watchers=100,
        open_issues=5,
        subscribers=15,
        network_count=20,
        size_kb=1024,
        license="MIT",
    )
    assert create_dto.stars == 100
    assert create_dto.repository_id == 1

    update_dto = RepositorySnapshotUpdate(stars=120)
    assert update_dto.stars == 120
    assert update_dto.forks is None

    snap_orm = RepositorySnapshot(
        id=10,
        repository_id=1,
        snapshot_time=now,
        stars=100,
        forks=20,
        watchers=100,
        open_issues=5,
        subscribers=15,
        network_count=20,
        size_kb=1024,
        license="MIT",
        default_branch="main",
        collected_at=now,
        created_at=now,
        updated_at=now,
    )

    response_dto = RepositorySnapshotResponse.model_validate(snap_orm)
    assert response_dto.id == 10
    assert response_dto.stars == 100
    assert response_dto.license == "MIT"
