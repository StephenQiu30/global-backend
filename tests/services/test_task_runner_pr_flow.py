"""Tests for task runner PR flow: call order and failure atomicity."""

import pytest
from unittest.mock import ANY, AsyncMock, MagicMock, call

from app.domain.task import Task, TaskStatus
from app.services.task_runner import TaskRunner


def _make_task(task_id="task-001", files=None, language="zh-CN"):
    """Create a Task with default values."""
    return Task(
        task_id=task_id,
        installation_id="1",
        repository="owner/repo",
        base_branch="main",
        files=files or ["README.md"],
        language=language,
    )


def _make_runner(github_client=None, translation_provider=None, github_write_client=None):
    """Create a TaskRunner with mock dependencies."""
    runner = TaskRunner(
        github_client=github_client or MagicMock(),
        translation_provider=translation_provider or MagicMock(),
        github_write_client=github_write_client or MagicMock(),
    )
    return runner


@pytest.mark.asyncio
async def test_call_order_branch_then_files_then_pr():
    """create_branch is called before put_file, which is called before create_pull_request."""
    github = MagicMock()
    github.get_file_content = AsyncMock(return_value="# Hello")
    github.create_branch.return_value = "translate/zh-CN/task-001"
    github.put_file.return_value = None
    github.create_pull_request.return_value = {"number": 1, "url": "https://github.com/owner/repo/pull/1"}

    provider = AsyncMock()
    provider.translate_markdown.return_value = "# 你好"

    runner = _make_runner(github_client=github, translation_provider=provider, github_write_client=github)

    task = _make_task()
    await runner.run(task)

    # create_branch must be called before put_file
    # put_file must be called before create_pull_request
    assert github.create_branch.call_count == 1
    assert github.put_file.call_count >= 1
    assert github.create_pull_request.call_count == 1

    # Verify ordering via call sequence
    github.assert_has_calls([
        call.create_branch("1", "owner/repo", "main", "translate/zh-CN/task-001"),
        call.put_file("1", "owner/repo", "translate/zh-CN/task-001", "README.zh-CN.md", "# 你好", ANY),
        call.create_pull_request("1", "owner/repo", title=ANY, body=ANY, head="translate/zh-CN/task-001", base="main"),
    ], any_order=False)


@pytest.mark.asyncio
async def test_multi_files_same_branch_and_pr():
    """Multiple translated files go into the same branch and PR."""
    github = MagicMock()
    github.get_file_content = AsyncMock(return_value="# Hello")
    github.create_branch.return_value = "translate/zh-CN/task-001"
    github.put_file.return_value = None
    github.create_pull_request.return_value = {"number": 1, "url": "https://github.com/owner/repo/pull/1"}

    provider = AsyncMock()
    provider.translate_markdown.return_value = "# translated"

    runner = _make_runner(github_client=github, translation_provider=provider, github_write_client=github)

    task = _make_task(files=["README.md", "docs/guide.md"])
    await runner.run(task)

    # Only one branch created
    assert github.create_branch.call_count == 1
    # Two files written
    assert github.put_file.call_count == 2
    # Only one PR created
    assert github.create_pull_request.call_count == 1


@pytest.mark.asyncio
async def test_translation_failure_creates_no_branch_no_pr():
    """If translation fails, no branch, file write, or PR is created."""
    github = MagicMock()
    github.get_file_content = AsyncMock(return_value="# Hello")
    provider = AsyncMock()
    provider.translate_markdown.side_effect = RuntimeError("translation failed")

    runner = _make_runner(github_client=github, translation_provider=provider, github_write_client=github)

    task = _make_task()
    result = await runner.run(task)

    assert github.create_branch.call_count == 0
    assert github.put_file.call_count == 0
    assert github.create_pull_request.call_count == 0
    assert result.status == TaskStatus.FAILED


@pytest.mark.asyncio
async def test_pr_body_uses_build_translation_pr_body():
    """PR body must include file mappings, provider name, and task ID (S4)."""
    github = MagicMock()
    github.get_file_content = AsyncMock(return_value="# Hello")
    github.create_branch.return_value = "translate/zh-CN/task-001"
    github.put_file.return_value = None
    github.create_pull_request.return_value = {"number": 1, "url": "https://github.com/owner/repo/pull/1"}

    provider = AsyncMock()
    provider.translate_markdown.return_value = "# translated"

    runner = _make_runner(github_client=github, translation_provider=provider, github_write_client=github)

    task = _make_task(files=["README.md", "docs/guide.md"])
    await runner.run(task)

    # PR body must contain file mappings and task info
    pr_call = github.create_pull_request.call_args
    body = pr_call.kwargs.get("body") or pr_call[0][3]
    assert "README.md" in body
    assert "README.zh-CN.md" in body
    assert "task-001" in body


@pytest.mark.asyncio
async def test_github_failure_in_phase2_returns_failed():
    """If a GitHub API call fails in Phase 2, task returns failed status (S6)."""
    github = MagicMock()
    github.get_file_content = AsyncMock(return_value="# Hello")
    github.create_branch.side_effect = RuntimeError("permission denied")

    provider = AsyncMock()
    provider.translate_markdown.return_value = "# translated"

    runner = _make_runner(github_client=github, translation_provider=provider, github_write_client=github)

    task = _make_task()
    result = await runner.run(task)

    assert result.status == TaskStatus.FAILED
    assert result.error_code is not None
