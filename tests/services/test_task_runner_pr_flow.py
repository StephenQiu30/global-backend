"""Tests for task runner PR flow: call order and failure atomicity."""

from unittest.mock import MagicMock, call

from app.services.task_runner import TaskRunner


def _make_runner(github_client=None, translation_provider=None):
    """Create a TaskRunner with mock dependencies."""
    runner = TaskRunner(
        github_client=github_client or MagicMock(),
        translation_provider=translation_provider or MagicMock(),
    )
    return runner


def test_call_order_branch_then_files_then_pr():
    """create_branch is called before put_file, which is called before create_pull_request."""
    github = MagicMock()
    github.create_branch.return_value = "translate/zh-CN/task-001"
    github.put_file.return_value = None
    github.create_pull_request.return_value = {"number": 1, "url": "https://github.com/owner/repo/pull/1"}

    provider = MagicMock()
    provider.translate_markdown.return_value = "# 你好"

    runner = _make_runner(github_client=github, translation_provider=provider)

    runner.run(
        installation_id=1,
        repository_full_name="owner/repo",
        base_branch="main",
        files=["README.md"],
        language="zh-CN",
        task_id="task-001",
    )

    # create_branch must be called before put_file
    # put_file must be called before create_pull_request
    assert github.create_branch.call_count == 1
    assert github.put_file.call_count >= 1
    assert github.create_pull_request.call_count == 1

    # Verify ordering via call sequence
    github.assert_has_calls([
        call.create_branch(1, "owner/repo", "main", "translate/zh-CN/task-001"),
        call.put_file(1, "owner/repo", "translate/zh-CN/task-001", "README.zh-CN.md", "# 你好", ...),
        call.create_pull_request(1, "owner/repo", ..., ..., "translate/zh-CN/task-001", "main"),
    ], any_order=False)


def test_multi_files_same_branch_and_pr():
    """Multiple translated files go into the same branch and PR."""
    github = MagicMock()
    github.create_branch.return_value = "translate/zh-CN/task-001"
    github.put_file.return_value = None
    github.create_pull_request.return_value = {"number": 1, "url": "https://github.com/owner/repo/pull/1"}

    provider = MagicMock()
    provider.translate_markdown.return_value = "# translated"

    runner = _make_runner(github_client=github, translation_provider=provider)

    runner.run(
        installation_id=1,
        repository_full_name="owner/repo",
        base_branch="main",
        files=["README.md", "docs/guide.md"],
        language="zh-CN",
        task_id="task-001",
    )

    # Only one branch created
    assert github.create_branch.call_count == 1
    # Two files written
    assert github.put_file.call_count == 2
    # Only one PR created
    assert github.create_pull_request.call_count == 1


def test_translation_failure_creates_no_branch_no_pr():
    """If translation fails, no branch, file write, or PR is created."""
    github = MagicMock()
    provider = MagicMock()
    provider.translate_markdown.side_effect = RuntimeError("translation failed")

    runner = _make_runner(github_client=github, translation_provider=provider)

    result = runner.run(
        installation_id=1,
        repository_full_name="owner/repo",
        base_branch="main",
        files=["README.md"],
        language="zh-CN",
        task_id="task-001",
    )

    assert github.create_branch.call_count == 0
    assert github.put_file.call_count == 0
    assert github.create_pull_request.call_count == 0
    assert result["status"] == "failed"
