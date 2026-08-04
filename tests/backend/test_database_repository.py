import pytest
from sqlalchemy.ext.asyncio import AsyncSession, async_sessionmaker

from backend.app.database import (
    Base,
    BaseRepository,
    Repository,
    create_engine,
)


@pytest.mark.asyncio
async def test_base_repository_crud_operations(tmp_path):
    """Verify all CRUD methods on BaseRepository: create, bulk_create, get, get_by_id, list, list_all, update, delete, exists, count, refresh, flush."""
    db_file = tmp_path / "test_repo.db"
    test_engine = create_engine(f"sqlite+aiosqlite:///{db_file}")

    async with test_engine.begin() as conn:
        await conn.run_sync(Base.metadata.create_all)

    session_maker = async_sessionmaker(bind=test_engine, class_=AsyncSession, expire_on_commit=False)

    async with session_maker() as session:
        repo_dao = BaseRepository(session, Repository)

        # 1. count() on empty table
        assert await repo_dao.count() == 0

        # 2. create()
        repo1 = await repo_dao.create(
            github_repository_id=1001,
            owner="django",
            name="django",
            full_name="django/django",
            default_branch="main",
            language="Python",
        )
        assert repo1.id is not None
        assert repo1.github_repository_id == 1001

        # 3. bulk_create()
        bulk_res = await repo_dao.bulk_create([
            {
                "github_repository_id": 1002,
                "owner": "pallets",
                "name": "flask",
                "full_name": "pallets/flask",
                "default_branch": "main",
                "language": "Python",
            },
            {
                "github_repository_id": 1003,
                "owner": "psf",
                "name": "requests",
                "full_name": "psf/requests",
                "default_branch": "main",
                "language": "Python",
            },
        ])
        assert len(bulk_res) == 2
        assert await repo_dao.count() == 3

        # bulk_create with empty list returns []
        assert await repo_dao.bulk_create([]) == []

        # 4. count() and exists()
        assert await repo_dao.exists(repo1.id) is True
        assert await repo_dao.exists(99999) is False

        # 5. get() with keyword filters
        fetched_by_filter = await repo_dao.get(full_name="psf/requests")
        assert fetched_by_filter is not None
        assert fetched_by_filter.owner == "psf"

        assert await repo_dao.get(full_name="nonexistent/repo") is None

        # 6. get_by_id()
        fetched = await repo_dao.get_by_id(repo1.id)
        assert fetched is not None
        assert fetched.full_name == "django/django"

        # 7. list_all() & list()
        all_repos = await repo_dao.list_all()
        all_repos_alias = await repo_dao.list()
        assert len(all_repos) == 3
        assert len(all_repos_alias) == 3

        # 8. update() with field validation
        updated = await repo_dao.update(repo1.id, {"default_branch": "stable", "visibility": "public"})
        assert updated is not None
        assert updated.default_branch == "stable"

        # Update with invalid attribute raises ValueError
        with pytest.raises(ValueError, match="Unknown attribute 'invalid_attr' for model 'Repository'"):
            await repo_dao.update(repo1.id, {"invalid_attr": "value"})

        # Update non-existent ID returns None
        assert await repo_dao.update(99999, {"name": "ghost"}) is None

        # 9. refresh() and flush()
        await repo_dao.refresh(repo1)
        await repo_dao.flush()

        # 10. delete()
        assert await repo_dao.delete(bulk_res[0].id) is True
        assert await repo_dao.delete(bulk_res[0].id) is False
        assert await repo_dao.count() == 2

    await test_engine.dispose()
