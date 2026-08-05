"""Base Pydantic schemas for Repository Intelligence Platform."""

from pydantic import BaseModel, ConfigDict


class BaseSchema(BaseModel):
    """Base schema shared by all API request and response models."""

    model_config = ConfigDict(
        from_attributes=True,
        populate_by_name=True,
        extra="forbid",
    )
