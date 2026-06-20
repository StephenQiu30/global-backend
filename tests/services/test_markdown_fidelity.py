"""Tests for Markdown fidelity placeholder protection.

Covers: fenced code, inline code, URLs, image URLs, HTML comments.
Source: PRD 06, OpenSpec REQ-1, REQ-2, REQ-3.
"""

import pytest

from app.services.markdown_fidelity import (
    ProtectedMarkdown,
    protect_markdown,
    restore_markdown,
)


class TestProtectedMarkdown:
    """Test the ProtectedMarkdown data structure."""

    def test_creation(self):
        pm = ProtectedMarkdown(text="hello", placeholders={"p1": "world"})
        assert pm.text == "hello"
        assert pm.placeholders == {"p1": "world"}

    def test_empty_placeholders(self):
        pm = ProtectedMarkdown(text="no placeholders", placeholders={})
        assert pm.placeholders == {}


class TestFencedCodeBlockProtection:
    """Test that fenced code blocks are protected."""

    def test_backtick_fenced_code(self):
        source = "Before\n```python\nprint('hello')\n```\nAfter"
        pm = protect_markdown(source)
        assert "print('hello')" not in pm.text
        assert "```" not in pm.text
        assert len(pm.placeholders) >= 1

    def test_tilde_fenced_code(self):
        source = "Before\n~~~javascript\nconsole.log('hi');\n~~~\nAfter"
        pm = protect_markdown(source)
        assert "console.log" not in pm.text
        assert "~~~" not in pm.text

    def test_fenced_code_roundtrip(self):
        source = "Text\n```\nblock content\n```\nMore"
        pm = protect_markdown(source)
        restored = restore_markdown(pm.text, pm.placeholders)
        assert restored == source


class TestInlineCodeProtection:
    """Test that inline code is protected."""

    def test_inline_code(self):
        source = "Use `print()` function"
        pm = protect_markdown(source)
        assert "`print()`" not in pm.text
        assert "print()" not in pm.text

    def test_inline_code_roundtrip(self):
        source = "Call `my_func(arg)` here"
        pm = protect_markdown(source)
        restored = restore_markdown(pm.text, pm.placeholders)
        assert restored == source

    def test_multiple_inline_codes(self):
        source = "Use `foo()` and `bar()`"
        pm = protect_markdown(source)
        restored = restore_markdown(pm.text, pm.placeholders)
        assert restored == source


class TestLinkUrlProtection:
    """Test that Markdown link URLs are protected."""

    def test_link_url_protected(self):
        source = "Visit [Example](https://example.com) site"
        pm = protect_markdown(source)
        assert "https://example.com" not in pm.text

    def test_link_label_preserved(self):
        """Link labels should remain translatable."""
        source = "Visit [Example Site](https://example.com)"
        pm = protect_markdown(source)
        # Label text should still be present for translation
        assert "Example Site" in pm.text or "[" in pm.text

    def test_link_roundtrip(self):
        source = "See [docs](https://docs.example.com/guide) for info"
        pm = protect_markdown(source)
        restored = restore_markdown(pm.text, pm.placeholders)
        assert restored == source


class TestImageUrlProtection:
    """Test that Markdown image URLs are protected."""

    def test_image_url_protected(self):
        source = "![Logo](https://example.com/logo.png)"
        pm = protect_markdown(source)
        assert "https://example.com/logo.png" not in pm.text

    def test_image_roundtrip(self):
        source = "![Screenshot](./images/screen.png)"
        pm = protect_markdown(source)
        restored = restore_markdown(pm.text, pm.placeholders)
        assert restored == source


class TestHtmlCommentProtection:
    """Test that HTML comments are protected."""

    def test_html_comment_protected(self):
        source = "Before\n<!-- This is a comment -->\nAfter"
        pm = protect_markdown(source)
        assert "This is a comment" not in pm.text

    def test_multiline_html_comment(self):
        source = "Text\n<!--\nMulti\nline\n-->\nEnd"
        pm = protect_markdown(source)
        assert "Multi" not in pm.text

    def test_html_comment_roundtrip(self):
        source = "Hello\n<!-- hidden info -->\nWorld"
        pm = protect_markdown(source)
        restored = restore_markdown(pm.text, pm.placeholders)
        assert restored == source


class TestRoundTripFidelity:
    """Test that protect -> restore is identity for all protected spans."""

    def test_complex_document_roundtrip(self):
        source = """# Title

Some text with `inline code` here.

```python
def hello():
    print("world")
```

See [link](https://example.com) and ![img](./pic.png).

<!-- comment -->
"""
        pm = protect_markdown(source)
        restored = restore_markdown(pm.text, pm.placeholders)
        assert restored == source

    def test_no_placeholders_passthrough(self):
        source = "Just plain text\n\nNo special markup."
        pm = protect_markdown(source)
        assert pm.text == source
        assert pm.placeholders == {}
        restored = restore_markdown(pm.text, pm.placeholders)
        assert restored == source
