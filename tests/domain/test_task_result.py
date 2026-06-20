"""Tests for task result domain models and error types."""

import pytest

from app.domain.task import TaskStatus, FileMapping, TaskResult
from app.core.errors import AppError


class TestTaskStatus:
    """Test TaskStatus enum values and type."""

    def test_is_str_enum(self):
        """GIVEN TaskStatus THEN it is a str Enum."""
        assert issubclass(TaskStatus, str)

    def test_queued_value(self):
        """GIVEN TaskStatus.QUEUED THEN value is 'queued'."""
        assert TaskStatus.QUEUED.value == "queued"

    def test_running_value(self):
        """GIVEN TaskStatus.RUNNING THEN value is 'running'."""
        assert TaskStatus.RUNNING.value == "running"

    def test_succeeded_value(self):
        """GIVEN TaskStatus.SUCCEEDED THEN value is 'succeeded'."""
        assert TaskStatus.SUCCEEDED.value == "succeeded"

    def test_failed_value(self):
        """GIVEN TaskStatus.FAILED THEN value is 'failed'."""
        assert TaskStatus.FAILED.value == "failed"

    def test_all_values(self):
        """GIVEN TaskStatus THEN it has exactly 4 members."""
        assert len(TaskStatus) == 4


class TestFileMapping:
    """Test FileMapping model serialization."""

    def test_create_with_fields(self):
        """GIVEN source_path and target_path THEN creates FileMapping."""
        mapping = FileMapping(source_path="README.md", target_path="README.zh-CN.md")
        assert mapping.source_path == "README.md"
        assert mapping.target_path == "README.zh-CN.md"

    def test_serialization(self):
        """GIVEN FileMapping THEN serializes to dict with both fields."""
        mapping = FileMapping(source_path="docs/guide.md", target_path="docs/guide.zh-CN.md")
        data = mapping.model_dump()
        assert data == {"source_path": "docs/guide.md", "target_path": "docs/guide.zh-CN.md"}


class TestTaskResultSucceeded:
    """Test TaskResult serialization for succeeded state."""

    def test_succeeded_with_pr_info(self):
        """GIVEN succeeded TaskResult with PR info THEN all fields present."""
        result = TaskResult(
            status=TaskStatus.SUCCEEDED,
            pr_url="https://github.com/owner/repo/pull/42",
            pr_number=42,
            mappings=[
                FileMapping(source_path="README.md", target_path="README.zh-CN.md"),
            ],
        )
        assert result.status == TaskStatus.SUCCEEDED
        assert result.pr_url == "https://github.com/owner/repo/pull/42"
        assert result.pr_number == 42
        assert len(result.mappings) == 1
        assert result.error_code is None
        assert result.error_message is None

    def test_succeeded_serialization_exclude_none(self):
        """GIVEN succeeded TaskResult THEN serialization excludes None fields."""
        result = TaskResult(
            status=TaskStatus.SUCCEEDED,
            pr_url="https://github.com/owner/repo/pull/42",
            pr_number=42,
            mappings=[FileMapping(source_path="README.md", target_path="README.zh-CN.md")],
        )
        data = result.model_dump(exclude_none=True)
        assert "error_code" not in data
        assert "error_message" not in data
        assert data["status"] == "succeeded"
        assert data["pr_url"] == "https://github.com/owner/repo/pull/42"

    def test_succeeded_status_value(self):
        """GIVEN succeeded TaskResult THEN status serializes as string."""
        result = TaskResult(status=TaskStatus.SUCCEEDED)
        data = result.model_dump()
        assert data["status"] == "succeeded"


class TestTaskResultFailed:
    """Test TaskResult serialization for failed state."""

    def test_failed_with_error_info(self):
        """GIVEN failed TaskResult with error info THEN error fields present."""
        result = TaskResult(
            status=TaskStatus.FAILED,
            error_code="github_permission_denied",
            error_message="GitHub App lacks repository access",
        )
        assert result.status == TaskStatus.FAILED
        assert result.error_code == "github_permission_denied"
        assert result.error_message == "GitHub App lacks repository access"
        assert result.pr_url is None
        assert result.pr_number is None
        assert result.mappings is None

    def test_failed_serialization_exclude_none(self):
        """GIVEN failed TaskResult THEN serialization excludes None fields."""
        result = TaskResult(
            status=TaskStatus.FAILED,
            error_code="model_timeout",
            error_message="LLM provider timed out",
        )
        data = result.model_dump(exclude_none=True)
        assert "pr_url" not in data
        assert "pr_number" not in data
        assert "mappings" not in data
        assert data["status"] == "failed"
        assert data["error_code"] == "model_timeout"

    def test_failed_status_value(self):
        """GIVEN failed TaskResult THEN status serializes as string."""
        result = TaskResult(status=TaskStatus.FAILED)
        data = result.model_dump()
        assert data["status"] == "failed"


class TestTaskResultDefaults:
    """Test TaskResult default field values."""

    def test_default_none_fields(self):
        """GIVEN TaskResult with only status THEN optional fields are None."""
        result = TaskResult(status=TaskStatus.QUEUED)
        assert result.pr_url is None
        assert result.pr_number is None
        assert result.mappings is None
        assert result.error_code is None
        assert result.error_message is None


class TestAppError:
    """Test AppError exception type."""

    def test_has_code_field(self):
        """GIVEN AppError with code THEN code is accessible."""
        err = AppError(code="test_error", message="Test message")
        assert err.code == "test_error"

    def test_has_message_field(self):
        """GIVEN AppError with message THEN message is accessible."""
        err = AppError(code="test_error", message="Test message")
        assert err.message == "Test message"

    def test_retryable_defaults_false(self):
        """GIVEN AppError without retryable THEN retryable is False."""
        err = AppError(code="test_error", message="Test message")
        assert err.retryable is False

    def test_retryable_can_be_true(self):
        """GIVEN AppError with retryable=True THEN retryable is True."""
        err = AppError(code="test_error", message="Test message", retryable=True)
        assert err.retryable is True

    def test_is_exception(self):
        """GIVEN AppError THEN it is an Exception."""
        err = AppError(code="test_error", message="Test message")
        assert isinstance(err, Exception)

    def test_str_representation(self):
        """GIVEN AppError THEN str(err) returns message."""
        err = AppError(code="test_error", message="Something went wrong")
        assert str(err) == "Something went wrong"
