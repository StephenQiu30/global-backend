# Tasks: Markdown File Discovery

## Task 1: Backend Markdown File Domain

**Files:**
- Create: `app/domain/markdown_files.py`
- Create: `tests/domain/test_markdown_files.py`

**Steps:**
- [ ] Write failing tests for extension support
- [ ] Write failing tests for translated variant detection
- [ ] Write failing tests for unsafe path rejection
- [ ] Write failing tests for target preview
- [ ] Implement `is_supported_markdown_path`
- [ ] Implement `is_translated_variant`
- [ ] Implement `is_safe_path`
- [ ] Implement `target_translation_path`
- [ ] Implement `validate_selection`
- [ ] Run: `pytest tests/domain/test_markdown_files.py -v`

**Acceptance:**
- Domain rules work without GitHub dependencies
- All tests pass

## Task 2: Backend GitHub Tree Discovery

**Files:**
- Create: `app/services/markdown_discovery.py`
- Create: `tests/services/test_markdown_discovery.py`

**Steps:**
- [ ] Write failing test with fake GitHub tree containing:
  - `README.md`
  - `README.zh-CN.md`
  - `docs/guide.md`
  - `src/index.ts`
  - `node_modules/pkg/README.md`
  - `dist/README.md`
  - `.next/server/page.md`
- [ ] Implement `get_repository_tree` service
- [ ] Implement discovery service with filtering
- [ ] Implement sorting (README first, then alphabetical)
- [ ] Implement size limit marking with `disabled_reason`
- [ ] Run: `pytest tests/services/test_markdown_discovery.py -v`

**Acceptance:**
- Discovery returns only eligible Markdown files
- README is highlighted as default
- Oversized files have `disabled_reason`

## Task 3: Backend Markdown Files API

**Files:**
- Modify: `app/api/repositories.py`
- Create: `tests/api/test_markdown_files_api.py`

**Steps:**
- [ ] Write failing test for `GET /api/repositories/{owner}/{repo}/markdown-files`
- [ ] Require `installation_id` from request context
- [ ] Accept optional `language` query parameter (default: `zh-CN`)
- [ ] Verify repository authorization before scanning
- [ ] Return `repository_not_installed` for unauthorized repo
- [ ] Run: `pytest tests/api/test_markdown_files_api.py -v`

**Acceptance:**
- API only works for authorized repositories
- Language parameter affects target path previews

## Task 4: Integration and Validation

**Steps:**
- [ ] Run full test suite: `pytest tests/domain/test_markdown_files.py tests/services/test_markdown_discovery.py tests/api/test_markdown_files_api.py -v`
- [ ] Verify all acceptance criteria met
- [ ] Create feature branch
- [ ] Commit with test-first ordering
- [ ] Create PR with test-first evidence

## Verification Command

```bash
pytest tests/domain/test_markdown_files.py tests/services/test_markdown_discovery.py tests/api/test_markdown_files_api.py -v
```
