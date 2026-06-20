# Design: STE-329 Security, Permissions, and Abuse Prevention

## Architecture

Security enforcement is layered:
1. **Domain layer** (`app/domain/`) - Pure validators for paths and file types
2. **Service layer** (`app/services/`) - Authorization and task limit enforcement
3. **API layer** (`app/api/`) - HTTP error responses for security violations

## Design Decisions

### 1. Path Validation as Domain Logic

Path safety is a pure function in `app/domain/markdown_files.py`:
- Rejects paths containing `..`
- Rejects absolute paths starting with `/`
- Rejects non-Markdown extensions (only `.md` and `.markdown` allowed)
- Returns validated path or raises `ValueError`

This follows the existing pattern in `app/domain/repository.py`.

### 2. Authorization as Shared Service

Authorization enforcement uses the existing `GitHubAppClient.is_repository_authorized()`:
- A helper function `require_repository_authorization()` wraps the check
- Returns structured error code `repository_not_installed` on failure
- Used by both scan and task creation endpoints

### 3. Secret Leakage as Regression Tests

No new production code needed for Task 3 - the tests verify existing behavior:
- Test all API endpoints for absence of `token`, `private_key`, `OPENAI_API_KEY`
- Test error responses for absence of raw stack traces
- Regression protection for future changes

### 4. Task Limits as Service Validation

Task limits are enforced in `app/services/task_runner.py`:
- `validate_task_limits()` checks file count and total size
- Raises `TaskLimitError` with structured error details
- Called before any translation/model invocation

## File Structure

```
app/domain/markdown_files.py          # Path/file safety validators
app/services/task_runner.py           # Task limit enforcement
tests/domain/test_security_paths.py   # Path safety tests
tests/api/test_authorization_enforcement.py  # Authorization tests
tests/api/test_secret_leakage.py      # Secret leakage regression
tests/services/test_task_limits.py    # Task limit tests
```
