# Tasks: GitHub 分支、文件写入与 PR 创建

## T1: Project Foundation

- Create `pyproject.toml` with dependencies (fastapi, httpx, pyjwt, pydantic-settings, pytest, respx)
- Create `app/__init__.py`, `app/core/__init__.py`, `app/services/__init__.py`, `app/domain/__init__.py`
- Create `app/core/config.py` with `Settings` class
- Create `app/core/errors.py` with `AppError`
- Create `tests/__init__.py`, `tests/services/__init__.py`
- Validation: `pytest tests/ -v` (empty suite passes)

## T2: GitHub Branch Creation

- File: `app/services/github_app.py`, `tests/services/test_github_branch_creation.py`
- Red: test `create_branch` mocks default branch ref lookup and refs creation
- Green: implement `create_branch(installation_id, full_name, base_branch, branch_name)`
- Validation: `pytest tests/services/test_github_branch_creation.py -v`

## T3: GitHub File Write

- File: `app/services/github_app.py`, `tests/services/test_github_file_write.py`
- Red: test `put_file` for writing `README.zh-CN.md` to branch
- Green: implement `put_file` with base64 encoding and SHA lookup for updates
- Validation: `pytest tests/services/test_github_file_write.py -v`

## T4: PR Body Builder

- File: `app/services/pr_description.py`, `tests/services/test_pr_description.py`
- Red: test PR body contains language, mappings, provider, task_id
- Green: implement `build_translation_pr_body`
- Validation: `pytest tests/services/test_pr_description.py -v`

## T5: PR Creation

- File: `app/services/github_app.py`, `tests/services/test_github_pr_creation.py`
- Red: test `create_pull_request` with title, body, head, base
- Green: implement `create_pull_request` returning url and number
- Validation: `pytest tests/services/test_github_pr_creation.py -v`

## T6: Task Runner PR Flow

- File: `app/services/task_runner.py`, `tests/services/test_task_runner_pr_flow.py`
- Red: test call order (create_branch → put_file → create_pull_request)
- Red: test translation failure creates no branch/file/PR
- Green: implement task runner PR flow with two-phase design
- Validation: `pytest tests/services/test_task_runner_pr_flow.py -v`

## Verification

```bash
pytest tests/services/test_github_* tests/services/test_pr_description.py tests/services/test_task_runner_pr_flow.py -v
```
