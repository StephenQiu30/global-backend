"""Tests for PublicRepositoryClient and PublicPreviewService."""

import pytest
from unittest.mock import AsyncMock, MagicMock, patch

from app.services.public_repository import (
    PublicRepositoryClient,
    PublicPreviewService,
    FilePreview,
    PublicPreviewResult,
)
from app.services.translation_provider import FakeTranslationProvider


# --- PublicRepositoryClient tests ---


class TestPublicRepositoryListMarkdownFiles:
    """Tests for listing Markdown files in a public repository."""

    @pytest.mark.asyncio
    async def test_list_markdown_files_returns_filtered_paths(self):
        """Only .md and .markdown files should be returned."""
        client = PublicRepositoryClient()
        tree_data = {
            "tree": [
                {"path": "README.md", "type": "blob"},
                {"path": "docs/guide.md", "type": "blob"},
                {"path": "image.png", "type": "blob"},
                {"path": "src/main.py", "type": "blob"},
                {"path": "CHANGELOG.markdown", "type": "blob"},
                {"path": ".gitignore", "type": "blob"},
            ]
        }
        mock_response = AsyncMock()
        mock_response.status_code = 200
        mock_response.json.return_value = tree_data
        mock_response.raise_for_status = MagicMock()

        with patch("httpx.AsyncClient.get", return_value=mock_response):
            files = await client.list_markdown_files("owner", "repo", "main")

        assert "README.md" in files
        assert "docs/guide.md" in files
        assert "CHANGELOG.markdown" in files
        assert "image.png" not in files
        assert "src/main.py" not in files

    @pytest.mark.asyncio
    async def test_list_markdown_files_excludes_excluded_dirs(self):
        """Files in .git, node_modules, etc. should be excluded."""
        client = PublicRepositoryClient()
        tree_data = {
            "tree": [
                {"path": "README.md", "type": "blob"},
                {"path": ".git/COMMIT_EDITMSG", "type": "blob"},
                {"path": "node_modules/pkg/readme.md", "type": "blob"},
                {"path": "dist/output.md", "type": "blob"},
            ]
        }
        mock_response = AsyncMock()
        mock_response.status_code = 200
        mock_response.json.return_value = tree_data
        mock_response.raise_for_status = MagicMock()

        with patch("httpx.AsyncClient.get", return_value=mock_response):
            files = await client.list_markdown_files("owner", "repo", "main")

        assert "README.md" in files
        assert len(files) == 1

    @pytest.mark.asyncio
    async def test_list_markdown_files_excludes_translated_variants(self):
        """Already-translated files (e.g. README.zh-CN.md) should be excluded."""
        client = PublicRepositoryClient()
        tree_data = {
            "tree": [
                {"path": "README.md", "type": "blob"},
                {"path": "README.zh-CN.md", "type": "blob"},
                {"path": "guide.en.md", "type": "blob"},
            ]
        }
        mock_response = AsyncMock()
        mock_response.status_code = 200
        mock_response.json.return_value = tree_data
        mock_response.raise_for_status = MagicMock()

        with patch("httpx.AsyncClient.get", return_value=mock_response):
            files = await client.list_markdown_files("owner", "repo", "main")

        assert "README.md" in files
        assert "README.zh-CN.md" not in files
        assert "guide.en.md" not in files


class TestPublicRepositoryGetFileContent:
    """Tests for reading file content from a public repository."""

    @pytest.mark.asyncio
    async def test_get_file_content_returns_decoded_text(self):
        """File content should be decoded from base64."""
        import base64

        content = "# Hello World\n\nWelcome."
        encoded = base64.b64encode(content.encode()).decode()
        client = PublicRepositoryClient()

        mock_response = AsyncMock()
        mock_response.status_code = 200
        mock_response.json.return_value = {
            "content": encoded,
            "encoding": "base64",
        }
        mock_response.raise_for_status = MagicMock()

        with patch("httpx.AsyncClient.get", return_value=mock_response):
            result = await client.get_file_content("owner", "repo", "main", "README.md")

        assert result == content

    @pytest.mark.asyncio
    async def test_get_file_content_rejects_unsafe_path(self):
        """Paths with directory traversal should be rejected."""
        client = PublicRepositoryClient()

        with pytest.raises(ValueError, match="unsafe path"):
            await client.get_file_content("owner", "repo", "main", "../../etc/passwd")

    @pytest.mark.asyncio
    async def test_get_file_content_rejects_absolute_path(self):
        """Absolute paths should be rejected."""
        client = PublicRepositoryClient()

        with pytest.raises(ValueError, match="unsafe path"):
            await client.get_file_content("owner", "repo", "main", "/etc/passwd")


class TestPublicRepositoryErrors:
    """Tests for error handling in PublicRepositoryClient."""

    @pytest.mark.asyncio
    async def test_repository_not_found_raises_value_error(self):
        """404 from GitHub should raise ValueError."""
        client = PublicRepositoryClient()

        mock_response = AsyncMock()
        mock_response.status_code = 404
        mock_response.raise_for_status.side_effect = Exception("Not Found")

        with patch("httpx.AsyncClient.get", return_value=mock_response):
            with pytest.raises(ValueError, match="not found"):
                await client.list_markdown_files("owner", "nonexistent", "main")

    @pytest.mark.asyncio
    async def test_rate_limited_raises_value_error(self):
        """403 from GitHub should raise ValueError with rate_limited."""
        client = PublicRepositoryClient()

        mock_response = AsyncMock()
        mock_response.status_code = 403
        mock_response.raise_for_status.side_effect = Exception("Forbidden")

        with patch("httpx.AsyncClient.get", return_value=mock_response):
            with pytest.raises(ValueError, match="rate_limited"):
                await client.list_markdown_files("owner", "repo", "main")

    @pytest.mark.asyncio
    async def test_rate_limited_429_raises_value_error(self):
        """429 from GitHub should also raise ValueError with rate_limited."""
        client = PublicRepositoryClient()

        mock_response = AsyncMock()
        mock_response.status_code = 429
        mock_response.raise_for_status.side_effect = Exception("Too Many Requests")

        with patch("httpx.AsyncClient.get", return_value=mock_response):
            with pytest.raises(ValueError, match="rate_limited"):
                await client.list_markdown_files("owner", "repo", "main")


class TestPublicRepositoryNoWriteMethods:
    """Tests proving PublicRepositoryClient has no write methods."""

    def test_no_create_branch_method(self):
        client = PublicRepositoryClient()
        assert not hasattr(client, "create_branch")

    def test_no_create_commit_method(self):
        client = PublicRepositoryClient()
        assert not hasattr(client, "create_commit")

    def test_no_create_pull_method(self):
        client = PublicRepositoryClient()
        assert not hasattr(client, "create_pull")

    def test_no_update_file_method(self):
        client = PublicRepositoryClient()
        assert not hasattr(client, "update_file")


# --- PublicPreviewService tests ---


class TestPublicPreviewServiceSuccess:
    """Tests for successful public preview generation."""

    @pytest.mark.asyncio
    async def test_single_file_preview(self):
        """Single file preview should return translated content."""
        mock_client = AsyncMock()
        mock_client.get_file_content.return_value = "# Hello World"
        mock_client.list_markdown_files.return_value = ["README.md"]
        provider = FakeTranslationProvider()
        service = PublicPreviewService(mock_client, provider)

        result = await service.preview(
            repository="owner/repo",
            branch="main",
            files=["README.md"],
            language="zh-CN",
        )

        assert len(result.previews) == 1
        assert result.previews[0].source_path == "README.md"
        assert result.previews[0].target_path == "README.zh-CN.md"
        assert "[zh-CN]" in result.previews[0].translated_content

    @pytest.mark.asyncio
    async def test_multiple_files_preview(self):
        """Multiple files should return multiple previews."""
        mock_client = AsyncMock()
        mock_client.get_file_content.return_value = "# Content"
        provider = FakeTranslationProvider()
        service = PublicPreviewService(mock_client, provider)

        result = await service.preview(
            repository="owner/repo",
            branch="main",
            files=["README.md", "docs/guide.md"],
            language="ja",
        )

        assert len(result.previews) == 2
        assert result.previews[0].target_path == "README.ja.md"
        assert result.previews[1].target_path == "docs/guide.ja.md"

    @pytest.mark.asyncio
    async def test_preview_result_has_no_pr_url(self):
        """Preview result must not contain pr_url or pr_number."""
        mock_client = AsyncMock()
        mock_client.get_file_content.return_value = "# Content"
        provider = FakeTranslationProvider()
        service = PublicPreviewService(mock_client, provider)

        result = await service.preview(
            repository="owner/repo",
            branch="main",
            files=["README.md"],
            language="zh-CN",
        )

        assert not hasattr(result, "pr_url") or result.pr_url is None
        assert not hasattr(result, "pr_number") or result.pr_number is None


class TestPublicPreviewServiceValidation:
    """Tests for input validation in PublicPreviewService."""

    @pytest.mark.asyncio
    async def test_rejects_unsafe_file_path(self):
        """Unsafe paths should be rejected."""
        mock_client = AsyncMock()
        provider = FakeTranslationProvider()
        service = PublicPreviewService(mock_client, provider)

        with pytest.raises(ValueError, match="unsafe"):
            await service.preview(
                repository="owner/repo",
                branch="main",
                files=["../../etc/passwd"],
                language="zh-CN",
            )

    @pytest.mark.asyncio
    async def test_rejects_non_markdown_file(self):
        """Non-Markdown files should be rejected."""
        mock_client = AsyncMock()
        provider = FakeTranslationProvider()
        service = PublicPreviewService(mock_client, provider)

        with pytest.raises(ValueError, match="not supported"):
            await service.preview(
                repository="owner/repo",
                branch="main",
                files=["image.png"],
                language="zh-CN",
            )

    @pytest.mark.asyncio
    async def test_rejects_excluded_directory(self):
        """Files in excluded directories should be rejected."""
        mock_client = AsyncMock()
        provider = FakeTranslationProvider()
        service = PublicPreviewService(mock_client, provider)

        with pytest.raises(ValueError, match="excluded"):
            await service.preview(
                repository="owner/repo",
                branch="main",
                files=[".git/config.md"],
                language="zh-CN",
            )


class TestPublicPreviewServiceErrors:
    """Tests for error handling in PublicPreviewService."""

    @pytest.mark.asyncio
    async def test_file_read_error_propagates(self):
        """File read errors should propagate."""
        mock_client = AsyncMock()
        mock_client.get_file_content.side_effect = ValueError("file not found")
        provider = FakeTranslationProvider()
        service = PublicPreviewService(mock_client, provider)

        with pytest.raises(ValueError, match="not found"):
            await service.preview(
                repository="owner/repo",
                branch="main",
                files=["missing.md"],
                language="zh-CN",
            )


class TestPublicPreviewServiceNoWriteOperations:
    """Tests proving PublicPreviewService does not call write methods."""

    @pytest.mark.asyncio
    async def test_no_write_methods_called(self):
        """Preview should not call any write method on the client."""
        mock_client = AsyncMock()
        mock_client.get_file_content.return_value = "# Content"
        provider = FakeTranslationProvider()
        service = PublicPreviewService(mock_client, provider)

        await service.preview(
            repository="owner/repo",
            branch="main",
            files=["README.md"],
            language="zh-CN",
        )

        # Verify no write methods were called
        mock_client.create_branch.assert_not_called()
        mock_client.create_commit.assert_not_called()
        mock_client.create_pull.assert_not_called()
        mock_client.update_file.assert_not_called()
