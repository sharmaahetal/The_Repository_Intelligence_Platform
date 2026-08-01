from typing import Any

from sqlalchemy import select
from sqlalchemy.ext.asyncio import AsyncSession

from backend.app.logging import logger
from backend.app.models.raw_payload import RawPayload, RawRepositoryPayload


class RawPayloadRepository:
    """Data Access Layer for saving and retrieving raw GitHub payloads and collection metadata.

    Contains no business logic or snapshot building code.
    """

    def __init__(self, session: AsyncSession):
        self.session = session

    async def save_raw_payload(
        self,
        owner: str,
        repo: str,
        collector_type: str,
        raw_json: dict[str, Any] | RawRepositoryPayload,
        request_id: str | None = None,
        etag: str | None = None,
        api_version: str | None = None,
        rate_limit_remaining: int | None = None,
        headers: dict[str, Any] | None = None,
    ) -> RawPayload:
        """Persist unmodified GitHub API response payload with metadata to raw_payload_store."""
        if isinstance(raw_json, RawRepositoryPayload):
            payload_model = raw_json
            payload_data = payload_model.raw_json
            headers = headers or payload_model.headers
            etag = etag or payload_model.etag
            request_id = request_id or payload_model.request_id
            api_version = api_version or payload_model.api_version
            rate_limit_remaining = rate_limit_remaining or payload_model.rate_limit_remaining
            fetched_at = payload_model.fetched_at
        else:
            payload_data = raw_json
            fetched_at = None

        payload_entry = RawPayload(
            request_id=request_id,
            repo_owner=owner,
            repo_name=repo,
            collector_type=collector_type,
            raw_json=payload_data,
            etag=etag,
            api_version=api_version,
            rate_limit_remaining=rate_limit_remaining,
            headers=headers,
        )
        if fetched_at:
            payload_entry.fetched_at = fetched_at

        self.session.add(payload_entry)
        await self.session.commit()
        await self.session.refresh(payload_entry)

        logger.info(
            "Persisted raw payload in storage",
            extra={
                "payload_id": payload_entry.id,
                "request_id": request_id,
                "owner": owner,
                "repo": repo,
                "collector_type": collector_type,
            },
        )
        return payload_entry

    async def get_latest_raw_payload(
        self, owner: str, repo: str, collector_type: str = "repository"
    ) -> RawPayload | None:
        """Retrieve the most recent raw payload for a repository and collector."""
        stmt = (
            select(RawPayload)
            .where(
                RawPayload.repo_owner == owner,
                RawPayload.repo_name == repo,
                RawPayload.collector_type == collector_type,
            )
            .order_by(RawPayload.fetched_at.desc())
            .limit(1)
        )
        result = await self.session.execute(stmt)
        return result.scalars().first()
