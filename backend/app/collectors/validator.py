from datetime import datetime
from typing import Any

from backend.app.logging import logger
from backend.app.models.raw_payload import RawRepositoryPayload


class RawPayloadValidator:
    """Validator ensuring raw response dictionaries match GitHub payload specs and domain models."""

    def validate_repository_payload(
        self,
        raw_data: dict[str, Any],
        headers: dict[str, str] | None = None,
        request_id: str | None = None,
    ) -> RawRepositoryPayload:
        """Validate raw dictionary response into RawRepositoryPayload model.

        Rejects missing required fields, invalid timestamps, and invalid repository IDs.
        """
        if not isinstance(raw_data, dict):
            raise ValueError(f"Payload must be a dictionary, got {type(raw_data)}")

        # 1. Required field: name
        repo_name = raw_data.get("name")
        if not repo_name or not isinstance(repo_name, str) or not repo_name.strip():
            raise ValueError("Payload missing required non-empty string field 'name'")

        # 2. Required field: owner
        owner_val = raw_data.get("owner")
        if owner_val is None:
            raise ValueError("Payload missing required field 'owner'")
        if isinstance(owner_val, dict):
            login = owner_val.get("login")
            if not login or not isinstance(login, str) or not login.strip():
                raise ValueError("Payload owner dictionary missing non-empty 'login' handle")
        elif not isinstance(owner_val, str) or not owner_val.strip():
            raise ValueError("Payload owner field must be a valid dict or string login")

        # 3. Validate integer ID if present
        if "id" in raw_data:
            repo_id = raw_data["id"]
            if not isinstance(repo_id, int) or repo_id <= 0:
                raise ValueError(f"Invalid repository ID '{repo_id}'; must be a positive integer")

        # 4. Validate ISO timestamp strings if present
        for ts_field in ("created_at", "updated_at", "pushed_at"):
            ts_val = raw_data.get(ts_field)
            if ts_val is not None and isinstance(ts_val, str):
                try:
                    datetime.fromisoformat(ts_val.replace("Z", "+00:00"))
                except ValueError as exc:
                    raise ValueError(f"Invalid timestamp format for '{ts_field}': '{ts_val}'") from exc

        # Construct validated RawRepositoryPayload preserving headers & metadata
        payload = RawRepositoryPayload.from_dict(raw_data, headers=headers)
        if request_id and payload.request_id is None:
            # Inject request_id if not present in headers
            payload = payload.model_copy(update={"request_id": request_id})

        logger.info(
            "Validated raw repository payload",
            extra={
                "owner": payload.owner_login,
                "repo": payload.name,
                "request_id": request_id,
            },
        )
        return payload
