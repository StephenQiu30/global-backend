# Proposal: GitHub App Installation Verification & Authorized Repositories API

## Summary

Add backend infrastructure for GitHub App installation verification and authorized repository listing. This is the first backend capability for the GitHub Markdown Translator product.

## Normative Files Changed

- New: `app/core/config.py` (GitHub App configuration)
- New: `app/services/github_app.py` (GitHub API client)
- New: `app/api/installations.py` (installation endpoints)
- New: `tests/api/test_installations.py` (installation verify tests)
- New: `tests/api/test_installation_repositories.py` (repository listing tests)

## Scope

### In Scope

- `GITHUB_APP_ID`, private key, webhook secret configuration via pydantic-settings
- Installation verification endpoint: `POST /api/github/installations/verify`
- Authorized repositories endpoint: `GET /api/github/installations/{installation_id}/repositories`
- GitHub App client using PyGithub with JWT auth
- Error mapping from GitHub API to safe HTTP responses
- Security: no tokens/secrets in response bodies

### Out of Scope

- Frontend installation page
- Markdown file scanning
- Translation tasks
- PR creation
- OAuth user login
- Webhook handling

### Non-Goals

- Return installation tokens to frontend
- Implement OAuth user authentication
- Support GitHub App creation/management

## Impact

- Establishes the GitHub App installation as the primary permission boundary for the first version
- Foundation for all subsequent GitHub API interactions (file reading, PR creation)
- Security boundary: tokens stay server-side only

## Risks

- GitHub API rate limits on installation token requests
- Private key management in development vs production
- Mock strategy for testing without real GitHub App
