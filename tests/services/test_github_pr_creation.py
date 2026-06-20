"""Tests for GitHub PR creation via GitHubAppClient."""

import respx
import httpx

from app.services.github_app import GitHubAppClient


INSTALLATION_ID = 12345
FULL_NAME = "owner/repo"


@respx.mock
def test_create_pull_request():
    """create_pull_request creates a PR and returns url and number."""
    client = GitHubAppClient(app_id="1", private_key="fake", token_provider=lambda _: "ghs_test")

    respx.post(
        "https://api.github.com/repos/owner/repo/pulls"
    ).mock(return_value=httpx.Response(201, json={
        "number": 42,
        "html_url": "https://github.com/owner/repo/pull/42",
    }))

    result = client.create_pull_request(
        INSTALLATION_ID, FULL_NAME,
        title="docs: add zh-CN translation",
        body="Auto-translated",
        head="translate/zh-CN/task-001",
        base="main",
    )
    assert result["number"] == 42
    assert result["url"] == "https://github.com/owner/repo/pull/42"


@respx.mock
def test_create_pull_request_returns_existing_when_already_open():
    """create_pull_request returns existing PR when 422 (already exists)."""
    client = GitHubAppClient(app_id="1", private_key="fake", token_provider=lambda _: "ghs_test")

    respx.post(
        "https://api.github.com/repos/owner/repo/pulls"
    ).mock(return_value=httpx.Response(422, json={
        "message": "Validation Failed",
        "errors": [{"message": "A pull request already exists"}],
    }))

    # Mock listing open PRs to find existing one
    respx.get(
        "https://api.github.com/repos/owner/repo/pulls",
        params={"head": "owner:translate/zh-CN/task-001", "state": "open"}
    ).mock(return_value=httpx.Response(200, json=[{
        "number": 38,
        "html_url": "https://github.com/owner/repo/pull/38",
    }]))

    result = client.create_pull_request(
        INSTALLATION_ID, FULL_NAME,
        title="docs: add zh-CN translation",
        body="Auto-translated",
        head="translate/zh-CN/task-001",
        base="main",
    )
    assert result["number"] == 38
    assert result["url"] == "https://github.com/owner/repo/pull/38"
