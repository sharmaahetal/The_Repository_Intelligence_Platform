"""Repository snapshot API endpoints for Repository Intelligence Platform."""

from fastapi import APIRouter, Depends, status

from backend.app.api.deps import get_snapshot_service
from backend.app.schemas import (
    RepositorySnapshotCreate,
    RepositorySnapshotResponse,
    RepositorySnapshotUpdate,
)
from backend.app.services.snapshot_service import SnapshotService

router = APIRouter(prefix="/snapshots", tags=["Snapshots"])


@router.post(
    "",
    response_model=RepositorySnapshotResponse,
    status_code=status.HTTP_201_CREATED,
    summary="Create a new repository snapshot",
)
async def create_snapshot(
    payload: RepositorySnapshotCreate,
    service: SnapshotService = Depends(get_snapshot_service),
) -> RepositorySnapshotResponse:
    """Record a point-in-time metrics snapshot for a repository."""
    snapshot = await service.create_snapshot(
        repository_id=payload.repository_id,
        snapshot_time=payload.snapshot_time,
        stars=payload.stars,
        forks=payload.forks,
        open_issues=payload.open_issues,
        watchers=payload.watchers,
        subscribers=payload.subscribers,
        network_count=payload.network_count,
        size_kb=payload.size_kb,
        license=payload.license,
        topics_json=payload.topics_json,
        default_branch=payload.default_branch,
    )
    return RepositorySnapshotResponse.model_validate(snapshot)


@router.get(
    "/{snapshot_id}",
    response_model=RepositorySnapshotResponse,
    status_code=status.HTTP_200_OK,
    summary="Get snapshot by ID",
)
async def get_snapshot(
    snapshot_id: int,
    service: SnapshotService = Depends(get_snapshot_service),
) -> RepositorySnapshotResponse:
    """Retrieve a snapshot entity by its primary key ID."""
    snapshot = await service.get_snapshot_by_id(snapshot_id)
    return RepositorySnapshotResponse.model_validate(snapshot)


@router.patch(
    "/{snapshot_id}",
    response_model=RepositorySnapshotResponse,
    status_code=status.HTTP_200_OK,
    summary="Update snapshot attributes",
)
async def update_snapshot(
    snapshot_id: int,
    payload: RepositorySnapshotUpdate,
    service: SnapshotService = Depends(get_snapshot_service),
) -> RepositorySnapshotResponse:
    """Update metrics or metadata for an existing snapshot."""
    update_data = payload.model_dump(exclude_unset=True)
    snapshot = await service.update_snapshot(snapshot_id, **update_data)
    return RepositorySnapshotResponse.model_validate(snapshot)


@router.delete(
    "/{snapshot_id}",
    status_code=status.HTTP_204_NO_CONTENT,
    summary="Delete a snapshot",
)
async def delete_snapshot(
    snapshot_id: int,
    service: SnapshotService = Depends(get_snapshot_service),
) -> None:
    """Delete a snapshot entity by ID."""
    await service.delete_snapshot(snapshot_id)


@router.get(
    "/repository/{repository_id}",
    response_model=list[RepositorySnapshotResponse],
    status_code=status.HTTP_200_OK,
    summary="Get repository snapshot history",
)
async def repository_history(
    repository_id: int,
    service: SnapshotService = Depends(get_snapshot_service),
) -> list[RepositorySnapshotResponse]:
    """Retrieve chronological snapshot history for a repository."""
    history = await service.snapshot_history(repository_id)
    return [RepositorySnapshotResponse.model_validate(s) for s in history]
