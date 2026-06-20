# PRD 06 Markdown Fidelity Implementation Plan

> **For agentic workers:** REQUIRED SUB-SKILL: Use superpowers:subagent-driven-development (recommended) or superpowers:executing-plans to implement this plan task-by-task. Steps use checkbox (`- [ ]`) syntax for tracking.

**Goal:** Preserve Markdown structure while translating natural language text.

**Architecture:** A backend Markdown fidelity service protects non-translatable spans with placeholders, sends safe text to the translation provider, restores placeholders, and performs lightweight structure checks.

**Tech Stack:** Python, pytest, Markdown-aware regular expressions for first version, OpenAI provider prompt constraints.

## Global Constraints

- Protect fenced code blocks, inline code, URLs, image URLs, HTML comments, frontmatter keys, table structure, badge URLs, and relative links.
- Translate headings, paragraphs, list text, link labels, image alt text, and table cell natural language.
- Provider returns only Markdown.
- PRD source: `docs/prd/github-translator/06-markdown-fidelity.md`.

---

## Task 1: Placeholder Protection Service

**Repo:** `global-backend`

**Files:**
- Create: `app/services/markdown_fidelity.py`
- Test: `tests/services/test_markdown_fidelity.py`

**Steps:**
- [ ] Write failing tests proving code blocks, inline code, URLs, and image URLs are removed from translatable text.
- [ ] Implement `ProtectedMarkdown(text, placeholders)`.
- [ ] Implement `protect_markdown(source)`.
- [ ] Implement `restore_markdown(translated, placeholders)`.
- [ ] Run: `pytest tests/services/test_markdown_fidelity.py -v`; expect pass.
- [ ] Commit: `feat: 添加 Markdown 占位符保护`

**Acceptance:**
- Protected spans round-trip exactly after restore.

## Task 2: Frontmatter And Table Coverage

**Repo:** `global-backend`

**Files:**
- Modify: `app/services/markdown_fidelity.py`
- Test: `tests/services/test_markdown_fidelity_frontmatter_tables.py`

**Steps:**
- [ ] Write failing test for YAML frontmatter preserving keys.
- [ ] Write failing test for Markdown table separator row preservation.
- [ ] Extend protection rules for frontmatter and table separators.
- [ ] Run: `pytest tests/services/test_markdown_fidelity_frontmatter_tables.py -v`; expect pass.
- [ ] Commit: `feat: 保护 frontmatter 和表格结构`

**Acceptance:**
- Frontmatter keys and table separator rows are not translated or corrupted.

## Task 3: OpenAI Prompt Integration

**Repo:** `global-backend`

**Files:**
- Modify: `app/services/translation_provider.py`
- Test: `tests/services/test_openai_translation_provider.py`

**Steps:**
- [ ] Write failing test that provider prompt includes “Preserve Markdown structure”, “Do not modify URLs”, and “Return only Markdown”.
- [ ] Implement `OpenAITranslationProvider`.
- [ ] Ensure provider calls `protect_markdown` before model call and `restore_markdown` after model call.
- [ ] Mock OpenAI client in tests.
- [ ] Run: `pytest tests/services/test_openai_translation_provider.py -v`; expect pass.
- [ ] Commit: `feat: 集成 OpenAI Markdown 翻译 Provider`

**Acceptance:**
- Provider prompts enforce Markdown fidelity constraints.

## Task 4: Fidelity Regression Fixtures

**Repo:** `global-backend`

**Files:**
- Create: `tests/fixtures/markdown/complex.md`
- Create: `tests/services/test_markdown_fidelity_regression.py`

**Steps:**
- [ ] Add fixture containing headings, code block, inline code, links, image, table, frontmatter, and blockquote.
- [ ] Write regression test that placeholder restore returns original protected spans.
- [ ] Run: `pytest tests/services/test_markdown_fidelity_regression.py -v`; expect pass.
- [ ] Commit: `test: 添加 Markdown 保真回归用例`

**Acceptance:**
- Future provider changes cannot silently break common Markdown structures.

## Verification

```bash
pytest tests/services/test_markdown_fidelity*.py tests/services/test_openai_translation_provider.py -v
```
