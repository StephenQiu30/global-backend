# PRD 09 Security And Permissions Implementation Plan

> **For agentic workers:** REQUIRED SUB-SKILL: Use superpowers:subagent-driven-development (recommended) or superpowers:executing-plans to implement this plan task-by-task. Steps use checkbox (`- [ ]`) syntax for tracking.

**Goal:** Enforce authorization, path safety, token secrecy, size limits, and abuse controls across the translation workflow.

**Architecture:** Security is enforced in backend domain validators and service boundaries, then reflected in frontend messaging. Frontend improves UX but never replaces backend enforcement.

**Tech Stack:** FastAPI, Pydantic validators, pytest regression tests, frontend warning UI.

## Global Constraints

- Unauthorized repositories cannot be translated.
- Non-Markdown files cannot be submitted.
- Path traversal is rejected.
- Installation tokens never reach frontend responses.
- All writes happen on translation branches.
- PRD source: `docs/prd/github-translator/09-security-and-permissions.md`.

---

## Task 1: Backend Path And File Safety Tests

**Repo:** `global-backend`

**Files:**
- Modify: `app/domain/markdown_files.py`
- Test: `tests/domain/test_security_paths.py`

**Steps:**
- [ ] Write failing tests for `../README.md`, `/README.md`, `README.txt`, and `README.zh-CN.md` source selection.
- [ ] Implement strict path rejection.
- [ ] Ensure translated variants are excluded from default source selections.
- [ ] Run: `pytest tests/domain/test_security_paths.py -v`; expect pass.
- [ ] Commit: `test: 添加路径安全回归测试`

**Acceptance:**
- Unsafe paths and unsupported files cannot enter task execution.

## Task 2: Backend Authorization Enforcement

**Repo:** `global-backend`

**Files:**
- Modify: `app/api/repositories.py`
- Modify: `app/api/tasks.py`
- Test: `tests/api/test_authorization_enforcement.py`

**Steps:**
- [ ] Write failing test that unauthorized repository cannot scan Markdown.
- [ ] Write failing test that unauthorized repository cannot create translation task.
- [ ] Add shared authorization check service.
- [ ] Return `repository_not_installed` for unauthorized repo.
- [ ] Run: `pytest tests/api/test_authorization_enforcement.py -v`; expect pass.
- [ ] Commit: `feat: 强制仓库授权边界`

**Acceptance:**
- Every read/write workflow verifies installation authorization.

## Task 3: Secret Leakage Regression Tests

**Repo:** `global-backend`

**Files:**
- Test: `tests/api/test_secret_leakage.py`

**Steps:**
- [ ] Write tests asserting responses do not contain `token`, `private_key`, `OPENAI_API_KEY`, or raw stack traces.
- [ ] Add response sanitation where needed.
- [ ] Run: `pytest tests/api/test_secret_leakage.py -v`; expect pass.
- [ ] Commit: `test: 添加密钥泄露回归测试`

**Acceptance:**
- API responses never expose sensitive credentials.

## Task 4: Task Size And Frequency Limits

**Repo:** `global-backend`

**Files:**
- Modify: `app/domain/markdown_files.py`
- Modify: `app/services/task_runner.py`
- Test: `tests/services/test_task_limits.py`

**Steps:**
- [ ] Write failing test for more than 10 files.
- [ ] Write failing test for total source size over 200KB.
- [ ] Enforce limits before calling translation provider.
- [ ] Return retryable false error for limit violations.
- [ ] Run: `pytest tests/services/test_task_limits.py -v`; expect pass.
- [ ] Commit: `feat: 添加翻译任务大小限制`

**Acceptance:**
- Large tasks are rejected before model calls.

## Task 5: Frontend Security Messaging

**Repo:** `global-frontend`

**Files:**
- Modify: `src/app/translate/page.tsx`
- Create: `src/components/SecurityNotice.tsx`
- Test: `src/components/SecurityNotice.test.tsx`

**Steps:**
- [ ] Write failing test for copy: `不会覆盖原始文件` and `所有变更通过 Pull Request 审核`.
- [ ] Implement concise security notice.
- [ ] Show notice on translate page.
- [ ] Run: `npm test -- src/components/SecurityNotice.test.tsx`; expect pass.
- [ ] Commit: `feat: 添加翻译安全提示`

**Acceptance:**
- Users understand PR-only and no-overwrite behavior before submitting.

## Verification

```bash
pytest tests/domain/test_security_paths.py tests/api/test_authorization_enforcement.py tests/api/test_secret_leakage.py tests/services/test_task_limits.py -v
npm test -- src/components/SecurityNotice.test.tsx
```
