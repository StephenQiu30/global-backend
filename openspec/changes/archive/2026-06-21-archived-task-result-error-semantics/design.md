# Design: Task Result & Error Semantics

## Architecture

Follow the existing three-layer architecture:
- `app/domain/task.py` — Pure domain models (already exists from STE-325)
- `app/core/errors.py` — Application-level error types (no I/O)
- `app/api/tasks.py` — API error mapping (FastAPI HTTPException conversion)

## Data Flow

```
Service layer raises AppError
    ↓
API layer catches AppError
    ↓
map_error_to_response() converts to HTTPException
    ↓
FastAPI returns JSON: {"error": "...", "message": "...", "retryable": ...}
```

## State Machine (existing)

```
QUEUED → RUNNING → SUCCEEDED
                 → FAILED
```

- `SUCCEEDED` state carries: `pr_url`, `pr_number`, `mappings`
- `FAILED` state carries: `error_code`, `error_message`

## Error Code Registry

| Code | HTTP Status | Retryable | Description |
|------|-------------|-----------|-------------|
| `github_permission_denied` | 403 | false | GitHub App lacks repo access |
| `github_rate_limited` | 429 | true | GitHub API rate limit hit |
| `model_timeout` | 504 | true | LLM provider timed out |
| `model_rate_limited` | 429 | true | LLM provider rate limit |
| `translation_failed` | 500 | false | Generic translation failure |
| `internal_error` | 500 | false | Catch-all for unknown errors |

## Security Constraints

- API responses MUST NEVER include: raw exception messages for unhandled errors, stack traces, tokens, secrets, provider responses
- `AppError.message` for known errors IS safe to expose (designed as user-facing)
- Unknown exceptions get generic "An unexpected error occurred" message

## Rollback Impact

- New files only; no existing code modified
- Removing `app/core/errors.py` and the `map_error_to_response` function reverts to pre-change state
