from unittest.mock import MagicMock, patch

import pytest


class TestTranslationTaskQueueEnqueue:
    """TranslationTaskQueue.enqueue must enqueue exactly one RQ job."""

    @patch("app.queues.translation_task_queue.rq.Queue")
    @patch("app.queues.translation_task_queue.Settings")
    def test_enqueue_calls_rq_queue_enqueue(self, mock_settings_cls, mock_queue_cls):
        """enqueue(task_id) must call rq.Queue.enqueue with the worker job."""
        mock_settings_cls.return_value = MagicMock(
            rq_queue_name="translation", redis_url="redis://localhost:6379/0"
        )
        mock_queue = MagicMock()
        mock_queue_cls.return_value = mock_queue

        from app.queues.translation_task_queue import TranslationTaskQueue

        queue = TranslationTaskQueue()
        queue.enqueue("task-abc")

        mock_queue.enqueue.assert_called_once()
        args, kwargs = mock_queue.enqueue.call_args
        assert args[0].__name__ == "run_translation_task"
        assert kwargs.get("task_id") == "task-abc"

    @patch("app.queues.translation_task_queue.rq.Queue")
    @patch("app.queues.translation_task_queue.Settings")
    def test_enqueue_returns_rq_job(self, mock_settings_cls, mock_queue_cls):
        """enqueue must return the RQ job object."""
        mock_settings_cls.return_value = MagicMock(
            rq_queue_name="translation", redis_url="redis://localhost:6379/0"
        )
        mock_queue = MagicMock()
        mock_job = MagicMock()
        mock_queue.enqueue.return_value = mock_job
        mock_queue_cls.return_value = mock_queue

        from app.queues.translation_task_queue import TranslationTaskQueue

        queue = TranslationTaskQueue()
        result = queue.enqueue("task-abc")

        assert result is mock_job

    @patch("app.queues.translation_task_queue.rq.Queue")
    @patch("app.queues.translation_task_queue.Settings")
    def test_enqueue_uses_configured_queue_name(self, mock_settings_cls, mock_queue_cls):
        """Queue must be created with the queue name from config."""
        mock_settings_cls.return_value = MagicMock(
            rq_queue_name="my-queue", redis_url="redis://localhost:6379/0"
        )
        mock_queue_cls.return_value = MagicMock()

        from app.queues.translation_task_queue import TranslationTaskQueue

        TranslationTaskQueue()

        _, kwargs = mock_queue_cls.call_args
        assert kwargs["name"] == "my-queue"

    @patch("app.queues.translation_task_queue.rq.Queue")
    @patch("app.queues.translation_task_queue.Settings")
    def test_enqueue_passes_redis_connection(self, mock_settings_cls, mock_queue_cls):
        """Queue must be created with a Redis connection."""
        mock_settings_cls.return_value = MagicMock(
            rq_queue_name="translation", redis_url="redis://localhost:6379/0"
        )
        mock_queue_cls.return_value = MagicMock()

        from app.queues.translation_task_queue import TranslationTaskQueue

        TranslationTaskQueue()

        _, kwargs = mock_queue_cls.call_args
        assert "connection" in kwargs


class TestTranslationTaskQueueConfig:
    """TranslationTaskQueue must read queue name from settings."""

    @patch("app.queues.translation_task_queue.rq.Queue")
    @patch("app.queues.translation_task_queue.Settings")
    def test_uses_queue_name_from_settings(self, mock_settings_cls, mock_queue_cls):
        """Queue name must come from settings.rq_queue_name."""
        mock_settings_cls.return_value = MagicMock(
            rq_queue_name="custom-queue", redis_url="redis://localhost:6379/0"
        )
        mock_queue_cls.return_value = MagicMock()

        from app.queues.translation_task_queue import TranslationTaskQueue

        TranslationTaskQueue()

        _, kwargs = mock_queue_cls.call_args
        assert kwargs["name"] == "custom-queue"


class TestRunTranslationTask:
    """Worker job entrypoint must accept task_id and log processing."""

    def test_accepts_task_id(self):
        """run_translation_task must accept a task_id string argument."""
        from app.workers.translation_jobs import run_translation_task

        # Should not raise
        run_translation_task("task-123")

    def test_logs_task_id(self, caplog):
        """run_translation_task must log the task_id being processed."""
        import logging

        from app.workers.translation_jobs import run_translation_task

        with caplog.at_level(logging.INFO):
            run_translation_task("task-456")

        assert "task-456" in caplog.text

    def test_enqueue_targets_worker_function(self):
        """TranslationTaskQueue.enqueue must target run_translation_task."""
        from app.queues.translation_task_queue import TranslationTaskQueue
        from app.workers.translation_jobs import run_translation_task

        with (
            patch("app.queues.translation_task_queue.rq.Queue") as mock_queue_cls,
            patch("app.queues.translation_task_queue.Settings") as mock_settings_cls,
        ):
            mock_settings_cls.return_value = MagicMock(
                rq_queue_name="translation", redis_url="redis://localhost:6379/0"
            )
            mock_queue = MagicMock()
            mock_queue_cls.return_value = mock_queue

            queue = TranslationTaskQueue()
            queue.enqueue("task-abc")

            args, _ = mock_queue.enqueue.call_args
            assert args[0] is run_translation_task
