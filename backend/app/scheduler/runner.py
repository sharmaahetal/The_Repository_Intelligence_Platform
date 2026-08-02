import asyncio
from collections.abc import Awaitable, Callable
from dataclasses import dataclass
from datetime import UTC, datetime
from typing import Any

from backend.app.logging import logger


@dataclass
class ScheduledJob:
    job_id: str
    name: str
    cron_interval_seconds: int
    func: Callable[[], Awaitable[None]] | Callable[[], None]
    last_run: datetime | None = None
    run_count: int = 0


class PlatformScheduler:
    """Background task scheduler executing periodic jobs outside route handlers."""

    def __init__(self) -> None:
        self._jobs: dict[str, ScheduledJob] = {}
        self._is_running = False

    def add_job(
        self,
        job_id: str,
        name: str,
        interval_seconds: int,
        func: Callable[[], Awaitable[None]] | Callable[[], None],
    ) -> None:
        """Register a periodic job with a given interval in seconds."""
        job = ScheduledJob(
            job_id=job_id,
            name=name,
            cron_interval_seconds=interval_seconds,
            func=func,
        )
        self._jobs[job_id] = job
        logger.info(
            "Scheduled job registered",
            extra={"job_id": job_id, "job_name": name, "interval_s": interval_seconds},
        )

    async def run_job_once(self, job_id: str) -> None:
        """Executes a single job immediately."""
        if job_id not in self._jobs:
            raise KeyError(f"Scheduled job '{job_id}' not found.")

        job = self._jobs[job_id]
        logger.info("Executing scheduled job", extra={"job_id": job_id, "job_name": job.name})
        try:
            if asyncio.iscoroutinefunction(job.func):
                await job.func()
            else:
                job.func()
            job.last_run = datetime.now(UTC)
            job.run_count += 1
            logger.info("Scheduled job completed", extra={"job_id": job_id, "runs": job.run_count})
        except Exception as exc:
            logger.error("Scheduled job failed", extra={"job_id": job_id, "error": str(exc)})

    def get_registered_jobs(self) -> list[dict[str, Any]]:
        """Retrieve overview of registered scheduled jobs."""
        return [
            {
                "job_id": j.job_id,
                "name": j.name,
                "interval_seconds": j.cron_interval_seconds,
                "last_run": j.last_run.isoformat() if j.last_run else None,
                "run_count": j.run_count,
            }
            for j in self._jobs.values()
        ]


# Global scheduler instance
default_scheduler = PlatformScheduler()
