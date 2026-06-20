# PRD 05 Translation Task Implementation Plan

> **For agentic workers:** REQUIRED SUB-SKILL: Use superpowers:subagent-driven-development (recommended) or superpowers:executing-plans to implement this plan task-by-task. Steps use checkbox (`- [ ]`) syntax for tracking.

**Goal:** Create and execute translation tasks that read selected Markdown files, translate them, and prepare PR submission results.

**Architecture:** A task runner coordinates repository authorization, file validation, content reading, Markdown translation, GitHub file writes, and task result creation. The API remains thin and testable.

**Tech Stack:** FastAPI, Pydantic, pytest-asyncio, OpenAI provider abstraction.

## Global Constraints

- First version uses synchronous execution with clear timeout and failure states.
- Task states: `queued`, `running`, `succeeded`, `failed`.
- Max 10 files and 200KB total source Markdown.
- PRD source: `docs/prd/github-translator/05-translation-task.md`.

---

## Task 1: Task Domain Models

**Repo:** `global-backend`

**Files:**
- Create: `app/domain/task.py`
- Test: `tests/domain/test_task.py`

**Steps:**
- [ ] Write failing tests for valid request and invalid empty files.
- [ ] Implement `TranslateTaskRequest`.
- [ ] Implement `TranslateTaskResult`.
- [ ] Implement `TaskStatus` literal values.
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
- Test: `tests/services/test_task_runner.py`

**Steps:**
- [ ] Write failing test using fake GitHub client and fake translation provider.
- [ ] Implement task validation for language and file limits.
- [ ] Read source file content from GitHub client.
- [ ] Translate each selected file.
- [ ] Build source-target file mappings.
- [ ] Return `succeeded` result with PR URL after PR creation.
- [ ] Return `failed` result with `error_code` and `error_message` on expected app errors.
- [ ] Run: `pytest tests/services/test_task_runner.py -v`; expect pass.
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
- [ ] Validate request body.
- [ ] Call task runner.
- [ ] Return task result JSON.
- [ ] Map unexpected exceptions to `failed` response with safe error message.
- [ ] Run: `pytest tests/api/test_translation_tasks.py -v`; expect pass.
- [ ] Commit: `feat: 添加翻译任务接口`

**Acceptance:**
- Frontend can submit a selected repository, files, and language to create a translation task.

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
- [ ] Navigate to result page or render result state after response.
- [ ] Disable submit until repository, language, and files are valid.
- [ ] Run: `npm test -- src/app/translate/page.test.tsx`; expect pass.
- [ ] Commit: `feat: 添加翻译任务提交页面`

**Acceptance:**
- User can submit the first-version Web workflow from a single page.

## Verification

```bash
pytest tests/domain/test_task.py tests/services/test_task_runner.py tests/api/test_translation_tasks.py -v
npm test -- src/app/translate/page.test.tsx
```
