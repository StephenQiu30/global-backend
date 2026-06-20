# PRD 03 Markdown File Discovery Implementation Plan

> **For agentic workers:** REQUIRED SUB-SKILL: Use superpowers:subagent-driven-development (recommended) or superpowers:executing-plans to implement this plan task-by-task. Steps use checkbox (`- [ ]`) syntax for tracking.

**Goal:** Scan authorized repositories for Markdown files, default-select README, exclude generated translation files, and let users select multiple files within limits.

**Architecture:** Backend uses GitHub tree APIs to discover files and enforce file eligibility. Frontend renders the list, default selection, disabled reasons, and size/count summary.

**Tech Stack:** FastAPI, GitHub REST trees API, TypeScript React components.

## Global Constraints

- Supported extensions: `.md`, `.markdown`.
- Exclude generated language variants such as `README.zh-CN.md`.
- Exclude `.git`, `node_modules`, `dist`, `build`, `.next`, and other generated/dependency directories before evaluating file extensions.
- Default-select root `README.md`.
- Single task limits: max 10 files and max 200KB total source Markdown.
- PRD source: `docs/prd/github-translator/03-markdown-file-discovery.md`.

---

## Task 1: Backend Markdown File Domain

**Repo:** `global-backend`

**Files:**
- Create: `app/domain/markdown_files.py`
- Test: `tests/domain/test_markdown_files.py`

**Steps:**
- [ ] Write failing tests for extension support, translated variant detection, unsafe path rejection, and target preview.
- [ ] Implement `is_supported_markdown_path`.
- [ ] Implement `is_translated_variant`.
- [ ] Implement `target_translation_path`.
- [ ] Implement selection limit validation.
- [ ] Run: `pytest tests/domain/test_markdown_files.py -v`; expect pass.
- [ ] Commit: `feat: 添加 Markdown 文件规则`

**Acceptance:**
- Backend can classify Markdown files without GitHub dependencies.

## Task 2: Backend GitHub Tree Discovery

**Repo:** `global-backend`

**Files:**
- Create: `app/services/markdown_discovery.py`
- Modify: `app/services/github_app.py`
- Test: `tests/services/test_markdown_discovery.py`

**Steps:**
- [ ] Write failing test with fake GitHub tree containing README, translated README, docs file, source code file, `node_modules/pkg/README.md`, `.next/server/page.md`, and `dist/README.md`.
- [ ] Add `get_repository_tree(installation_id, full_name, branch)`.
- [ ] Implement discovery service that filters eligible Markdown files and rejects excluded directories before extension checks.
- [ ] Sort README first, then paths alphabetically.
- [ ] Return `path`, `size_bytes`, `is_default_readme`, `is_translated_variant`, `disabled_reason`, `target_path_preview`, and `target_exists`.
- [ ] Mark files over the configured size limit with `disabled_reason` instead of silently dropping them.
- [ ] Run: `pytest tests/services/test_markdown_discovery.py -v`; expect pass.
- [ ] Commit: `feat: 添加 Markdown 文件扫描服务`

**Acceptance:**
- Discovery returns only eligible Markdown files and highlights README.

## Task 3: Backend Markdown Files API

**Repo:** `global-backend`

**Files:**
- Modify: `app/api/repositories.py`
- Test: `tests/api/test_markdown_files_api.py`

**Steps:**
- [ ] Write failing test for `GET /api/repositories/{owner}/{repo}/markdown-files`.
- [ ] Require `installation_id`.
- [ ] Accept optional `language` query parameter and default it to `zh-CN` for target path previews.
- [ ] Verify repository is authorized before scanning.
- [ ] Return `repository_not_installed` for unauthorized repo.
- [ ] Run: `pytest tests/api/test_markdown_files_api.py -v`; expect pass.
- [ ] Commit: `feat: 添加 Markdown 文件列表接口`

**Acceptance:**
- Frontend can request Markdown files only for authorized repositories.

## Task 4: Frontend Markdown File Picker

**Repo:** `global-frontend`

**Files:**
- Create: `src/components/MarkdownFilePicker.tsx`
- Create: `src/lib/targetPath.ts`
- Test: `src/components/MarkdownFilePicker.test.tsx`
- Test: `src/lib/targetPath.test.ts`

**Steps:**
- [ ] Write failing tests for default README selection and target path preview.
- [ ] Implement target path preview helper.
- [ ] Implement file picker with checkbox list, disabled reason, file size, target path preview.
- [ ] Show selected count and total size.
- [ ] Prevent selecting more than 10 files in UI.
- [ ] Disable files with backend `disabled_reason` and show the exact reason inline.
- [ ] Show `target_exists` as an update warning rather than blocking selection.
- [ ] Run: `npm test -- src/components/MarkdownFilePicker.test.tsx src/lib/targetPath.test.ts`; expect pass.
- [ ] Commit: `feat: 添加 Markdown 文件选择界面`

**Acceptance:**
- User can see scan results, target paths, and selection limits.

## Verification

```bash
pytest tests/domain/test_markdown_files.py tests/services/test_markdown_discovery.py tests/api/test_markdown_files_api.py -v
npm test -- src/components/MarkdownFilePicker.test.tsx src/lib/targetPath.test.ts
```
