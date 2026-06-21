# Tasks: Markdown File Discovery

## Task 1: Backend Markdown File Domain

**Files:**
- Create: `app/domain/markdown_files.py`
- Create: `tests/domain/test_markdown_files.py`

**Steps:**
- [x] Write failing tests for extension support
- [x] Write failing tests for translated variant detection
- [x] Write failing tests for unsafe path rejection
- [x] Write failing tests for target preview
- [x] Implement `is_supported_markdown_path`
- [x] Implement `is_translated_variant`
- [x] Implement `is_safe_path`
- [x] Implement `target_translation_path`
- [x] Implement `validate_selection`
- [x] Run: `pytest tests/domain/test_markdown_files.py -v`

**Acceptance:**
- Domain rules work without GitHub dependencies
- All tests pass

## Task 2: Backend GitHub Tree Discovery

**Files:**
- Create: `app/services/markdown_discovery.py`
- Create: `tests/services/test_markdown_discovery.py`

**Steps:**
- [x] Write failing test with fake GitHub tree containing:
  - `README.md`
  - `README.zh-CN.md`
  - `docs/guide.md`
  - `src/index.ts`
  - `node_modules/pkg/README.md`
  - `dist/README.md`
  - `.next/server/page.md`
- [x] Implement `get_repository_tree` service
- [x] Implement discovery service with filtering
- [x] Implement sorting (README first, then alphabetical)
- [x] Implement size limit marking with `disabled_reason`
- [x] Run: `pytest tests/services/test_markdown_discovery.py -v`

**Acceptance:**
- Discovery returns only eligible Markdown files
- README is highlighted as default
- Oversized files have `disabled_reason`

## Task 3: Backend Markdown Files API

**Files:**
- Modify: `app/api/repositories.py`
- Create: `tests/api/test_markdown_files_api.py`

**Steps:**
- [x] Write failing test for `GET /api/repositories/{owner}/{repo}/markdown-files`
- [x] Require `installation_id` from request context
- [x] Accept optional `language` query parameter (default: `zh-CN`)
- [x] Verify repository authorization before scanning
- [x] Return `repository_not_installed` for unauthorized repo
- [x] Run: `pytest tests/api/test_markdown_files_api.py -v`

**Acceptance:**
- API only works for authorized repositories
- Language parameter affects target path previews

## Task 4: Integration and Validation

**Steps:**
- [x] Run full test suite: `pytest tests/domain/test_markdown_files.py tests/services/test_markdown_discovery.py tests/api/test_markdown_files_api.py -v`
- [x] Verify all acceptance criteria met
- [x] Create feature branch
- [x] Commit with test-first ordering
- [x] Create PR with test-first evidence

## Verification Command

```bash
pytest tests/domain/test_markdown_files.py tests/services/test_markdown_discovery.py tests/api/test_markdown_files_api.py -v
```
