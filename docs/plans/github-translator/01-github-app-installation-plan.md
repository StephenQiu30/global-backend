# PRD 01 GitHub App Installation Implementation Plan

> **For agentic workers:** REQUIRED SUB-SKILL: Use superpowers:subagent-driven-development (recommended) or superpowers:executing-plans to implement this plan task-by-task. Steps use checkbox (`- [ ]`) syntax for tracking.

**Goal:** Implement GitHub App installation entry, callback handling, installation verification, and authorized repository listing.

**Architecture:** Frontend owns install and callback UI. Backend owns installation verification and repository listing through GitHub App APIs. Installation tokens stay server-side.

**Tech Stack:** Next.js App Router, FastAPI, PyJWT, httpx, pytest, Vitest.

## Global Constraints

- GitHub App installation is the first-version permission boundary.
- The frontend must not receive GitHub private keys or installation tokens.
- Required permissions: Contents read/write, Pull requests read/write, Metadata read-only.
- Frontend installation entry must use a backend-provided install URL, not a hard-coded GitHub App URL, so callback URL, app slug, and future environment differences stay server-controlled.
- PRD source: `docs/prd/github-translator/01-github-app-installation.md`.

---

## Task 1: Backend Installation Configuration

**Repo:** `global-backend`

**Files:**
- Create: `app/core/config.py`
- Create: `app/main.py`
- Create: `pyproject.toml`
- Test: `tests/test_config.py`

**Steps:**
- [ ] Write a failing test that asserts settings expose `github_app_id`, `github_private_key`, and `github_webhook_secret`.
- [ ] Run: `pytest tests/test_config.py -v`; expect missing module failure.
- [ ] Add FastAPI dependencies and `Settings` using `pydantic-settings`.
- [ ] Add `.env.example` keys: `GITHUB_APP_ID`, `GITHUB_PRIVATE_KEY`, `GITHUB_WEBHOOK_SECRET`.
- [ ] Run: `pytest tests/test_config.py -v`; expect pass.
- [ ] Commit: `feat: 添加 GitHub App 后端配置`

**Acceptance:**
- Backend can load GitHub App configuration from environment without exposing values.

## Task 2: Backend Installation Verification API

**Repo:** `global-backend`

**Files:**
- Create: `app/services/github_app.py`
- Create: `app/api/installations.py`
- Modify: `app/main.py`
- Test: `tests/api/test_installations.py`

**Steps:**
- [ ] Write a failing API test for `POST /api/github/installations/verify`.
- [ ] Mock GitHub API and verify response includes `installation_id` and `account_login`.
- [ ] Implement GitHub App JWT creation and installation API request.
- [ ] Register installation router in `create_app()`.
- [ ] Run: `pytest tests/api/test_installations.py -v`; expect pass.
- [ ] Commit: `feat: 添加 GitHub App 安装校验接口`

**Acceptance:**
- Given a valid `installation_id`, backend returns installation account metadata.
- Invalid installation returns a structured error code.

## Task 3: Backend Authorized Repository Listing

**Repo:** `global-backend`

**Files:**
- Modify: `app/services/github_app.py`
- Modify: `app/api/installations.py`
- Test: `tests/api/test_installation_repositories.py`

**Steps:**
- [ ] Write a failing test for `GET /api/github/installations/{installation_id}/repositories`.
- [ ] Mock GitHub `/installation/repositories`.
- [ ] Implement repository normalization with `owner`, `repo`, `full_name`, `default_branch`, `private`.
- [ ] Run: `pytest tests/api/test_installation_repositories.py -v`; expect pass.
- [ ] Commit: `feat: 添加授权仓库列表接口`

**Acceptance:**
- Frontend can fetch authorized repositories after installation.

## Task 4: Backend GitHub App Install URL API

**Repo:** `global-backend`

**Files:**
- Modify: `app/core/config.py`
- Modify: `app/api/installations.py`
- Test: `tests/api/test_install_url.py`

**Steps:**
- [ ] Write a failing test for `GET /api/github/app/install-url`.
- [ ] Add `github_app_slug` and `frontend_install_callback_url` settings.
- [ ] Build the URL as `https://github.com/apps/{github_app_slug}/installations/new?state={signed_state}`.
- [ ] Include a signed, short-lived `state` value so callback requests can be correlated without exposing secrets.
- [ ] Return only `{ "install_url": "..." }`.
- [ ] Run: `pytest tests/api/test_install_url.py -v`; expect pass.
- [ ] Commit: `feat: 添加 GitHub App 安装链接接口`

**Acceptance:**
- Frontend can request an install URL from backend.
- The response does not include private key, installation token, or webhook secret.

## Task 5: Frontend Install Entry UI

**Repo:** `global-frontend`

**Files:**
- Create: `src/app/page.tsx`
- Create: `src/components/InstallCard.tsx`
- Create: `package.json`
- Test: `src/components/InstallCard.test.tsx`

**Steps:**
- [ ] Write a failing component test for install CTA text `安装 GitHub App`.
- [ ] Scaffold Next.js, TypeScript, Tailwind, Vitest.
- [ ] Implement homepage and `InstallCard` with permission explanation.
- [ ] Fetch `GET /api/github/app/install-url` through the frontend API client and use the returned `install_url`.
- [ ] Configure `NEXT_PUBLIC_API_BASE_URL` in `.env.example`; do not require `NEXT_PUBLIC_GITHUB_APP_INSTALL_URL`.
- [ ] Run: `npm test -- src/components/InstallCard.test.tsx`; expect pass.
- [ ] Commit: `feat: 添加 GitHub App 安装入口`

**Acceptance:**
- Homepage clearly explains install purpose and links to GitHub App install URL.

## Task 6: Frontend Installation Callback UI

**Repo:** `global-frontend`

**Files:**
- Create: `src/app/install/callback/page.tsx`
- Create: `src/lib/api.ts`
- Test: `src/app/install/callback/page.test.tsx`

**Steps:**
- [ ] Write a failing test for callback page showing `installation_id`.
- [ ] Implement callback page with success, missing parameter, canceled installation, and invalid state states.
- [ ] Add API client function to call backend verification with both `installation_id` and `state`.
- [ ] Show installed account and repository count when backend returns data.
- [ ] Render a retry link back to the backend install URL when callback verification fails.
- [ ] Run: `npm test -- src/app/install/callback/page.test.tsx`; expect pass.
- [ ] Commit: `feat: 添加 GitHub App 安装回调页面`

**Acceptance:**
- Callback page handles success, cancellation, and invalid callback states.

## Verification

Backend:

```bash
pytest tests/api/test_install_url.py tests/api/test_installations.py tests/api/test_installation_repositories.py -v
scripts/validate-repository.sh
git diff --check
```

Frontend:

```bash
npm test
npm run build
scripts/validate-repository.sh
git diff --check
```
