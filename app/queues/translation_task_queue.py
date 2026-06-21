import rq
from redis import Redis

from app.core.config import Settings
from app.workers.translation_jobs import run_translation_task


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
