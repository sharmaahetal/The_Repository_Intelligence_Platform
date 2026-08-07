from datetime import UTC, datetime

import pytest
from fastapi.testclient import TestClient

from backend.app.api.deps import get_snapshot_service
from backend.app.database.models.snapshot import RepositorySnapshot
from backend.app.main import app
from backend.app.services.exceptions import DuplicateSnapshotError, SnapshotNotFound


class FakeSnapshotService:
    def __init__(self) -> None:
        now = datetime.now(UTC)
        self.snapshots: dict[int, RepositorySnapshot] = {
            10: RepositorySnapshot(
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
        }

    async def create_snapshot(self, **kwargs):
        repository_id = kwargs["repository_id"]
        snapshot_time = kwargs["snapshot_time"]
        if any(
            s.repository_id == repository_id and s.snapshot_time == snapshot_time
            for s in self.snapshots.values()
        ):
            raise DuplicateSnapshotError(repository_id, snapshot_time)
        now = datetime.now(UTC)
        new_id = max(self.snapshots.keys(), default=0) + 1
        snapshot = RepositorySnapshot(
            id=new_id,
            collected_at=now,
            created_at=now,
            updated_at=now,
            **kwargs,
        )
        self.snapshots[new_id] = snapshot
        return snapshot

    async def get_snapshot_by_id(self, snapshot_id: int):
        if snapshot_id in self.snapshots:
            return self.snapshots[snapshot_id]
        raise SnapshotNotFound(snapshot_id)

    async def update_snapshot(self, snapshot_id: int, **attributes):
        if snapshot_id not in self.snapshots:
            raise SnapshotNotFound(snapshot_id)
        snap = self.snapshots[snapshot_id]
        for k, v in attributes.items():
            setattr(snap, k, v)
        return snap

    async def delete_snapshot(self, snapshot_id: int):
        if snapshot_id not in self.snapshots:
            raise SnapshotNotFound(snapshot_id)
        del self.snapshots[snapshot_id]
        return True

    async def snapshot_history(self, repository_id: int):
        return [s for s in self.snapshots.values() if s.repository_id == repository_id]


@pytest.fixture
def client_with_fake_service():
    fake_service = FakeSnapshotService()
    app.dependency_overrides[get_snapshot_service] = lambda: fake_service
    client = TestClient(app, raise_server_exceptions=False)
    yield client
    app.dependency_overrides.clear()


def test_create_snapshot_endpoint(client_with_fake_service):
    now_iso = datetime.now(UTC).isoformat()
    payload = {
        "repository_id": 1,
        "snapshot_time": now_iso,
        "stars": 150,
        "forks": 30,
        "watchers": 150,
        "open_issues": 10,
        "subscribers": 20,
        "network_count": 30,
        "size_kb": 2048,
        "license": "Apache-2.0",
        "default_branch": "main",
    }
    response = client_with_fake_service.post("/snapshots", json=payload)
    assert response.status_code == 201
    data = response.json()
    assert data["stars"] == 150
    assert data["repository_id"] == 1


def test_get_snapshot_endpoint(client_with_fake_service):
    response = client_with_fake_service.get("/snapshots/10")
    assert response.status_code == 200
    assert response.json()["stars"] == 100


def test_update_snapshot_endpoint(client_with_fake_service):
    payload = {"stars": 200}
    response = client_with_fake_service.patch("/snapshots/10", json=payload)
    assert response.status_code == 200
    assert response.json()["stars"] == 200


def test_delete_snapshot_endpoint(client_with_fake_service):
    response = client_with_fake_service.delete("/snapshots/10")
    assert response.status_code == 204

    # Verify deletion
    get_res = client_with_fake_service.get("/snapshots/10")
    assert get_res.status_code in (404, 500)


def test_repository_snapshot_history_endpoints(client_with_fake_service):
    res1 = client_with_fake_service.get("/snapshots/repository/1")
    assert res1.status_code == 200
    assert len(res1.json()) == 1

    res2 = client_with_fake_service.get("/repositories/1/snapshots")
    assert res2.status_code == 200
    assert len(res2.json()) == 1
