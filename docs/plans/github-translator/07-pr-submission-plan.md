# PRD 07 Pull Request Submission Implementation Plan

> **For agentic workers:** REQUIRED SUB-SKILL: Use superpowers:subagent-driven-development (recommended) or superpowers:executing-plans to implement this plan task-by-task. Steps use checkbox (`- [ ]`) syntax for tracking.

**Goal:** Submit translated Markdown files to GitHub through a branch, commit, and Pull Request.

**Architecture:** GitHub write operations live in `GitHubAppClient`. Task runner calls high-level methods to create branches, write files, and create PRs. PR body generation is pure and tested separately.

**Tech Stack:** FastAPI backend, GitHub REST API, pytest, respx.

## Global Constraints

- Do not push directly to default branch.
- Write only target language suffix files.
- Multiple files in one task go into one branch and one PR.
- Translation must complete for every selected file before the first GitHub write. Failed translation must not create a branch, file commit, or half-finished PR.
- PRD source: `docs/prd/github-translator/07-pr-submission.md`.

---

## Task 1: GitHub Branch Creation

**Repo:** `global-backend`

**Files:**
- Modify: `app/services/github_app.py`
- Test: `tests/services/test_github_branch_creation.py`

**Steps:**
- [ ] Write failing test that mocks default branch ref lookup and refs creation.
- [ ] Implement `create_branch(installation_id, full_name, base_branch, branch_name)`.
- [ ] Return created branch name.
- [ ] Handle branch exists by returning existing branch when safe.
- [ ] Run: `pytest tests/services/test_github_branch_creation.py -v`; expect pass.
- [ ] Commit: `feat: 添加 GitHub 翻译分支创建`

**Acceptance:**
- Backend can create a branch from default branch SHA.

## Task 2: GitHub File Write

**Repo:** `global-backend`

**Files:**
- Modify: `app/services/github_app.py`
- Test: `tests/services/test_github_file_write.py`

**Steps:**
- [ ] Write failing test for writing `README.zh-CN.md` to branch.
- [ ] Implement `put_file(installation_id, full_name, branch, path, content, message)`.
- [ ] Base64-encode content.
- [ ] Support update of existing target file by fetching existing SHA first.
- [ ] Ensure file writes reject source paths and accept only target language suffix paths.
- [ ] Run: `pytest tests/services/test_github_file_write.py -v`; expect pass.
- [ ] Commit: `feat: 添加 GitHub 翻译文件写入`

**Acceptance:**
- Backend writes translated files to the translation branch only.

## Task 3: PR Body Builder

**Repo:** `global-backend`

**Files:**
- Create: `app/services/pr_description.py`
- Test: `tests/services/test_pr_description.py`

**Steps:**
- [ ] Write failing test for PR body containing target language, mappings, provider, and review reminder.
- [ ] Implement `build_translation_pr_body(language, mappings, provider_name, task_id)`.
- [ ] Ensure body is valid Markdown.
- [ ] Run: `pytest tests/services/test_pr_description.py -v`; expect pass.
- [ ] Commit: `feat: 添加翻译 PR 描述生成`

**Acceptance:**
- PR body contains all PRD-required review context.

## Task 4: PR Creation

**Repo:** `global-backend`

**Files:**
- Modify: `app/services/github_app.py`
- Test: `tests/services/test_github_pr_creation.py`

**Steps:**
- [ ] Write failing test for creating PR with title, body, head, and base.
- [ ] Implement `create_pull_request`.
- [ ] Return `url` and `number`.
- [ ] Handle existing open PR for same branch by returning existing PR.
- [ ] Run: `pytest tests/services/test_github_pr_creation.py -v`; expect pass.
- [ ] Commit: `feat: 添加 GitHub Pull Request 创建`

**Acceptance:**
- Successful translation task returns a GitHub PR URL.

## Task 5: End-To-End Task Runner PR Flow

**Repo:** `global-backend`

**Files:**
- Modify: `app/services/task_runner.py`
- Test: `tests/services/test_task_runner_pr_flow.py`

**Steps:**
- [ ] Write failing test asserting call order: create branch, write files, create PR.
- [ ] Write failing test asserting translation of all selected files completes before `create_branch` is called.
- [ ] Write failing test asserting a translation failure creates no branch, no file write, and no PR.
- [ ] Update task runner to use branch/file/PR methods.
- [ ] Split task runner into two phases: prepare all translated outputs in memory, then perform GitHub writes.
- [ ] Ensure no GitHub write happens if any translation, target path validation, or size validation fails.
- [ ] Run: `pytest tests/services/test_task_runner_pr_flow.py -v`; expect pass.
- [ ] Commit: `feat: 串联翻译任务 PR 提交流程`

**Acceptance:**
- Multi-file translation creates one branch and one PR.
- Translation failure before write phase leaves the target repository unchanged.

## Verification

```bash
pytest tests/services/test_github_* tests/services/test_pr_description.py tests/services/test_task_runner_pr_flow.py -v
```
