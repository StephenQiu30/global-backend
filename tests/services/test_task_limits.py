"""Tests for task size and frequency limits.

PRD 09: Security, Permissions, and Abuse Prevention
Spec: openspec/changes/ste-329-security-permissions/specs/task-limits/spec.md
"""

import pytest

from app.services.task_runner import TaskLimitError, validate_task_limits


class TestValidateTaskLimits:
    """Tests for validate_task_limits function."""

    def test_rejects_more_than_10_files(self):
        """Reject task with more than 10 files."""
        files = [{"path": f"file{i}.md", "size": 100} for i in range(11)]
        with pytest.raises(TaskLimitError, match="task_too_many_files"):
            validate_task_limits(files)

    def test_accepts_10_files(self):
        """Accept task with exactly 10 files."""
        files = [{"path": f"file{i}.md", "size": 100} for i in range(10)]
        # Should not raise
        validate_task_limits(files)

    def test_rejects_total_size_over_200kb(self):
        """Reject task with total source size exceeding 200KB."""
        # 200KB = 204800 bytes
        files = [{"path": "large.md", "size": 204801}]
        with pytest.raises(TaskLimitError, match="task_too_large"):
            validate_task_limits(files)

    def test_accepts_total_size_exactly_200kb(self):
        """Accept task with total source size exactly 200KB."""
        files = [{"path": "exact.md", "size": 204800}]
        # Should not raise
        validate_task_limits(files)

    def test_accepts_small_task(self):
        """Accept small task within all limits."""
        files = [
            {"path": "README.md", "size": 1024},
            {"path": "docs/guide.md", "size": 2048},
        ]
        # Should not raise
        validate_task_limits(files)

    def test_rejects_empty_file_list(self):
        """Reject task with no files."""
        with pytest.raises(TaskLimitError, match="task_empty"):
            validate_task_limits([])

    def test_file_count_checked_before_size(self):
        """File count limit is checked before size limit."""
        # 11 files, each 1 byte - should fail on count, not size
        files = [{"path": f"file{i}.md", "size": 1} for i in range(11)]
        with pytest.raises(TaskLimitError, match="task_too_many_files"):
            validate_task_limits(files)


class TestTaskLimitError:
    """Tests for TaskLimitError class."""

    def test_error_has_code(self):
        """TaskLimitError has error code."""
        err = TaskLimitError("task_too_many_files", "Too many files")
        assert err.code == "task_too_many_files"

    def test_error_has_message(self):
        """TaskLimitError has human-readable message with code."""
        err = TaskLimitError("task_too_many_files", "Too many files")
        assert str(err) == "task_too_many_files: Too many files"

    def test_error_is_not_retryable(self):
        """TaskLimitError is not retryable by default."""
        err = TaskLimitError("task_too_many_files", "Too many files")
        assert err.retryable is False
