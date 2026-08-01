import uuid
from datetime import UTC, datetime

from backend.app.collectors.repository_collector import RepositoryCollector
from backend.app.collectors.validator import RawPayloadValidator
from backend.app.logging import logger
from backend.app.models.snapshot import RepositorySnapshot
from backend.app.raw_store.raw_payload_repository import RawPayloadRepository
from backend.app.snapshots.snapshot_builder import SnapshotBuilder
from backend.app.snapshots.snapshot_repository import SnapshotRepository


class SnapshotService:
    """Application Orchestration Service coordinating:

    Collect -> Validate -> Store Raw -> Build Snapshot -> Store Snapshot -> Return Snapshot.

    Contains no FastAPI API routes or background schedulers.
    """

    def __init__(
        self,
        collector: RepositoryCollector | None = None,
        validator: RawPayloadValidator | None = None,
        builder: SnapshotBuilder | None = None,
        raw_repository: RawPayloadRepository | None = None,
        snapshot_repository: SnapshotRepository | None = None,
    ):
        self.collector = collector or RepositoryCollector()
        self.validator = validator or RawPayloadValidator()
        self.builder = builder or SnapshotBuilder()
        self.raw_repository = raw_repository
        self.snapshot_repository = snapshot_repository or SnapshotRepository()

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

        # 1. Collect and validate raw payload
        raw_payload = await self.collector.collect_repository(
            owner=owner,
            repo=repo,
            request_id=req_id,
        )

        # 2. Persist raw payload (if repository configured)
        if self.raw_repository is not None:
            await self.raw_repository.save_raw_payload(
                owner=owner,
                repo=repo,
                collector_type="repository",
                raw_json=raw_payload,
                request_id=req_id,
            )

        # 3. Build deterministic point-in-time snapshot S(t_k)
        snapshot = self.builder.build_snapshot_from_raw(
            raw_payload=raw_payload,
            snapshot_time=t_snapshot,
            request_id=req_id,
        )

        # 4. Persist snapshot in SnapshotRepository
        if self.snapshot_repository is not None:
            await self.snapshot_repository.save_snapshot(snapshot)

        logger.info(
            "Successfully generated and saved repository snapshot S(t_k)",
            extra={
                "owner": owner,
                "repo": repo,
                "request_id": req_id,
                "schema_version": snapshot.schema_version,
            },
        )
        return snapshot


# Backward-compatible alias
RepositorySnapshotService = SnapshotService
