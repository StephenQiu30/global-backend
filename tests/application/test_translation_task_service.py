"""Tests for TranslationTaskService."""

from unittest.mock import AsyncMock, MagicMock

import pytest

from app.domain.task import TaskResult, TaskStatus


class TestTranslationTaskServiceCreateTask:
    """Test create_task method."""

    @pytest.mark.asyncio
    async def test_create_task_success(self):
        """create_task returns TaskResult on success."""
        from app.application.translation_task_service import (
            TranslationTaskRequest,
            TranslationTaskService,
        )

        mock_runner = AsyncMock()
        mock_runner.run.return_value = TaskResult(
            status=TaskStatus.SUCCEEDED,
            pr_url="https://github.com/owner/repo/pull/1",
            pr_number=1,
        )

        service = TranslationTaskService(task_runner=mock_runner)
        request = TranslationTaskRequest(
            installation_id="123",
            repository="owner/repo",
            base_branch="main",
            files=["README.md"],
            language="zh-CN",
        )

        result = await service.create_task(request)

        assert result.status == TaskStatus.SUCCEEDED
        assert result.pr_url == "https://github.com/owner/repo/pull/1"
        mock_runner.run.assert_called_once()

    @pytest.mark.asyncio
    async def test_create_task_unsupported_language(self):
        """create_task raises UnsupportedLanguageError for invalid language."""
        from app.application.translation_task_service import (
            TranslationTaskRequest,
            TranslationTaskService,
            UnsupportedLanguageError,
        )

        mock_runner = AsyncMock()
        service = TranslationTaskService(task_runner=mock_runner)
        request = TranslationTaskRequest(
            installation_id="123",
            repository="owner/repo",
            base_branch="main",
            files=["README.md"],
            language="invalid-lang",
        )

        with pytest.raises(UnsupportedLanguageError):
            await service.create_task(request)

        mock_runner.run.assert_not_called()

    @pytest.mark.asyncio
    async def test_create_task_delegates_to_runner(self):
        """create_task constructs Task and delegates to TaskRunner."""
        from app.application.translation_task_service import (
            TranslationTaskRequest,
            TranslationTaskService,
        )

        mock_runner = AsyncMock()
        mock_runner.run.return_value = TaskResult(status=TaskStatus.SUCCEEDED)

        service = TranslationTaskService(task_runner=mock_runner)
        request = TranslationTaskRequest(
            installation_id="456",
            repository="org/project",
            base_branch="develop",
            files=["docs/guide.md", "README.md"],
            language="ja",
        )

        await service.create_task(request)

        call_args = mock_runner.run.call_args[0][0]
        assert call_args.installation_id == "456"
        assert call_args.repository == "org/project"
        assert call_args.base_branch == "develop"
        assert call_args.files == ["docs/guide.md", "README.md"]
        assert call_args.language == "ja"
        assert call_args.status == TaskStatus.QUEUED
