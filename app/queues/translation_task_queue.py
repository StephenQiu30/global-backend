"""Stub queue adapter for translation task submission.

Production will use RQ/Redis. This in-memory stub records task IDs
for testing without external dependencies.
"""


class TranslationTaskQueue:
    """Queue adapter that enqueues translation task IDs."""

    def __init__(self) -> None:
        self._enqueued: list[str] = []

    def enqueue(self, task_id: str) -> str:
        """Enqueue a task ID for async execution.

        Args:
            task_id: The translation task identifier.

        Returns:
            The task ID (used as job reference).
        """
        self._enqueued.append(task_id)
        return task_id

    @property
    def enqueued_ids(self) -> list[str]:
        """Return list of enqueued task IDs (for testing)."""
        return list(self._enqueued)
