# Design: GitHub App Installation Verification & Authorized Repositories

## Architecture

```
FastAPI App
  ├── app/core/config.py          # pydantic-settings configuration
  ├── app/services/github_app.py  # GitHub API client (PyGithub + JWT)
  ├── app/api/installations.py    # Installation endpoints
  └── app/main.py                 # FastAPI app factory
```

## Component Design

### Configuration (`app/core/config.py`)

- Use `pydantic-settings` `BaseSettings` with `env_prefix="GITHUB_APP_"`
- Fields: `app_id: int`, `private_key: str`, `webhook_secret: str`
- Load private key from env (supports both raw PEM and base64-encoded)
- Singleton pattern via module-level instance

### GitHub App Client (`app/services/github_app.py`)

- Class `GitHubAppClient` wrapping PyGithub
- Method `get_installation(installation_id) -> InstallationInfo`
- Method `get_installation_repos(installation_id) -> list[RepositoryInfo]`
- Uses JWT for app-level auth, installation token for per-installation auth
- Maps GitHub API exceptions to domain exceptions

### API Endpoints (`app/api/installations.py`)

- `POST /api/github/installations/verify`
  - Request body: `{"installation_id": int}`
  - Response: `{"installation_id": int, "account_login": str, "account_type": str, "repository_selection": str}`
  - Errors: 404 (not found), 502 (GitHub API failure)

- `GET /api/github/installations/{installation_id}/repositories`
  - Response: `{"repositories": [{"full_name": str, "default_branch": str, "private": bool}]}`
  - Errors: 404 (not found), 502 (GitHub API failure)

### Error Handling

- GitHub exceptions mapped to safe HTTP errors
- No internal details leaked in error responses
- Logging preserves full error context for debugging

## Dependencies

- `fastapi` - web framework
- `pydantic-settings` - configuration
- `PyGithub` - GitHub API client
- `PyJWT` - JWT token generation (dependency of PyGithub)
- `cryptography` - private key handling (dependency of PyGithub)

## Testing Strategy

- Unit tests with mocked GitHub API responses
- Test both success and error paths
- Verify no tokens/secrets in any response
- Use `pytest` with `httpx` `TestClient` for endpoint tests
