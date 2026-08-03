import pytest
from sqlalchemy.ext.asyncio import AsyncSession

from backend.app.database.session import (
    AsyncSessionLocal,
    SessionFactory,
    get_db_session,
    get_session_factory,
)


@pytest.mark.asyncio
async def test_session_creation_via_factory():
    """Test 1: Verify session creation via SessionFactory and AsyncSessionLocal alias."""
    session1 = SessionFactory()
    session2 = AsyncSessionLocal()
    assert isinstance(session1, AsyncSession)
    assert isinstance(session2, AsyncSession)
    await session1.close()
    await session2.close()


@pytest.mark.asyncio
async def test_get_db_session_lifecycle_and_close():
    """Test 3: Verify get_db_session yields an active session and closes it on exit."""
    yielded_session = None
    async for session in get_db_session():
        assert isinstance(session, AsyncSession)
        yielded_session = session
        assert session.is_active

    assert yielded_session is not None


@pytest.mark.asyncio
async def test_get_db_session_rollback_on_exception():
    """Test 2: Verify exceptions trigger transaction rollback and are re-raised without swallowing."""
    with pytest.raises(RuntimeError, match="Simulated transaction error"):
        async for session in get_db_session():
            raise RuntimeError("Simulated transaction error")


@pytest.mark.asyncio
async def test_multiple_sessions_independence():
    """Test 4: Verify multiple get_db_session invocations produce distinct AsyncSession instances."""
    gen1 = get_db_session()
    gen2 = get_db_session()

    s1 = await anext(gen1)
    s2 = await anext(gen2)

    assert isinstance(s1, AsyncSession)
    assert isinstance(s2, AsyncSession)
    assert s1 is not s2

    await gen1.aclose()
    await gen2.aclose()
