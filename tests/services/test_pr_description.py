"""Tests for PR description builder."""

from app.services.pr_description import build_translation_pr_body


def test_body_contains_language():
    """PR body includes target language."""
    body = build_translation_pr_body(
        language="zh-CN",
        mappings=[],
        provider_name="openai",
        task_id="task-001",
    )
    assert "zh-CN" in body


def test_body_contains_file_mappings():
    """PR body includes source-to-target file mappings."""
    mappings = [
        {"source": "README.md", "target": "README.zh-CN.md"},
        {"source": "docs/guide.md", "target": "docs/guide.zh-CN.md"},
    ]
    body = build_translation_pr_body(
        language="zh-CN",
        mappings=mappings,
        provider_name="openai",
        task_id="task-001",
    )
    assert "README.md" in body
    assert "README.zh-CN.md" in body
    assert "docs/guide.md" in body
    assert "docs/guide.zh-CN.md" in body


def test_body_contains_provider():
    """PR body includes translation provider name."""
    body = build_translation_pr_body(
        language="zh-CN",
        mappings=[],
        provider_name="openai",
        task_id="task-001",
    )
    assert "openai" in body


def test_body_contains_task_id():
    """PR body includes task ID."""
    body = build_translation_pr_body(
        language="zh-CN",
        mappings=[],
        provider_name="openai",
        task_id="task-001",
    )
    assert "task-001" in body


def test_body_contains_review_reminder():
    """PR body includes a human review reminder."""
    body = build_translation_pr_body(
        language="zh-CN",
        mappings=[],
        provider_name="openai",
        task_id="task-001",
    )
    lower = body.lower()
    assert "review" in lower or "审核" in body or "人工" in body


def test_body_contains_auto_translation_disclaimer():
    """PR body states it was auto-translated."""
    body = build_translation_pr_body(
        language="zh-CN",
        mappings=[],
        provider_name="openai",
        task_id="task-001",
    )
    lower = body.lower()
    assert "auto" in lower or "自动" in body or "翻译" in body


def test_body_is_valid_markdown():
    """PR body is valid Markdown with headings."""
    body = build_translation_pr_body(
        language="zh-CN",
        mappings=[{"source": "README.md", "target": "README.zh-CN.md"}],
        provider_name="openai",
        task_id="task-001",
    )
    assert body.startswith("#") or "\n# " in body or "\n## " in body
