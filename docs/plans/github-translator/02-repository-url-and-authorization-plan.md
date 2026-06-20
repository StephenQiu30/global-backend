# PRD 02 Repository URL And Authorization Implementation Plan

> **For agentic workers:** REQUIRED SUB-SKILL: Use superpowers:subagent-driven-development (recommended) or superpowers:executing-plans to implement this plan task-by-task. Steps use checkbox (`- [ ]`) syntax for tracking.

**Goal:** Parse user-provided GitHub repository addresses and verify the repository is authorized for the selected GitHub App installation.

**Architecture:** Repository parsing is pure logic duplicated in frontend for immediate UX and enforced in backend for security. Backend authorization checks the installation repository list before any scan or translation task.

**Tech Stack:** TypeScript pure helpers, Python Pydantic domain models, FastAPI.

## Global Constraints

- Supported inputs: `https://github.com/owner/repo`, `github.com/owner/repo`, and `owner/repo`.
- Unsupported inputs: Git SSH URLs, subpath URLs, Gist, non-GitHub providers.
- Unauthorized repositories cannot enter the translation flow.
- PRD source: `docs/prd/github-translator/02-repository-url-and-authorization.md`.

---

## Task 1: Backend Repository Parser

**Repo:** `global-backend`

**Files:**
- Create: `app/domain/repository.py`
- Test: `tests/domain/test_repository.py`

**Steps:**
- [ ] Write failing tests for accepted URL forms and rejected non-GitHub URLs.
- [ ] Implement `RepositoryRef(owner: str, repo: str, full_name: str)`.
- [ ] Implement `parse_repository_input(value: str) -> RepositoryRef`.
- [ ] Reject empty input, Git SSH, subpaths, and non-GitHub URLs.
- [ ] Run: `pytest tests/domain/test_repository.py -v`; expect pass.
- [ ] Commit: `feat: 添加后端仓库地址解析`

**Acceptance:**
- Backend normalizes valid input to owner/repo and rejects invalid input.

## Task 2: Backend Authorization Resolver API

**Repo:** `global-backend`

**Files:**
- Create: `app/api/repositories.py`
- Modify: `app/main.py`
- Test: `tests/api/test_repository_resolve.py`

**Steps:**
- [ ] Write failing test for `POST /api/repositories/resolve`.
- [ ] Mock authorized repositories from GitHub App service.
- [ ] Return repository metadata for authorized repo.
- [ ] Return error code `repository_not_installed` for unauthorized repo.
- [ ] Run: `pytest tests/api/test_repository_resolve.py -v`; expect pass.
- [ ] Commit: `feat: 添加仓库授权校验接口`

**Acceptance:**
- UI can verify whether an input repository is authorized.

## Task 3: Frontend Repository Parser

**Repo:** `global-frontend`

**Files:**
- Create: `src/lib/repository.ts`
- Test: `src/lib/repository.test.ts`

**Steps:**
- [ ] Write failing tests matching backend accepted and rejected inputs.
- [ ] Implement `parseRepositoryInput(input)`.
- [ ] Return `{ owner, repo, fullName }`.
- [ ] Throw user-readable errors for unsupported input.
- [ ] Run: `npm test -- src/lib/repository.test.ts`; expect pass.
- [ ] Commit: `feat: 添加前端仓库地址解析`

**Acceptance:**
- Frontend catches obvious invalid input before calling backend.

## Task 4: Frontend Repository Selector

**Repo:** `global-frontend`

**Files:**
- Create: `src/components/RepositorySelector.tsx`
- Test: `src/components/RepositorySelector.test.tsx`

**Steps:**
- [ ] Write failing test for entering `owner/repo` and clicking `校验仓库`.
- [ ] Implement text input, authorized repository dropdown, validation state, and error state.
- [ ] Connect selector to backend `POST /api/repositories/resolve`.
- [ ] Display repository full name, default branch, visibility, and authorization status.
- [ ] Run: `npm test -- src/components/RepositorySelector.test.tsx`; expect pass.
- [ ] Commit: `feat: 添加仓库选择和授权校验界面`

**Acceptance:**
- User can input or choose an authorized repository before Markdown scanning.

## Verification

Backend:

```bash
pytest tests/domain/test_repository.py tests/api/test_repository_resolve.py -v
```

Frontend:

```bash
npm test -- src/lib/repository.test.ts src/components/RepositorySelector.test.tsx
```
