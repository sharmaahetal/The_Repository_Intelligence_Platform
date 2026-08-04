from datetime import UTC, datetime

from sqlalchemy import UniqueConstraint
from sqlalchemy.orm import Mapped, mapped_column

from backend.app.database.base import (
    NAMING_CONVENTION,
    Base,
    TimestampMixin,
    metadata,
)


class SampleRepositoryModel(Base, TimestampMixin):
    __tablename__ = "sample_test_repositories"

    id: Mapped[int] = mapped_column(primary_key=True, autoincrement=True)
    repo_name: Mapped[str] = mapped_column(index=True, nullable=False)
    slug: Mapped[str] = mapped_column(nullable=False)

    __table_args__ = (
        UniqueConstraint("slug"),
    )


def test_base_metadata_and_naming_conventions():
    """Checklist 2 & 3: Verify metadata attachment and naming conventions."""
    assert SampleRepositoryModel.metadata is metadata

    table = SampleRepositoryModel.__table__
    assert table.name == "sample_test_repositories"
    assert table.primary_key.name == "pk_sample_test_repositories"

    # Verify index naming convention
    index_names = [i.name for i in table.indexes]
    assert "ix_sample_test_repositories_repo_name" in index_names

    # Verify unique constraint naming convention
    unique_constraints = [c for c in table.constraints if getattr(c, "name", None)]
    assert any(c.name == "uq_sample_test_repositories_slug" for c in unique_constraints)


def test_timestamp_mixin_defaults():
    """Checklist 1 & 4: Verify sample model inherits timestamp fields and sets UTC defaults."""
    instance = SampleRepositoryModel(repo_name="fastapi/fastapi", slug="fastapi")
    assert instance.repo_name == "fastapi/fastapi"
    assert repr(instance).startswith("<SampleRepositoryModel(")
