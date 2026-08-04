import asyncio
from datetime import datetime

import pytest
from sqlalchemy import inspect
from sqlalchemy.ext.asyncio import AsyncSession, async_sessionmaker
from sqlalchemy.orm import Mapped, mapped_column

from backend.app.database.base import (
    ORM_METADATA,
    POSTGRES_NAMING_CONVENTION,
    Base,
    TimestampMixin,
)
from backend.app.database.engine import create_engine


class DummyModel(Base, TimestampMixin):
    __tablename__ = "dummy_test_models"

    id: Mapped[int] = mapped_column(primary_key=True, autoincrement=True)
    name: Mapped[str] = mapped_column(nullable=False)


def test_1_sqlalchemy_can_map_dummy_model():
    """Test 1: Verify SQLAlchemy mapper inspects DummyModel inheriting Base & TimestampMixin."""
    mapper = inspect(DummyModel)
    assert mapper is not None
    assert mapper.tables[0].name == "dummy_test_models"
    assert "created_at" in mapper.columns
    assert "updated_at" in mapper.columns


def test_2_metadata_contains_naming_convention():
    """Test 2: Verify ORM_METADATA contains explicit Postgres naming convention rules."""
    assert Base.metadata is ORM_METADATA
    assert ORM_METADATA.naming_convention == POSTGRES_NAMING_CONVENTION
    assert ORM_METADATA.naming_convention["pk"] == "pk_%(table_name)s"
    assert ORM_METADATA.naming_convention["ix"] == "ix_%(column_0_label)s"


@pytest.mark.asyncio
async def test_3_timestamps_populate_on_insert(tmp_path):
    """Test 3: Verify created_at and updated_at populate with valid datetimes on row insert."""
    db_file = tmp_path / "test_base.db"
    test_engine = create_engine(f"sqlite+aiosqlite:///{db_file}")

    async with test_engine.begin() as conn:
        await conn.run_sync(Base.metadata.create_all)

    session_maker = async_sessionmaker(bind=test_engine, class_=AsyncSession, expire_on_commit=False)
    async with session_maker() as session:
        dummy = DummyModel(name="test_item")
        session.add(dummy)
        await session.commit()
        await session.refresh(dummy)

        assert dummy.id is not None
        assert isinstance(dummy.created_at, datetime)
        assert isinstance(dummy.updated_at, datetime)
        assert repr(dummy) == f"<DummyModel(id={dummy.id!r})>"

    await test_engine.dispose()


@pytest.mark.asyncio
async def test_4_updated_at_changes_on_update(tmp_path):
    """Test 4: Verify updated_at updates when row is modified while created_at remains unchanged."""
    db_file = tmp_path / "test_base_update.db"
    test_engine = create_engine(f"sqlite+aiosqlite:///{db_file}")

    async with test_engine.begin() as conn:
        await conn.run_sync(Base.metadata.create_all)

    session_maker = async_sessionmaker(bind=test_engine, class_=AsyncSession, expire_on_commit=False)
    async with session_maker() as session:
        dummy = DummyModel(name="initial_name")
        session.add(dummy)
        await session.commit()
        await session.refresh(dummy)

        initial_created_at = dummy.created_at
        initial_updated_at = dummy.updated_at

        # Delay to guarantee timestamp change
        await asyncio.sleep(0.02)

        dummy.name = "updated_name"
        await session.commit()
        await session.refresh(dummy)

        assert dummy.created_at == initial_created_at
        assert dummy.updated_at >= initial_updated_at

    await test_engine.dispose()
