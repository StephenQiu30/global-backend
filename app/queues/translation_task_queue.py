"""Queue adapter for translation task submission.

Supports two modes:
- Production: RQ/Redis queue for async execution
- Stub: In-memory queue for testing (when Redis is unavailable)
"""

from typing import Protocol

import rq
from redis import Redis

from app.core.config import Settings
from app.workers.translation_jobs import run_translation_task


class QueueAdapter(Protocol):
    """Protocol for queue adapters."""

    def enqueue(self, task_id: str) -> str:
        """Enqueue a task ID for async execution."""
        ...


class StubTranslationTaskQueue:
    """In-memory stub queue for testing."""

    def __init__(self) -> None:
        self._enqueued: list[str] = []

    def enqueue(self, task_id: str) -> str:
        """Enqueue a task ID (in-memory)."""
        self._enqueued.append(task_id)
        return task_id

    @property
    def enqueued_ids(self) -> list[str]:
        """Return list of enqueued task IDs (for testing)."""
        return list(self._enqueued)


class TranslationTaskQueue:
    """Minimal RQ queue adapter for translation tasks."""

    def __init__(self) -> None:
        settings = Settings()
        self._queue = rq.Queue(
            name=settings.rq_queue_name,
            connection=Redis.from_url(settings.redis_url),
        )

    def enqueue(self, task_id: str) -> rq.job.Job:
        """Enqueue a translation task by ID."""
        return self._queue.enqueue(run_translation_task, task_id=task_id)
