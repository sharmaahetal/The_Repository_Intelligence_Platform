import pytest
from pydantic import ValidationError

from backend.app.schemas import BaseSchema


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
