"""Tests for path and file safety validation.

PRD 09: Security, Permissions, and Abuse Prevention
Spec: openspec/changes/ste-329-security-permissions/specs/security-paths/spec.md
"""

import pytest

from app.domain.markdown_files import validate_markdown_path


class TestValidateMarkdownPath:
    """Tests for validate_markdown_path function."""

    def test_rejects_path_traversal_dotdot(self):
        """Reject path containing .. (path traversal)."""
        with pytest.raises(ValueError, match="path_traversal"):
            validate_markdown_path("../README.md")

    def test_rejects_path_traversal_in_subdirectory(self):
        """Reject path with .. in subdirectory."""
        with pytest.raises(ValueError, match="path_traversal"):
            validate_markdown_path("docs/../README.md")

    def test_rejects_absolute_path(self):
        """Reject absolute path starting with /."""
        with pytest.raises(ValueError, match="absolute_path"):
            validate_markdown_path("/README.md")

    def test_rejects_absolute_path_with_subdirectory(self):
        """Reject absolute path with subdirectory."""
        with pytest.raises(ValueError, match="absolute_path"):
            validate_markdown_path("/docs/README.md")

    def test_rejects_non_markdown_txt(self):
        """Reject .txt files."""
        with pytest.raises(ValueError, match="unsupported_file_type"):
            validate_markdown_path("README.txt")

    def test_rejects_non_markdown_py(self):
        """Reject .py files."""
        with pytest.raises(ValueError, match="unsupported_file_type"):
            validate_markdown_path("main.py")

    def test_rejects_non_markdown_json(self):
        """Reject .json files."""
        with pytest.raises(ValueError, match="unsupported_file_type"):
            validate_markdown_path("config.json")

    def test_rejects_translated_variant(self):
        """Reject translated variant files (e.g., README.zh-CN.md)."""
        with pytest.raises(ValueError, match="translated_variant"):
            validate_markdown_path("README.zh-CN.md")

    def test_rejects_translated_variant_complex(self):
        """Reject complex translated variant."""
        with pytest.raises(ValueError, match="translated_variant"):
            validate_markdown_path("docs/guide.zh-TW.md")

    def test_accepts_valid_markdown(self):
        """Accept valid relative Markdown path."""
        result = validate_markdown_path("README.md")
        assert result == "README.md"

    def test_accepts_valid_markdown_in_subdirectory(self):
        """Accept valid Markdown path in subdirectory."""
        result = validate_markdown_path("docs/README.md")
        assert result == "docs/README.md"

    def test_accepts_markdown_extension(self):
        """Accept .markdown extension."""
        result = validate_markdown_path("README.markdown")
        assert result == "README.markdown"

    def test_accepts_nested_markdown(self):
        """Accept deeply nested Markdown file."""
        result = validate_markdown_path("docs/guides/setup.md")
        assert result == "docs/guides/setup.md"

    def test_rejects_empty_path(self):
        """Reject empty path."""
        with pytest.raises(ValueError, match="empty_path"):
            validate_markdown_path("")

    def test_rejects_whitespace_only(self):
        """Reject whitespace-only path."""
        with pytest.raises(ValueError, match="empty_path"):
            validate_markdown_path("   ")
