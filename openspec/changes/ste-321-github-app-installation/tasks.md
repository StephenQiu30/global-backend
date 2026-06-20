# Tasks: GitHub App Installation Verification & Authorized Repositories

## Task 1: Project scaffolding

- [ ] 1.1 Create `pyproject.toml` with dependencies (fastapi, pydantic-settings, PyGithub, uvicorn, pytest, httpx)
- [ ] 1.2 Create `app/__init__.py`, `app/core/__init__.py`, `app/services/__init__.py`, `app/api/__init__.py`
- [ ] 1.3 Create `app/main.py` with FastAPI app factory
- [ ] 1.4 Create `tests/__init__.py`, `tests/api/__init__.py`, `tests/conftest.py`
- [ ] 1.5 Verify: `python -c "from app.main import app; print(app.title)"` works

## Task 2: Configuration (TDD)

- [ ] 2.1 Write `tests/test_config.py` with red tests for GitHub App config loading
- [ ] 2.2 Implement `app/core/config.py` with `Settings` class
- [ ] 2.3 Verify: `pytest tests/test_config.py -v` passes

## Task 3: GitHub App client (TDD)

- [ ] 3.1 Write `tests/test_github_app_client.py` with red tests for installation verification and repo listing
- [ ] 3.2 Implement `app/services/github_app.py` with `GitHubAppClient`
- [ ] 3.3 Verify: `pytest tests/test_github_app_client.py -v` passes

## Task 4: Installation verify endpoint (TDD)

- [ ] 4.1 Write `tests/api/test_installations.py` with red tests for POST /api/github/installations/verify
- [ ] 4.2 Implement installation verify endpoint in `app/api/installations.py`
- [ ] 4.3 Verify: `pytest tests/api/test_installations.py -v` passes

## Task 5: Installation repositories endpoint (TDD)

- [ ] 5.1 Write `tests/api/test_installation_repositories.py` with red tests for GET /api/github/installations/{id}/repositories
- [ ] 5.2 Implement repositories endpoint in `app/api/installations.py`
- [ ] 5.3 Verify: `pytest tests/api/test_installation_repositories.py -v` passes

## Task 6: Security audit & validation

- [ ] 6.1 Verify no tokens/secrets appear in any response body
- [ ] 6.2 Run full test suite: `pytest tests/ -v`
- [ ] 6.3 Run validation script: `scripts/validate-repository.sh`
- [ ] 6.4 Run `git diff --check`

## Task 7: OpenSpec sync & handoff

- [ ] 7.1 Update `openspec/specs/` with accepted GitHub App installation spec
- [ ] 7.2 Update workpad with final validation evidence
- [ ] 7.3 Prepare PR with test-first evidence
