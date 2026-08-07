"""Repository API endpoints for Repository Intelligence Platform."""

from fastapi import APIRouter, Depends, status

from backend.app.api.deps import get_repository_service
from backend.app.schemas import (
    RepositoryCreate,
    RepositoryResponse,
    RepositorySearch,
    RepositoryUpdate,
)
from backend.app.services.repository_service import RepositoryService

router = APIRouter(prefix="/repositories", tags=["Repositories"])


@router.post(
    "",
    response_model=RepositoryResponse,
    status_code=status.HTTP_201_CREATED,
    summary="Create a new repository",
)
async def create_repository(
    payload: RepositoryCreate,
    service: RepositoryService = Depends(get_repository_service),
) -> RepositoryResponse:
    """Create a new repository entity."""
    repo = await service.create_repository(
        owner=payload.owner,
        name=payload.name,
        full_name=payload.full_name,
        github_repository_id=payload.github_repository_id,
        default_branch=payload.default_branch,
        language=payload.language,
        visibility=payload.visibility,
        archived=payload.archived,
        fork=payload.fork,
    )
    return RepositoryResponse.model_validate(repo)


@router.get(
    "/{repository_id}",
    response_model=RepositoryResponse,
    status_code=status.HTTP_200_OK,
    summary="Get repository by ID",
)
async def get_repository(
    repository_id: int,
    service: RepositoryService = Depends(get_repository_service),
) -> RepositoryResponse:
    """Retrieve a repository entity by its internal database ID."""
    repo = await service.get_repository(repository_id=repository_id)
    return RepositoryResponse.model_validate(repo)


@router.patch(
    "/{repository_id}",
    response_model=RepositoryResponse,
    status_code=status.HTTP_200_OK,
    summary="Update repository attributes",
)
async def update_repository(
    repository_id: int,
    payload: RepositoryUpdate,
    service: RepositoryService = Depends(get_repository_service),
) -> RepositoryResponse:
    """Update non-null fields of an existing repository entity."""
    update_data = payload.model_dump(exclude_unset=True)
    repo = await service.update_repository(repository_id, **update_data)
    return RepositoryResponse.model_validate(repo)


@router.delete(
    "/{repository_id}",
    status_code=status.HTTP_204_NO_CONTENT,
    summary="Delete a repository",
)
async def delete_repository(
    repository_id: int,
    service: RepositoryService = Depends(get_repository_service),
) -> None:
    """Delete a repository entity by ID."""
    await service.delete_repository(repository_id)


@router.get(
    "",
    response_model=list[RepositoryResponse],
    status_code=status.HTTP_200_OK,
    summary="Search repositories",
)
async def search_repositories(
    search_params: RepositorySearch = Depends(),
    service: RepositoryService = Depends(get_repository_service),
) -> list[RepositoryResponse]:
    """Search repositories matching optional query criteria."""
    repos = await service.search_repositories(
        owner=search_params.owner,
        language=search_params.language,
        visibility=search_params.visibility,
        archived=search_params.archived,
    )
    return [RepositoryResponse.model_validate(r) for r in repos]
