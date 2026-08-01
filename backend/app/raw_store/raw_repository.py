from typing import Any

from app.logging import logger
from app.models.raw_payload import RawPayload
from sqlalchemy import select
from sqlalchemy.ext.asyncio import AsyncSession


class RawPayloadRepository:
    """Data Access Layer for saving and retrieving raw GitHub payloads and collection metadata."""

    def __init__(self, session: AsyncSession):
        self.session = session

    async def save_raw_payload(
        self,
        owner: str,
        repo: str,
        collector_type: str,
        raw_json: dict[str, Any],
        request_id: str | None = None,
        etag: str | None = None,
        api_version: str | None = None,
        rate_limit_remaining: int | None = None,
        headers: dict[str, Any] | None = None,
    ) -> RawPayload:
        """Persist unmodified GitHub API response payload with metadata."""
        payload = RawPayload(
            request_id=request_id,
            repo_owner=owner,
            repo_name=repo,
            collector_type=collector_type,
            raw_json=raw_json,
            etag=etag,
            api_version=api_version,
            rate_limit_remaining=rate_limit_remaining,
            headers=headers,
        )
        self.session.add(payload)
        await self.session.commit()
        await self.session.refresh(payload)
        logger.info(
            "Persisted raw payload in storage",
            extra={
                "payload_id": payload.id,
                "request_id": request_id,
                "owner": owner,
                "repo": repo,
                "collector_type": collector_type,
            },
        )
        return payload

    async def get_latest_raw_payload(
        self, owner: str, repo: str, collector_type: str
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
