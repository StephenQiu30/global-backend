# PRD 05 Translation Task Implementation Plan

> **For agentic workers:** REQUIRED SUB-SKILL: Use superpowers:subagent-driven-development (recommended) or superpowers:executing-plans to implement this plan task-by-task. Steps use checkbox (`- [ ]`) syntax for tracking.

**Goal:** Create and execute translation tasks that read selected Markdown files, translate them, and prepare PR submission results.

**Architecture:** A task runner coordinates repository authorization, file validation, content reading, Markdown translation, GitHub file writes, and task result creation. The API remains thin and testable.

**Tech Stack:** FastAPI, Pydantic, pytest-asyncio, OpenAI provider abstraction.

## Global Constraints

- First version uses synchronous execution with clear timeout and failure states.
- Task states: `queued`, `running`, `succeeded`, `failed`.
- Max 10 files and 200KB total source Markdown.
- Task execution must verify installation authorization immediately before reading files or writing PR branches; frontend-provided repository data is not trusted.
- The task result must be saved at least in an in-memory repository for first version so the frontend can show a result page and PRD 08 can add polling without changing response shape.
- PRD source: `docs/prd/github-translator/05-translation-task.md`.

---

## Task 1: Task Domain Models

**Repo:** `global-backend`

**Files:**
- Create: `app/domain/task.py`
- Test: `tests/domain/test_task.py`

**Steps:**
- [ ] Write failing tests for valid request and invalid empty files.
- [ ] Implement `TranslateTaskRequest` with `installation_id`, `repository_full_name`, `base_branch`, `files`, and `language`.
- [ ] Implement `TranslateTaskResult`.
- [ ] Implement `TaskStatus` literal values.
- [ ] Include `task_id`, `created_at`, and `updated_at` fields in results for PRD 08 compatibility.
- [ ] Run: `pytest tests/domain/test_task.py -v`; expect pass.
- [ ] Commit: `feat: 添加翻译任务领域模型`

**Acceptance:**
- Task input and output shape is stable for API and frontend.

## Task 2: Translation Provider Interface

**Repo:** `global-backend`

**Files:**
- Create: `app/services/translation_provider.py`
- Test: `tests/services/test_translation_provider_contract.py`

**Steps:**
- [ ] Write failing contract test with fake provider.
- [ ] Define `TranslationProvider` protocol with `translate_markdown(source, language)`.
- [ ] Implement `FakeTranslationProvider` in tests.
- [ ] Run: `pytest tests/services/test_translation_provider_contract.py -v`; expect pass.
- [ ] Commit: `feat: 添加翻译 Provider 接口`

**Acceptance:**
- Task runner can use any provider implementation.

## Task 3: Task Runner

**Repo:** `global-backend`

**Files:**
- Create: `app/services/task_runner.py`
- Create: `app/services/task_store.py`
- Test: `tests/services/test_task_runner.py`
- Test: `tests/services/test_task_store.py`

**Steps:**
- [ ] Write failing test using fake GitHub client and fake translation provider.
- [ ] Write failing test proving unauthorized repository errors before any `get_file_content` call.
- [ ] Implement task validation for language and file limits.
- [ ] Verify installation authorization against GitHub App repository list immediately before reading files.
- [ ] Read source file content from GitHub client.
- [ ] Translate each selected file.
- [ ] Build source-target file mappings.
- [ ] Save `running`, `succeeded`, and `failed` results to `TaskStore`.
- [ ] Return `succeeded` result with PR URL after PR creation.
- [ ] Return `failed` result with `error_code` and `error_message` on expected app errors.
- [ ] Run: `pytest tests/services/test_task_runner.py tests/services/test_task_store.py -v`; expect pass.
- [ ] Commit: `feat: 添加翻译任务执行器`

**Acceptance:**
- A task can translate one or more Markdown files and return a structured result.

## Task 4: Translation Task API

**Repo:** `global-backend`

**Files:**
- Create: `app/api/tasks.py`
- Modify: `app/main.py`
- Test: `tests/api/test_translation_tasks.py`

**Steps:**
- [ ] Write failing test for `POST /api/translation-tasks`.
- [ ] Write failing test that successful submission returns `task_id`.
- [ ] Validate request body.
- [ ] Call task runner.
- [ ] Return task result JSON.
- [ ] Map unexpected exceptions to `failed` response with safe error message.
- [ ] Run: `pytest tests/api/test_translation_tasks.py -v`; expect pass.
- [ ] Commit: `feat: 添加翻译任务接口`

**Acceptance:**
- Frontend can submit a selected repository, files, and language to create a translation task and receive a stable `task_id`.

## Task 5: Frontend Translation Workflow Submission

**Repo:** `global-frontend`

**Files:**
- Create: `src/app/translate/page.tsx`
- Modify: `src/lib/api.ts`
- Test: `src/app/translate/page.test.tsx`

**Steps:**
- [ ] Write failing test for workflow page controls and submit button `创建翻译 PR`.
- [ ] Compose repository selector, language selector, and file picker.
- [ ] Submit task payload to `POST /api/translation-tasks`.
- [ ] Navigate to `/tasks/{task_id}` after successful response.
- [ ] Disable submit until repository, language, and files are valid.
- [ ] Run: `npm test -- src/app/translate/page.test.tsx`; expect pass.
- [ ] Commit: `feat: 添加翻译任务提交页面`

**Acceptance:**
- User can submit the first-version Web workflow from a single page.

## Verification

```bash
pytest tests/domain/test_task.py tests/services/test_task_runner.py tests/services/test_task_store.py tests/api/test_translation_tasks.py -v
npm test -- src/app/translate/page.test.tsx
```
