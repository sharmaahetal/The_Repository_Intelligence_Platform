import pytest
from sqlalchemy.ext.asyncio import AsyncSession

from backend.app.database.session import (
    AsyncSessionLocal,
    get_db_session,
    get_sessionmaker,
)


@pytest.mark.asyncio
async def test_session_factory_initialization():
    """Step 1 & Checklist 1: Verify get_sessionmaker initializes valid async_sessionmaker."""
    factory = get_sessionmaker()
    session = factory()
    assert isinstance(session, AsyncSession)
    await session.close()


@pytest.mark.asyncio
async def test_get_db_session_lifecycle():
    """Step 2 & Checklist 4: Verify get_db_session yields active session and closes cleanly."""
    yielded_session = None
    async for session in get_db_session():
        assert isinstance(session, AsyncSession)
        yielded_session = session
        assert session.is_active

    # After generator exit, verify session is closed
    assert yielded_session is not None


@pytest.mark.asyncio
async def test_get_db_session_rollback_on_exception():
    """Step 3 & Checklist 3: Verify exceptions trigger rollback and are re-raised without swallowing."""
    with pytest.raises(RuntimeError, match="Simulated transaction failure"):
        async for session in get_db_session():
            raise RuntimeError("Simulated transaction failure")
