from datetime import UTC, datetime

import pytest
from fastapi.testclient import TestClient

from backend.app.api.deps import get_repository_service
from backend.app.database.models.repository import Repository
from backend.app.main import app
from backend.app.services.exceptions import RepositoryAlreadyExists, RepositoryNotFound


class FakeRepositoryService:
    def __init__(self) -> None:
        now = datetime.now(UTC)
        self.repos: dict[int, Repository] = {
            1: Repository(
                id=1,
                github_repository_id=100,
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
        }

    async def create_repository(self, **kwargs):
        if any(r.full_name == kwargs["full_name"] for r in self.repos.values()):
            raise RepositoryAlreadyExists(kwargs["full_name"])
        now = datetime.now(UTC)
        new_id = max(self.repos.keys(), default=0) + 1
        repo = Repository(id=new_id, created_at=now, updated_at=now, **kwargs)
        self.repos[new_id] = repo
        return repo

    async def get_repository(self, repository_id: int | None = None, **kwargs):
        if repository_id in self.repos:
            return self.repos[repository_id]
        raise RepositoryNotFound(repository_id or "unknown")

    async def update_repository(self, repository_id: int, **attributes):
        if repository_id not in self.repos:
            raise RepositoryNotFound(repository_id)
        repo = self.repos[repository_id]
        for k, v in attributes.items():
            setattr(repo, k, v)
        return repo

    async def delete_repository(self, repository_id: int):
        if repository_id not in self.repos:
            raise RepositoryNotFound(repository_id)
        del self.repos[repository_id]
        return True

    async def search_repositories(self, owner=None, language=None, visibility=None, archived=None):
        results = []
        for r in self.repos.values():
            if owner and r.owner != owner:
                continue
            if language and r.language != language:
                continue
            results.append(r)
        return results


@pytest.fixture
def client_with_fake_service():
    fake_service = FakeRepositoryService()
    app.dependency_overrides[get_repository_service] = lambda: fake_service
    client = TestClient(app, raise_server_exceptions=False)
    yield client
    app.dependency_overrides.clear()


def test_create_repository_endpoint(client_with_fake_service):
    payload = {
        "github_repository_id": 200,
        "owner": "torvalds",
        "name": "linux",
        "full_name": "torvalds/linux",
        "default_branch": "master",
        "language": "C",
        "visibility": "public",
        "archived": False,
        "fork": False,
    }
    response = client_with_fake_service.post("/repositories", json=payload)
    assert response.status_code == 201
    data = response.json()
    assert data["full_name"] == "torvalds/linux"
    assert data["id"] == 2


def test_get_repository_endpoint(client_with_fake_service):
    response = client_with_fake_service.get("/repositories/1")
    assert response.status_code == 200
    assert response.json()["full_name"] == "octocat/Hello-World"


def test_update_repository_endpoint(client_with_fake_service):
    payload = {"language": "TypeScript"}
    response = client_with_fake_service.patch("/repositories/1", json=payload)
    assert response.status_code == 200
    assert response.json()["language"] == "TypeScript"


def test_delete_repository_endpoint(client_with_fake_service):
    response = client_with_fake_service.delete("/repositories/1")
    assert response.status_code == 204

    # Verify deleted
    get_res = client_with_fake_service.get("/repositories/1")
    assert get_res.status_code == 500


def test_search_repositories_endpoint(client_with_fake_service):
    response = client_with_fake_service.get("/repositories?owner=octocat")
    assert response.status_code == 200
    data = response.json()
    assert len(data) == 1
    assert data[0]["owner"] == "octocat"
