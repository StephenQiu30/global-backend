"""Tests for Markdown fidelity frontmatter and table protection.

Covers: YAML frontmatter keys, Markdown table separator rows.
Source: PRD 06, OpenSpec REQ-1.
"""

import pytest

from app.services.markdown_fidelity import (
    protect_markdown,
    restore_markdown,
)


class TestFrontmatterProtection:
    """Test that YAML frontmatter keys are protected."""

    def test_frontmatter_detected(self):
        source = "---\ntitle: Hello\nlang: en\n---\n\nContent here."
        pm = protect_markdown(source)
        # Frontmatter structure should be preserved
        assert "---" in pm.text

    def test_frontmatter_keys_preserved(self):
        """Frontmatter keys (title, lang) should not be translated."""
        source = "---\ntitle: My Document\nlang: en\n---\n\nBody text."
        pm = protect_markdown(source)
        restored = restore_markdown(pm.text, pm.placeholders)
        assert restored == source

    def test_frontmatter_with_complex_values(self):
        source = "---\ntitle: \"Quoted: value\"\ntags: [a, b, c]\n---\n\nContent."
        pm = protect_markdown(source)
        restored = restore_markdown(pm.text, pm.placeholders)
        assert restored == source

    def test_no_frontmatter(self):
        source = "# Just a heading\n\nNo frontmatter here."
        pm = protect_markdown(source)
        restored = restore_markdown(pm.text, pm.placeholders)
        assert restored == source


class TestTableSeparatorProtection:
    """Test that Markdown table separator rows are protected."""

    def test_table_separator_preserved(self):
        source = "| Name | Value |\n|------|-------|\n| foo  | bar   |"
        pm = protect_markdown(source)
        restored = restore_markdown(pm.text, pm.placeholders)
        assert restored == source

    def test_table_with_alignment(self):
        source = "| Left | Center | Right |\n|:-----|:------:|------:|\n| a    | b      | c     |"
        pm = protect_markdown(source)
        restored = restore_markdown(pm.text, pm.placeholders)
        assert restored == source

    def test_separator_not_translated(self):
        """Separator row should be entirely in placeholders."""
        source = "| A | B |\n|---|---|\n| 1 | 2 |"
        pm = protect_markdown(source)
        # The separator row content should not appear in translatable text
        assert "|---|---|" not in pm.text


class TestCombinedProtection:
    """Test frontmatter + table + other structures together."""

    def test_full_document_roundtrip(self):
        source = """---
title: Guide
lang: en
---

# Introduction

Some `code` and [link](https://example.com).

| Feature | Status |
|---------|--------|
| Alpha   | done   |
| Beta    | wip    |

```python
print("hello")
```

<!-- hidden -->
"""
        pm = protect_markdown(source)
        restored = restore_markdown(pm.text, pm.placeholders)
        assert restored == source
