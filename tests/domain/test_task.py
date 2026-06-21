"""Tests for task domain models."""

import pytest
from app.domain.task import TaskStatus, FileMapping, Task


class TestTaskStatus:
    """Tests for TaskStatus enum."""

    def test_has_queued_status(self):
        assert TaskStatus.QUEUED == "queued"

    def test_has_running_status(self):
        assert TaskStatus.RUNNING == "running"

    def test_has_succeeded_status(self):
        assert TaskStatus.SUCCEEDED == "succeeded"

    def test_has_failed_status(self):
        assert TaskStatus.FAILED == "failed"


class TestFileMapping:
    """Tests for FileMapping model."""

    def test_create_file_mapping(self):
        mapping = FileMapping(source_path="README.md", target_path="README.zh-CN.md")
        assert mapping.source_path == "README.md"
        assert mapping.target_path == "README.zh-CN.md"

    def test_file_mapping_from_dict(self):
        data = {"source_path": "docs/guide.md", "target_path": "docs/guide.zh-CN.md"}
        mapping = FileMapping(**data)
        assert mapping.source_path == "docs/guide.md"
        assert mapping.target_path == "docs/guide.zh-CN.md"


class TestTask:
    """Tests for Task model."""

    def test_create_task_with_defaults(self):
        task = Task(
            task_id="task-001",
            installation_id="inst-123",
            repository="owner/repo",
            base_branch="main",
            files=["README.md"],
            language="zh-CN",
        )
        assert task.task_id == "task-001"
        assert task.installation_id == "inst-123"
        assert task.repository == "owner/repo"
        assert task.base_branch == "main"
        assert task.files == ["README.md"]
        assert task.language == "zh-CN"
        assert task.status == TaskStatus.QUEUED

    def test_create_task_with_custom_status(self):
        task = Task(
            task_id="task-002",
            installation_id="inst-456",
            repository="org/project",
            base_branch="develop",
            files=["README.md", "docs/guide.md"],
            language="ja",
            status=TaskStatus.RUNNING,
        )
        assert task.status == TaskStatus.RUNNING

    def test_task_multiple_files(self):
        task = Task(
            task_id="task-003",
            installation_id="inst-789",
            repository="company/product",
            base_branch="main",
            files=["README.md", "CONTRIBUTING.md", "docs/api.md"],
            language="ko",
        )
        assert len(task.files) == 3
