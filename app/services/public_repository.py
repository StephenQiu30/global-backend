"""Public repository read-only client and preview service."""

import base64

import httpx
from pydantic import BaseModel

from app.core.exceptions import AppException
from app.core.response import ErrorCode
from app.domain.markdown_files import (
    is_supported_markdown_path,
    is_safe_path,
    is_in_excluded_directory,
    is_translated_variant,
    target_translation_path,
    MAX_FILE_COUNT,
    MAX_TOTAL_SIZE,
)
from app.services.translation_provider import TranslationProvider


class FilePreview(BaseModel):
    """Preview of a single translated file."""

    source_path: str
    target_path: str
    translated_content: str


class PublicPreviewResult(BaseModel):
    """Result of a public preview request."""

    previews: list[FilePreview]


class PublicRepositoryClient:
    """Read-only client for public GitHub repositories using unauthenticated HTTP.

    Uses GitHub REST API directly via httpx. No authentication, no write methods.
    """

    _GITHUB_API = "https://api.github.com"

    async def list_markdown_files(
        self, owner: str, repo: str, branch: str
    ) -> list[str]:
        """List Markdown files in a public repository.

        Args:
            owner: Repository owner
            repo: Repository name
            branch: Branch name

        Returns:
            List of Markdown file paths

        Raises:
            ValueError: If repository not found or rate limited
        """
        url = f"{self._GITHUB_API}/repos/{owner}/{repo}/git/trees/{branch}"
        params = {"recursive": "1"}

        status, data = await self._get(url, params)

        tree = data.get("tree", [])
        files = []
        for item in tree:
            if item.get("type") != "blob":
                continue
            path = item.get("path", "")
            if not is_supported_markdown_path(path):
                continue
            if is_translated_variant(path):
                continue
            if is_in_excluded_directory(path):
                continue
            if not is_safe_path(path):
                continue
            files.append(path)

        return files

    async def get_file_content(
        self, owner: str, repo: str, branch: str, path: str
    ) -> str:
        """Read file content from a public repository.

        Args:
            owner: Repository owner
            repo: Repository name
            branch: Branch name
            path: File path

        Returns:
            File content as string

        Raises:
            AppException: If path is unsafe or file not found
        """
        if not is_safe_path(path):
            raise AppException(
                code=ErrorCode.VALIDATION_ERROR,
                message=f"unsafe path: {path}",
                http_status=400,
            )

        url = f"{self._GITHUB_API}/repos/{owner}/{repo}/contents/{path}"
        params = {"ref": branch}

        _, data = await self._get(url, params)

        content = data.get("content", "")
        encoding = data.get("encoding", "base64")

        if encoding == "base64":
            return base64.b64decode(content).decode("utf-8")

        return content

    async def _get(self, url: str, params: dict | None = None) -> tuple[int, dict]:
        """Make a GET request to GitHub API.

        Returns:
            Tuple of (status_code, response_json)

        Raises:
            AppException: On 404 (not found) or 403/429 (rate limited)
        """
        async with httpx.AsyncClient() as client:
            response = await client.get(url, params=params, timeout=10.0)

            if response.status_code == 404:
                raise AppException(
                    code=ErrorCode.REPOSITORY_NOT_FOUND,
                    message="repository not found",
                    http_status=404,
                )

            if response.status_code in (403, 429):
                raise AppException(
                    code=ErrorCode.GITHUB_RATE_LIMITED,
                    message="GitHub API rate limit exceeded",
                    http_status=429,
                )

            if response.status_code >= 400:
                raise AppException(
                    code=ErrorCode.GITHUB_API_ERROR,
                    message=f"GitHub API error: {response.status_code}",
                    http_status=502,
                )

            return response.status_code, response.json()


class PublicPreviewService:
    """Service for generating read-only translation previews of public repositories.

    Args:
        github_client: PublicRepositoryClient for reading files
        translation_provider: TranslationProvider for translating content
    """

    def __init__(
        self,
        github_client: PublicRepositoryClient,
        translation_provider: TranslationProvider,
    ) -> None:
        self._github = github_client
        self._provider = translation_provider

    async def preview(
        self,
        repository: str,
        branch: str,
        files: list[str],
        language: str,
    ) -> PublicPreviewResult:
        """Generate translation previews for public repository files.

        Args:
            repository: Repository full name (owner/repo)
            branch: Branch name
            files: List of file paths to preview
            language: Target language code

        Returns:
            PublicPreviewResult with translated previews

        Raises:
            AppException: For invalid inputs or not-found errors
        """
        # Validate file count
        if len(files) > MAX_FILE_COUNT:
            raise AppException(
                code=ErrorCode.VALIDATION_ERROR,
                message=f"too many files: {len(files)} exceeds limit of {MAX_FILE_COUNT}",
                http_status=422,
            )

        # Validate inputs
        for path in files:
            if not is_safe_path(path):
                raise AppException(
                    code=ErrorCode.VALIDATION_ERROR,
                    message=f"unsafe path: {path}",
                    http_status=400,
                )
            if not is_supported_markdown_path(path):
                raise AppException(
                    code=ErrorCode.VALIDATION_ERROR,
                    message=f"file not supported: {path}",
                    http_status=400,
                )
            if is_in_excluded_directory(path):
                raise AppException(
                    code=ErrorCode.VALIDATION_ERROR,
                    message=f"path in excluded directory: {path}",
                    http_status=400,
                )

        owner, repo = repository.split("/", 1)
        previews: list[FilePreview] = []
        total_size = 0

        for source_path in files:
            content = await self._github.get_file_content(
                owner, repo, branch, source_path,
            )
            total_size += len(content.encode("utf-8"))
            if total_size > MAX_TOTAL_SIZE:
                raise AppException(
                    code=ErrorCode.VALIDATION_ERROR,
                    message=f"total content size exceeds limit of {MAX_TOTAL_SIZE} bytes",
                    http_status=422,
                )
            try:
                translated = await self._provider.translate_markdown(
                    content, language,
                )
            except RuntimeError:
                raise AppException(
                    code=ErrorCode.TRANSLATION_ERROR,
                    message="Translation provider returned an error",
                    http_status=500,
                )
            target_path = target_translation_path(source_path, language)
            previews.append(FilePreview(
                source_path=source_path,
                target_path=target_path,
                translated_content=translated,
            ))

        return PublicPreviewResult(previews=previews)
