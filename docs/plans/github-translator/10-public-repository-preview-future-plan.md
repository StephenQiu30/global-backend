# PRD 10 Public Repository Preview Future Implementation Plan

> **For agentic workers:** REQUIRED SUB-SKILL: Use superpowers:subagent-driven-development (recommended) or superpowers:executing-plans to implement this plan task-by-task. Steps use checkbox (`- [ ]`) syntax for tracking.

**Goal:** Add second-phase read-only translation preview for public GitHub repositories.

**Architecture:** Public preview is separate from GitHub App PR submission. It can read public Markdown and generate previews, but any write or PR creation must redirect users to GitHub App installation or a future OAuth/fork flow.

**Tech Stack:** FastAPI public read service, Next.js preview page, existing Markdown fidelity and translation provider.

## Global Constraints

- This is second-phase work, not part of first-version delivery.
- Public preview must not write to GitHub.
- Public preview can read only public Markdown files.
- PR submission still requires GitHub App installation or future fork/OAuth flow.
- PRD source: `docs/prd/github-translator/10-public-repository-preview-future.md`.

---

## Task 1: Backend Public Repository Read Client

**Repo:** `global-backend`

**Files:**
- Create: `app/services/public_repository.py`
- Test: `tests/services/test_public_repository.py`

**Steps:**
- [ ] Write failing test for listing public `README.md` through GitHub tree API.
- [ ] Implement unauthenticated public repository read client.
- [ ] Reuse Markdown file filters from PRD 03.
- [ ] Return rate-limit friendly errors.
- [ ] Run: `pytest tests/services/test_public_repository.py -v`; expect pass.
- [ ] Commit: `feat: 添加公开仓库只读客户端`

**Acceptance:**
- Backend can list public Markdown files without installation write permissions.

## Task 2: Backend Public Preview API

**Repo:** `global-backend`

**Files:**
- Create: `app/api/public_preview.py`
- Modify: `app/main.py`
- Test: `tests/api/test_public_preview.py`

**Steps:**
- [ ] Write failing test for `POST /api/public-preview`.
- [ ] Accept repository, selected files, and language.
- [ ] Read public Markdown.
- [ ] Translate and return preview content plus target path.
- [ ] Assert response contains no PR URL and performs no GitHub write call.
- [ ] Run: `pytest tests/api/test_public_preview.py -v`; expect pass.
- [ ] Commit: `feat: 添加公开仓库翻译预览接口`

**Acceptance:**
- Public preview returns translated Markdown without writing to GitHub.

## Task 3: Frontend Preview Page

**Repo:** `global-frontend`

**Files:**
- Create: `src/app/preview/page.tsx`
- Create: `src/components/PublicRepositoryPreview.tsx`
- Test: `src/app/preview/page.test.tsx`

**Steps:**
- [ ] Write failing test for heading `公开仓库翻译预览`.
- [ ] Add repository input, language selector, Markdown file selector, and preview action.
- [ ] Display read-only warning: `预览不会写入任何 GitHub 仓库。`
- [ ] Run: `npm test -- src/app/preview/page.test.tsx`; expect pass.
- [ ] Commit: `feat: 添加公开仓库翻译预览页面`

**Acceptance:**
- Users can start a preview without installing the GitHub App.

## Task 4: Frontend Preview Result And Install CTA

**Repo:** `global-frontend`

**Files:**
- Create: `src/components/PreviewResult.tsx`
- Test: `src/components/PreviewResult.test.tsx`

**Steps:**
- [ ] Write failing test for translated Markdown preview.
- [ ] Write failing test for CTA `安装 GitHub App 后提交 PR`.
- [ ] Implement preview display and download action.
- [ ] Route PR submission CTA to GitHub App install.
- [ ] Run: `npm test -- src/components/PreviewResult.test.tsx`; expect pass.
- [ ] Commit: `feat: 添加公开仓库预览结果`

**Acceptance:**
- Preview makes clear that submission requires authorization.

## Verification

```bash
pytest tests/services/test_public_repository.py tests/api/test_public_preview.py -v
npm test -- src/app/preview/page.test.tsx src/components/PreviewResult.test.tsx
```
