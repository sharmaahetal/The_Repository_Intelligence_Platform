import uuid
from datetime import UTC, datetime

from backend.app.collectors.repository import RepositoryCollector
from backend.app.collectors.validator import RawPayloadValidator
from backend.app.logging import logger
from backend.app.models.snapshot import RepositorySnapshot
from backend.app.raw_store.raw_repository import RawPayloadRepository
from backend.app.snapshots.snapshot_builder import SnapshotBuilder


class RepositorySnapshotService:
    """Application Orchestration Service coordinating collection, validation, raw storage, and snapshot creation."""

    def __init__(
        self,
        collector: RepositoryCollector | None = None,
        validator: RawPayloadValidator | None = None,
        builder: SnapshotBuilder | None = None,
        raw_repository: RawPayloadRepository | None = None,
    ):
        self.collector = collector or RepositoryCollector()
        self.validator = validator or RawPayloadValidator()
        self.builder = builder or SnapshotBuilder()
        self.raw_repository = raw_repository

    async def get_snapshot(self, owner: str, repo: str) -> RepositorySnapshot:
        """Convenience alias for collect_and_build_snapshot."""
        return await self.collect_and_build_snapshot(owner=owner, repo=repo)

    async def collect_and_build_snapshot(
        self,
        owner: str,
        repo: str,
        snapshot_time: datetime | None = None,
        request_id: str | None = None,
    ) -> RepositorySnapshot:
        """Orchestrates end-to-end repository pipeline execution for a single job."""
        req_id = request_id or f"req-{uuid.uuid4().hex[:12]}"
        t_snapshot = snapshot_time or datetime.now(UTC)

        logger.info(
            "Starting repository snapshot collection pipeline",
            extra={"owner": owner, "repo": repo, "request_id": req_id},
        )

        # 1. Collect raw response
        gh_response = await self.collector.fetch_repository(owner, repo, request_id=req_id)

        # 2. Validate raw payload
        raw_payload = self.validator.validate_repository_payload(
            gh_response.data if isinstance(gh_response.data, dict) else {},
            request_id=req_id,
        )

        # 3. Optional: Persist raw payload and HTTP response metadata
        if self.raw_repository is not None:
            await self.raw_repository.save_raw_payload(
                owner=owner,
                repo=repo,
                collector_type="repository",
                raw_json=gh_response.data if isinstance(gh_response.data, dict) else {},
                request_id=req_id,
                etag=gh_response.etag,
                api_version=gh_response.api_version,
                rate_limit_remaining=gh_response.rate_limit_remaining,
                headers=gh_response.headers,
            )

        # 4. Build deterministic point-in-time snapshot
        snapshot = self.builder.build_snapshot_from_raw(
            raw_payload=raw_payload,
            snapshot_time=t_snapshot,
            request_id=req_id,
        )

        logger.info(
            "Successfully generated repository snapshot S(t_k)",
            extra={
                "owner": owner,
                "repo": repo,
                "request_id": req_id,
                "schema_version": snapshot.schema_version,
            },
        )
        return snapshot
