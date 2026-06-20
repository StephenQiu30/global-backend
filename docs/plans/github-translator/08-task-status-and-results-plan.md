# PRD 08 Task Status And Results Implementation Plan

> **For agentic workers:** REQUIRED SUB-SKILL: Use superpowers:subagent-driven-development (recommended) or superpowers:executing-plans to implement this plan task-by-task. Steps use checkbox (`- [ ]`) syntax for tracking.

**Goal:** Display translation task progress, success PR links, file mappings, and actionable failure messages.

**Architecture:** First version can return task result synchronously, but response shape must support status pages and future polling. Frontend result components handle success and failure states.

**Tech Stack:** FastAPI response models, React result components, Vitest, Playwright.

## Global Constraints

- Status values: `queued`, `running`, `succeeded`, `failed`.
- Success result shows PR link and source-target mappings.
- Failure result shows error code, message, retry guidance.
- `POST /api/translation-tasks` and `GET /api/translation-tasks/{task_id}` must return the same result schema.
- PRD source: `docs/prd/github-translator/08-task-status-and-results.md`.

---

## Task 1: Backend Task Result Shape

**Repo:** `global-backend`

**Files:**
- Modify: `app/domain/task.py`
- Test: `tests/domain/test_task_result.py`

**Steps:**
- [ ] Write failing tests for success and failure result serialization.
- [ ] Add `TaskResult` fields: `task_id`, `status`, `repository`, `language`, `selected_files`, `pr_url`, `error_code`, `error_message`, `file_mappings`.
- [ ] Ensure failed result does not require PR URL.
- [ ] Run: `pytest tests/domain/test_task_result.py -v`; expect pass.
- [ ] Commit: `feat: 标准化任务结果结构`

**Acceptance:**
- API and frontend share stable result semantics.

## Task 2: Backend Safe Error Mapping

**Repo:** `global-backend`

**Files:**
- Create: `app/core/errors.py`
- Modify: `app/api/tasks.py`
- Test: `tests/api/test_task_errors.py`

**Steps:**
- [ ] Write failing tests for validation error, GitHub permission error, and translation timeout.
- [ ] Implement `AppError(code, message, retryable)`.
- [ ] Map expected errors to `failed` task responses.
- [ ] Avoid returning secrets, stack traces, or provider raw payloads.
- [ ] Run: `pytest tests/api/test_task_errors.py -v`; expect pass.
- [ ] Commit: `feat: 添加任务错误结果映射`

**Acceptance:**
- Failed tasks produce actionable, safe messages.

## Task 3: Backend Task Status API

**Repo:** `global-backend`

**Files:**
- Modify: `app/api/tasks.py`
- Modify: `app/services/task_store.py`
- Test: `tests/api/test_task_status.py`

**Steps:**
- [ ] Write failing test for `GET /api/translation-tasks/{task_id}` returning a saved success result.
- [ ] Write failing test for unknown task returning `task_not_found`.
- [ ] Read task results from `TaskStore`.
- [ ] Return the same schema used by `POST /api/translation-tasks`.
- [ ] Run: `pytest tests/api/test_task_status.py -v`; expect pass.
- [ ] Commit: `feat: 添加翻译任务状态查询接口`

**Acceptance:**
- Frontend task page can poll a concrete backend endpoint.
- Unknown task IDs return a safe, user-readable error.

## Task 4: Frontend Result Component

**Repo:** `global-frontend`

**Files:**
- Create: `src/components/TaskResult.tsx`
- Test: `src/components/TaskResult.test.tsx`

**Steps:**
- [ ] Write failing test for success PR link.
- [ ] Write failing test for failure message and retry button.
- [ ] Implement success panel with PR link and file mappings.
- [ ] Implement failure panel with error message and back-to-edit action.
- [ ] Run: `npm test -- src/components/TaskResult.test.tsx`; expect pass.
- [ ] Commit: `feat: 添加任务结果展示组件`

**Acceptance:**
- User can see whether to review PR or fix input.

## Task 5: Frontend Task Page

**Repo:** `global-frontend`

**Files:**
- Create: `src/app/tasks/[taskId]/page.tsx`
- Test: `src/app/tasks/[taskId]/page.test.tsx`

**Steps:**
- [ ] Write failing test that task page renders loading and final result states.
- [ ] Implement simple polling every 2 seconds for at most 2 minutes.
- [ ] Render timeout message if task stays unresolved.
- [ ] Connect to `GET /api/translation-tasks/{task_id}`.
- [ ] Treat `task_not_found` as a failed state with a back-to-translate action.
- [ ] Run: `npm test -- src/app/tasks/[taskId]/page.test.tsx`; expect pass.
- [ ] Commit: `feat: 添加任务状态页面`

**Acceptance:**
- Task status is visible after submission.

## Task 6: E2E Result Smoke Test

**Repo:** `global-frontend`

**Files:**
- Create: `tests/e2e/task-result.spec.ts`

**Steps:**
- [ ] Add Playwright test with mocked backend success result.
- [ ] Assert PR link is visible.
- [ ] Assert file mapping is visible.
- [ ] Run: `npm run e2e -- tests/e2e/task-result.spec.ts`; expect pass.
- [ ] Commit: `test: 添加任务结果端到端冒烟测试`

**Acceptance:**
- Browser flow can display successful task result.

## Verification

```bash
pytest tests/domain/test_task_result.py tests/api/test_task_errors.py tests/api/test_task_status.py -v
npm test -- src/components/TaskResult.test.tsx src/app/tasks/[taskId]/page.test.tsx
```
