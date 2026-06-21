# Tasks: STE-329 Security, Permissions, and Abuse Prevention

## Task 1: Path and File Safety Tests
- [x] Write failing tests for path traversal (`../README.md`, `/README.md`)
- [x] Write failing tests for non-Markdown files (`README.txt`)
- [x] Write failing tests for translated variants (`README.zh-CN.md`)
- [x] Implement `validate_markdown_path()` in `app/domain/markdown_files.py`
- [x] Run `pytest tests/domain/test_security_paths.py -v` - expect pass

## Task 2: Authorization Enforcement
- [x] Write failing test: unauthorized repo cannot scan Markdown
- [x] Write failing test: unauthorized repo cannot create task
- [x] Write failing test: task execution re-checks authorization
- [x] Implement `require_repository_authorization()` helper
- [x] Run `pytest tests/api/test_authorization_enforcement.py -v` - expect pass

## Task 3: Secret Leakage Regression
- [x] Write tests asserting no tokens/keys in responses
- [x] Write tests asserting no raw stack traces in error responses
- [x] Run `pytest tests/api/test_secret_leakage.py -v` - expect pass

## Task 4: Task Size Limits
- [x] Write failing test: >10 files rejected
- [x] Write failing test: >200KB total rejected
- [x] Write failing test: sizes from GitHub, not request
- [x] Implement `validate_task_limits()` in `app/services/task_runner.py`
- [x] Run `pytest tests/services/test_task_limits.py -v` - expect pass

## Verification

```bash
pytest tests/domain/test_security_paths.py tests/api/test_authorization_enforcement.py tests/api/test_secret_leakage.py tests/services/test_task_limits.py -v
```
