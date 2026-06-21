# Spec: Authorization Enforcement

## Requirements

1. All task-related endpoints must verify repository authorization via GitHub App installation
2. Unauthorized repositories receive `repository_not_installed` error (403)
3. Authorization is re-checked at task execution time, not just at resolve time
4. Missing or invalid installation_id results in 400/404

## Test Cases

- Scan endpoint with unauthorized repo -> 403
- Task creation with unauthorized repo -> 403
- Task execution re-checks authorization -> 403 if revoked
- Valid authorization -> proceed normally
