"""Tests for GitHub branch creation via GitHubAppClient."""

import respx
import httpx

from app.services.github_app import GitHubAppClient


INSTALLATION_ID = 12345
FULL_NAME = "owner/repo"
BASE_BRANCH = "main"
BRANCH_NAME = "translate/zh-CN/task-001"
DEFAULT_SHA = "abc123def456"


@respx.mock
def test_create_branch_from_default_sha():
    """create_branch fetches default branch SHA and creates a new ref."""
    client = GitHubAppClient(app_id="1", private_key="fake", token_provider=lambda _: "ghs_test")

    # Mock get default branch SHA
    respx.get(
        "https://api.github.com/repos/owner/repo/git/ref/heads/main"
    ).mock(return_value=httpx.Response(200, json={"object": {"sha": DEFAULT_SHA}}))

    # Mock create ref
    respx.post(
        "https://api.github.com/repos/owner/repo/git/refs"
    ).mock(return_value=httpx.Response(201, json={"ref": f"refs/heads/{BRANCH_NAME}"}))

    result = client.create_branch(INSTALLATION_ID, FULL_NAME, BASE_BRANCH, BRANCH_NAME)
    assert result == BRANCH_NAME


@respx.mock
def test_create_branch_returns_existing_when_ref_exists():
    """create_branch returns existing branch when ref already exists (422)."""
    client = GitHubAppClient(app_id="1", private_key="fake", token_provider=lambda _: "ghs_test")

    respx.get(
        "https://api.github.com/repos/owner/repo/git/ref/heads/main"
    ).mock(return_value=httpx.Response(200, json={"object": {"sha": DEFAULT_SHA}}))

    # 422 means ref already exists
    respx.post(
        "https://api.github.com/repos/owner/repo/git/refs"
    ).mock(return_value=httpx.Response(422, json={"message": "Reference already exists"}))

    result = client.create_branch(INSTALLATION_ID, FULL_NAME, BASE_BRANCH, BRANCH_NAME)
    assert result == BRANCH_NAME
