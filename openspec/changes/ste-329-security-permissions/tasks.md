# Tasks: STE-329 Security, Permissions, and Abuse Prevention

## Task 1: Path and File Safety Tests
- [ ] Write failing tests for path traversal (`../README.md`, `/README.md`)
- [ ] Write failing tests for non-Markdown files (`README.txt`)
- [ ] Write failing tests for translated variants (`README.zh-CN.md`)
- [ ] Implement `validate_markdown_path()` in `app/domain/markdown_files.py`
- [ ] Run `pytest tests/domain/test_security_paths.py -v` - expect pass

## Task 2: Authorization Enforcement
- [ ] Write failing test: unauthorized repo cannot scan Markdown
- [ ] Write failing test: unauthorized repo cannot create task
- [ ] Write failing test: task execution re-checks authorization
- [ ] Implement `require_repository_authorization()` helper
- [ ] Run `pytest tests/api/test_authorization_enforcement.py -v` - expect pass

## Task 3: Secret Leakage Regression
- [ ] Write tests asserting no tokens/keys in responses
- [ ] Write tests asserting no raw stack traces in error responses
- [ ] Run `pytest tests/api/test_secret_leakage.py -v` - expect pass

## Task 4: Task Size Limits
- [ ] Write failing test: >10 files rejected
- [ ] Write failing test: >200KB total rejected
- [ ] Write failing test: sizes from GitHub, not request
- [ ] Implement `validate_task_limits()` in `app/services/task_runner.py`
- [ ] Run `pytest tests/services/test_task_limits.py -v` - expect pass

## Verification

```bash
pytest tests/domain/test_security_paths.py tests/api/test_authorization_enforcement.py tests/api/test_secret_leakage.py tests/services/test_task_limits.py -v
```
