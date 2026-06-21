# Tasks: GitHub 分支、文件写入与 PR 创建

## T1: Project Foundation

- [x] Create `pyproject.toml` with dependencies (fastapi, httpx, pyjwt, pydantic-settings, pytest, respx)
- [x] Create `app/__init__.py`, `app/core/__init__.py`, `app/services/__init__.py`, `app/domain/__init__.py`
- [x] Create `app/core/config.py` with `Settings` class
- [x] Create `app/core/errors.py` with `AppError`
- [x] Create `tests/__init__.py`, `tests/services/__init__.py`
- [x] Validation: `pytest tests/ -v` (empty suite passes)

## T2: GitHub Branch Creation

- [x] File: `app/services/github_app.py`, `tests/services/test_github_branch_creation.py`
- [x] Red: test `create_branch` mocks default branch ref lookup and refs creation
- [x] Green: implement `create_branch(installation_id, full_name, base_branch, branch_name)`
- [x] Validation: `pytest tests/services/test_github_branch_creation.py -v`

## T3: GitHub File Write

- [x] File: `app/services/github_app.py`, `tests/services/test_github_file_write.py`
- [x] Red: test `put_file` for writing `README.zh-CN.md` to branch
- [x] Green: implement `put_file` with base64 encoding and SHA lookup for updates
- [x] Validation: `pytest tests/services/test_github_file_write.py -v`

## T4: PR Body Builder

- [x] File: `app/services/pr_description.py`, `tests/services/test_pr_description.py`
- [x] Red: test PR body contains language, mappings, provider, task_id
- [x] Green: implement `build_translation_pr_body`
- [x] Validation: `pytest tests/services/test_pr_description.py -v`

## T5: PR Creation

- [x] File: `app/services/github_app.py`, `tests/services/test_github_pr_creation.py`
- [x] Red: test `create_pull_request` with title, body, head, base
- [x] Green: implement `create_pull_request` returning url and number
- [x] Validation: `pytest tests/services/test_github_pr_creation.py -v`

## T6: Task Runner PR Flow

- [x] File: `app/services/task_runner.py`, `tests/services/test_task_runner_pr_flow.py`
- [x] Red: test call order (create_branch → put_file → create_pull_request)
- [x] Red: test translation failure creates no branch/file/PR
- [x] Green: implement task runner PR flow with two-phase design
- [x] Validation: `pytest tests/services/test_task_runner_pr_flow.py -v`

## Verification

```bash
pytest tests/services/test_github_* tests/services/test_pr_description.py tests/services/test_task_runner_pr_flow.py -v
```
