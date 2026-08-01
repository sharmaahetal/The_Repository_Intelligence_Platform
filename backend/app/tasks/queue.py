import asyncio
import uuid
from collections.abc import Awaitable, Callable
from dataclasses import dataclass, field
from datetime import UTC, datetime
from typing import Any

from backend.app.logging import logger


@dataclass
class BackgroundTask:
    task_id: str
    name: str
    payload: dict[str, Any]
    status: str = "queued"  # queued, running, completed, failed
    result: Any = None
    error: str | None = None
    created_at: datetime = field(default_factory=lambda: datetime.now(UTC))


class TaskQueue:
    """Async background task queue ensuring heavy batch processing does not block main request loops."""

    def __init__(self) -> None:
        self._queue: asyncio.Queue[BackgroundTask] = asyncio.Queue()
        self._tasks: dict[str, BackgroundTask] = {}
        self._handlers: dict[str, Callable[[dict[str, Any]], Awaitable[Any]]] = {}

    def register_handler(self, task_name: str, handler: Callable[[dict[str, Any]], Awaitable[Any]]) -> None:
        """Register handler coroutine for named task."""
        self._handlers[task_name] = handler

    async def enqueue(self, task_name: str, payload: dict[str, Any]) -> str:
        """Enqueues a background task for async execution. Returns task_id."""
        task_id = str(uuid.uuid4())
        task = BackgroundTask(task_id=task_id, name=task_name, payload=payload)
        self._tasks[task_id] = task
        await self._queue.put(task)
        logger.info("Enqueued background task", extra={"task_id": task_id, "task_name": task_name})
        return task_id

    def get_task_status(self, task_id: str) -> BackgroundTask | None:
        """Query task status by task_id."""
        return self._tasks.get(task_id)

    async def process_next(self) -> bool:
        """Pulls and executes next task from queue. Returns True if task processed."""
        if self._queue.empty():
            return False

        task = await self._queue.get()
        task.status = "running"
        handler = self._handlers.get(task.name)

        if not handler:
            task.status = "failed"
            task.error = f"No registered handler for task name '{task.name}'"
            logger.error("No handler registered for task", extra={"task_id": task.task_id, "task_name": task.name})
            return True

        try:
            result = await handler(task.payload)
            task.result = result
            task.status = "completed"
            logger.info("Background task completed", extra={"task_id": task.task_id, "task_name": task.name})
        except Exception as exc:
            task.status = "failed"
            task.error = str(exc)
            logger.error("Background task failed", extra={"task_id": task.task_id, "error": str(exc)})

        return True


# Global default task queue instance
default_task_queue = TaskQueue()
