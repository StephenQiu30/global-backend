from unittest.mock import MagicMock, patch

import pytest


class TestTranslationTaskQueueEnqueue:
    """TranslationTaskQueue.enqueue must enqueue exactly one RQ job."""

    @patch("app.queues.translation_task_queue.rq.Queue")
    def test_enqueue_calls_rq_queue_enqueue(self, mock_queue_cls):
        """enqueue(task_id) must call rq.Queue.enqueue with the worker job."""
        mock_queue = MagicMock()
        mock_queue_cls.return_value = mock_queue

        from app.queues.translation_task_queue import TranslationTaskQueue

        queue = TranslationTaskQueue()
        queue.enqueue("task-abc")

        mock_queue.enqueue.assert_called_once()
        args, kwargs = mock_queue.enqueue.call_args
        assert args[0].__name__ == "run_translation_task"
        assert kwargs.get("task_id") == "task-abc" or (len(args) > 1 and args[1] == "task-abc")

    @patch("app.queues.translation_task_queue.rq.Queue")
    def test_enqueue_returns_rq_job(self, mock_queue_cls):
        """enqueue must return the RQ job object."""
        mock_queue = MagicMock()
        mock_job = MagicMock()
        mock_queue.enqueue.return_value = mock_job
        mock_queue_cls.return_value = mock_queue

        from app.queues.translation_task_queue import TranslationTaskQueue

        queue = TranslationTaskQueue()
        result = queue.enqueue("task-abc")

        assert result is mock_job

    @patch("app.queues.translation_task_queue.rq.Queue")
    def test_enqueue_uses_configured_queue_name(self, mock_queue_cls):
        """Queue must be created with the queue name from config."""
        mock_queue_cls.return_value = MagicMock()

        from app.queues.translation_task_queue import TranslationTaskQueue

        TranslationTaskQueue()

        _, kwargs = mock_queue_cls.call_args
        assert kwargs.get("name") is not None or (len(mock_queue_cls.call_args[0]) > 0)

    @patch("app.queues.translation_task_queue.rq.Queue")
    def test_enqueue_passes_connection(self, mock_queue_cls):
        """Queue must be created with a Redis connection."""
        mock_queue_cls.return_value = MagicMock()

        from app.queues.translation_task_queue import TranslationTaskQueue

        TranslationTaskQueue()

        _, kwargs = mock_queue_cls.call_args
        assert "connection" in kwargs or len(mock_queue_cls.call_args[0]) > 1


class TestTranslationTaskQueueConfig:
    """TranslationTaskQueue must read queue name from settings."""

    @patch("app.queues.translation_task_queue.rq.Queue")
    def test_uses_queue_name_from_settings(self, mock_queue_cls):
        """Queue name must come from settings.rq_queue_name."""
        mock_queue_cls.return_value = MagicMock()

        from app.queues.translation_task_queue import TranslationTaskQueue

        with patch(
            "app.queues.translation_task_queue.get_settings",
            return_value=MagicMock(rq_queue_name="custom-queue", redis_url="redis://localhost:6379/0"),
        ):
            TranslationTaskQueue()

        _, kwargs = mock_queue_cls.call_args
        assert kwargs.get("name") == "custom-queue"
