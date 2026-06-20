"""Tests for GitHub file write via GitHubAppClient."""

import base64

import respx
import httpx

from app.services.github_app import GitHubAppClient


INSTALLATION_ID = 12345
FULL_NAME = "owner/repo"
BRANCH = "translate/zh-CN/task-001"


@respx.mock
def test_put_file_creates_new_file():
    """put_file writes a translated file to the branch with base64 encoding."""
    client = GitHubAppClient(app_id="1", private_key="fake", token_provider=lambda _: "ghs_test")

    # Mock GET for new file (404 = doesn't exist)
    respx.get(
        "https://api.github.com/repos/owner/repo/contents/README.zh-CN.md",
    ).mock(return_value=httpx.Response(404, json={"message": "Not Found"}))

    # Mock PUT for new file (no existing SHA)
    route = respx.put(
        "https://api.github.com/repos/owner/repo/contents/README.zh-CN.md"
    ).mock(return_value=httpx.Response(200, json={"content": {"path": "README.zh-CN.md"}}))

    content = "# 你好世界"
    client.put_file(INSTALLATION_ID, FULL_NAME, BRANCH, "README.zh-CN.md", content, "add zh-CN translation")

    request = route.calls.last.request
    import json
    body = json.loads(request.content)
    assert body["branch"] == BRANCH
    assert body["message"] == "add zh-CN translation"
    assert body["content"] == base64.b64encode(content.encode()).decode()


@respx.mock
def test_put_file_fetches_sha_for_existing_file():
    """put_file fetches existing file SHA before update."""
    client = GitHubAppClient(app_id="1", private_key="fake", token_provider=lambda _: "ghs_test")

    # Mock GET for existing file
    respx.get(
        "https://api.github.com/repos/owner/repo/contents/README.zh-CN.md",
        params={"ref": BRANCH}
    ).mock(return_value=httpx.Response(200, json={"sha": "existing_sha_123"}))

    # Mock PUT for update
    route = respx.put(
        "https://api.github.com/repos/owner/repo/contents/README.zh-CN.md"
    ).mock(return_value=httpx.Response(200, json={"content": {"path": "README.zh-CN.md"}}))

    content = "# 更新翻译"
    client.put_file(INSTALLATION_ID, FULL_NAME, BRANCH, "README.zh-CN.md", content, "update translation")

    import json
    body = json.loads(route.calls.last.request.content)
    assert body["sha"] == "existing_sha_123"
