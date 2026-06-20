"""Tests for TaskRunner service."""

import pytest
from unittest.mock import AsyncMock

from app.domain.task import Task, TaskStatus, TaskResult, FileMapping
from app.services.translation_provider import FakeTranslationProvider
from app.services.task_runner import TaskRunner


def make_task(files=None, language="zh-CN"):
    """Helper to create a Task for testing."""
    return Task(
        task_id="test-task-001",
        installation_id="inst-123",
        repository="owner/repo",
        base_branch="main",
        files=files or ["README.md"],
        language=language,
    )


class TestTaskRunnerSuccess:
    """Tests for successful task execution."""

    @pytest.mark.asyncio
    async def test_single_file_success(self):
        fake_github = AsyncMock()
        fake_github.get_file_content.return_value = "# Hello World\n\nWelcome."
        provider = FakeTranslationProvider()
        runner = TaskRunner(provider, fake_github)

        task = make_task(files=["README.md"])
        result = await runner.run(task)

        assert result.status == TaskStatus.SUCCEEDED
        assert result.pr_url is not None
        assert result.pr_number is not None
        assert len(result.mappings) == 1
        assert result.mappings[0].source_path == "README.md"
        assert result.mappings[0].target_path == "README.zh-CN.md"
        assert result.error_code is None

    @pytest.mark.asyncio
    async def test_multiple_files_success(self):
        fake_github = AsyncMock()
        fake_github.get_file_content.return_value = "# File content"
        provider = FakeTranslationProvider()
        runner = TaskRunner(provider, fake_github)

        task = make_task(files=["README.md", "docs/guide.md"])
        result = await runner.run(task)

        assert result.status == TaskStatus.SUCCEEDED
        assert len(result.mappings) == 2
        assert result.mappings[0].source_path == "README.md"
        assert result.mappings[0].target_path == "README.zh-CN.md"
        assert result.mappings[1].source_path == "docs/guide.md"
        assert result.mappings[1].target_path == "docs/guide.zh-CN.md"

    @pytest.mark.asyncio
    async def test_task_status_transitions(self):
        fake_github = AsyncMock()
        fake_github.get_file_content.return_value = "# Content"
        provider = FakeTranslationProvider()
        runner = TaskRunner(provider, fake_github)

        task = make_task()
        assert task.status == TaskStatus.QUEUED

        result = await runner.run(task)
        assert result.status == TaskStatus.SUCCEEDED


class TestTaskRunnerErrors:
    """Tests for task runner error handling."""

    @pytest.mark.asyncio
    async def test_file_read_error(self):
        fake_github = AsyncMock()
        fake_github.get_file_content.side_effect = Exception("File not found")
        provider = FakeTranslationProvider()
        runner = TaskRunner(provider, fake_github)

        task = make_task(files=["missing.md"])
        result = await runner.run(task)

        assert result.status == TaskStatus.FAILED
        assert result.error_code == "file_read_error"
        assert result.error_message is not None
        assert result.pr_url is None

    @pytest.mark.asyncio
    async def test_translation_error(self):
        fake_github = AsyncMock()
        fake_github.get_file_content.return_value = "# Content"

        failing_provider = AsyncMock()
        failing_provider.translate_markdown.side_effect = Exception("Provider error")
        runner = TaskRunner(failing_provider, fake_github)

        task = make_task()
        result = await runner.run(task)

        assert result.status == TaskStatus.FAILED
        assert result.error_code == "translation_error"
        assert result.error_message is not None

    @pytest.mark.asyncio
    async def test_error_does_not_leak_internal_details(self):
        fake_github = AsyncMock()
        fake_github.get_file_content.side_effect = Exception("SECRET_KEY=abc123")
        provider = FakeTranslationProvider()
        runner = TaskRunner(provider, fake_github)

        task = make_task()
        result = await runner.run(task)

        assert result.status == TaskStatus.FAILED
        assert "SECRET_KEY" not in (result.error_message or "")
        assert "abc123" not in (result.error_message or "")
