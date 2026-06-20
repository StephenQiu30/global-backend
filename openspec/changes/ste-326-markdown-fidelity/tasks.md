# Tasks: Markdown 保真翻译保护层

## Task 1: Placeholder Protection Service

**Files:**
- Create: `app/services/markdown_fidelity.py`
- Create: `tests/services/test_markdown_fidelity.py`

**Steps:**
- [ ] Write failing tests proving code blocks, inline code, URLs, and image URLs are removed from translatable text
- [ ] Implement `ProtectedMarkdown` dataclass
- [ ] Implement `protect_markdown(source)` with core regex patterns
- [ ] Implement `restore_markdown(translated, placeholders)`
- [ ] Verify tests pass

**Acceptance:**
- Protected spans round-trip exactly after restore

## Task 2: Frontmatter And Table Coverage

**Files:**
- Modify: `app/services/markdown_fidelity.py`
- Create: `tests/services/test_markdown_fidelity_frontmatter_tables.py`

**Steps:**
- [ ] Write failing test for YAML frontmatter preserving keys
- [ ] Write failing test for Markdown table separator row preservation
- [ ] Extend protection rules for frontmatter and table separators
- [ ] Verify tests pass

**Acceptance:**
- Frontmatter keys and table separator rows are not translated or corrupted

## Task 3: OpenAI Prompt Integration

**Files:**
- Create: `app/services/translation_provider.py`
- Create: `tests/services/test_openai_translation_provider.py`

**Steps:**
- [ ] Write failing test that provider prompt includes required constraints
- [ ] Implement `OpenAITranslationProvider` with protect/restore integration
- [ ] Mock OpenAI client in tests
- [ ] Verify tests pass

**Acceptance:**
- Provider prompts enforce Markdown fidelity constraints

## Task 4: Fidelity Regression Fixtures

**Files:**
- Create: `tests/fixtures/markdown/complex.md`
- Create: `tests/services/test_markdown_fidelity_regression.py`

**Steps:**
- [ ] Add fixture containing headings, code block, inline code, links, image, table, frontmatter, and blockquote
- [ ] Write regression test that placeholder restore returns original protected spans
- [ ] Verify tests pass

**Acceptance:**
- Future provider changes cannot silently break common Markdown structures

## Verification

```bash
pytest tests/services/test_markdown_fidelity*.py tests/services/test_openai_translation_provider.py -v
```
