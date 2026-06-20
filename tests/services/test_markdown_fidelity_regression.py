"""Regression tests for Markdown fidelity protection.

Uses complex fixture to verify all protected structures survive round-trip.
Source: PRD 06, OpenSpec REQ-3.
"""

import pathlib

import pytest

from app.services.markdown_fidelity import protect_markdown, restore_markdown

_FIXTURE_DIR = pathlib.Path(__file__).parent.parent / "fixtures" / "markdown"


class TestComplexFixtureRegression:
    """Regression test using complex Markdown fixture."""

    @pytest.fixture
    def complex_source(self) -> str:
        return (_FIXTURE_DIR / "complex.md").read_text()

    def test_roundtrip_preserves_structure(self, complex_source: str):
        """All protected spans must survive protect -> restore exactly."""
        pm = protect_markdown(complex_source)
        restored = restore_markdown(pm.text, pm.placeholders)
        assert restored == complex_source

    def test_code_blocks_protected(self, complex_source: str):
        """Fenced code blocks should not appear in translatable text."""
        pm = protect_markdown(complex_source)
        assert 'def greet(name: str)' not in pm.text
        assert 'const add = (a, b)' not in pm.text

    def test_inline_code_protected(self, complex_source: str):
        """Inline code should not appear in translatable text."""
        pm = protect_markdown(complex_source)
        assert '`print("hello")`' not in pm.text
        assert '`len(data)`' not in pm.text

    def test_urls_protected(self, complex_source: str):
        """URLs should not appear in translatable text."""
        pm = protect_markdown(complex_source)
        assert 'https://docs.python.org/3/' not in pm.text
        assert 'https://example.com' not in pm.text
        assert 'https://img.shields.io' not in pm.text

    def test_relative_links_protected(self, complex_source: str):
        """Relative links should not appear in translatable text."""
        pm = protect_markdown(complex_source)
        assert './docs/guide.md' not in pm.text
        assert '../README.md' not in pm.text
        assert './assets/logo.png' not in pm.text
        assert './pic.png' not in pm.text

    def test_html_comments_protected(self, complex_source: str):
        """HTML comments should not appear in translatable text."""
        pm = protect_markdown(complex_source)
        assert 'This is a single-line comment' not in pm.text
        assert 'multi-line comment' not in pm.text

    def test_frontmatter_preserved(self, complex_source: str):
        """Frontmatter structure should survive round-trip."""
        pm = protect_markdown(complex_source)
        restored = restore_markdown(pm.text, pm.placeholders)
        assert restored.startswith("---\n")
        assert "title: Complex Markdown Test" in restored

    def test_table_separator_preserved(self, complex_source: str):
        """Table separator rows should survive round-trip."""
        pm = protect_markdown(complex_source)
        restored = restore_markdown(pm.text, pm.placeholders)
        assert "|---------|--------|----------|" in restored

    def test_link_labels_translatable(self, complex_source: str):
        """Link labels should remain in translatable text."""
        pm = protect_markdown(complex_source)
        # Labels like "Python Docs" should still be present
        assert "Python Docs" in pm.text or "Python" in pm.text

    def test_image_alt_translatable(self, complex_source: str):
        """Image alt text should remain in translatable text."""
        pm = protect_markdown(complex_source)
        # Alt text like "Build Status" should still be present
        assert "Build Status" in pm.text or "Status" in pm.text
