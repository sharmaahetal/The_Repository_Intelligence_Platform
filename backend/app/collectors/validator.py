from typing import Any
from app.logging import logger
from app.models.domain import RawRepositoryPayload


class RawPayloadValidator:
    """Validator ensuring raw response dictionaries match domain payload models."""

    def validate_repository_payload(
        self, raw_data: dict[str, Any], request_id: str | None = None
    ) -> RawRepositoryPayload:
        """Validate raw dictionary response into RawRepositoryPayload model."""
        if not isinstance(raw_data, dict):
            raise ValueError(f"Payload must be a dictionary, got {type(raw_data)}")

        payload = RawRepositoryPayload.model_validate(raw_data)
        logger.info(
            "Validated raw repository payload",
            extra={
                "owner": payload.owner_login,
                "repo": payload.name,
                "request_id": request_id,
            },
        )
        return payload
