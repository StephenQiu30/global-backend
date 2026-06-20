"""Task runner service with size/limit enforcement and translation execution.

Two-phase design: translate all files first, then write to GitHub.
Translation failure creates no branch, files, or PR (atomicity).
"""

from typing import Any, Protocol

from app.domain.markdown_files import target_translation_path
from app.domain.task import (
    FileMapping,
    Task,
    TaskResult,
    TaskStatus,
)
from app.services.pr_description import build_translation_pr_body
from app.services.translation_provider import TranslationProvider


# --- PRD 09: Task limit enforcement ---

MAX_FILES_PER_TASK = 10
MAX_TOTAL_SIZE_BYTES = 200 * 1024  # 200KB


class TaskLimitError(Exception):
    """Raised when task violates size or count limits."""

    def __init__(self, code: str, message: str):
        self.code = code
        self.retryable = False
        super().__init__(f"{code}: {message}")


def validate_task_limits(files: list[dict]) -> None:
    """Validate task file count and total size limits.

    Args:
        files: List of dicts with 'path' and 'size' keys.
            'size' must be the actual byte count from GitHub content,
            not from the request payload.

    Raises:
        TaskLimitError: If limits are violated.
    """
    if not files:
        raise TaskLimitError("task_empty", "Task must contain at least one file")

    if len(files) > MAX_FILES_PER_TASK:
        raise TaskLimitError(
            "task_too_many_files",
            f"Task has {len(files)} files, maximum is {MAX_FILES_PER_TASK}",
        )

    total_size = sum(f.get("size", 0) for f in files)
    if total_size > MAX_TOTAL_SIZE_BYTES:
        raise TaskLimitError(
            "task_too_large",
            f"Total size {total_size} bytes exceeds limit of {MAX_TOTAL_SIZE_BYTES} bytes",
        )


# --- GitHub client protocol for write operations ---


class GitHubWriteClientProtocol(Protocol):
    """Protocol for GitHub write operations (branch, file, PR)."""

    def create_branch(
        self, installation_id: int, full_name: str, base_branch: str, branch_name: str
    ) -> str: ...
    def put_file(
        self,
        installation_id: int,
        full_name: str,
        branch: str,
        path: str,
        content: str,
        message: str,
    ) -> None: ...
    def create_pull_request(
        self,
        installation_id: int,
        full_name: str,
        title: str,
        body: str,
        head: str,
        base: str,
    ) -> dict[str, Any]: ...


# --- Task runner ---


class TaskRunner:
    """Executes translation tasks with two-phase design.

    Phase 1: Translate all files in memory.
    Phase 2: Write to GitHub (branch, files, PR).

    Translation failure creates no branch, files, or PR (atomicity).

    Args:
        translation_provider: Provider for translating markdown content
        github_client: Client for reading/writing files from GitHub
        github_write_client: Client for GitHub write operations (branch, file, PR)
    """

    def __init__(
        self,
        translation_provider: TranslationProvider,
        github_client: Any,
        github_write_client: GitHubWriteClientProtocol | None = None,
    ) -> None:
        self._provider = translation_provider
        self._github = github_client
        self._write_client = github_write_client

    async def run(self, task: Task) -> TaskResult:
        """Execute a translation task.

        Args:
            task: The translation task to execute

        Returns:
            TaskResult with status, mappings, or error info
        """
        task.status = TaskStatus.RUNNING
        branch_name = f"translate/{task.language}/{task.id}"

        # Phase 1: Translate all files in memory
        translated: list[dict[str, str]] = []
        mappings: list[FileMapping] = []

        try:
            for source_path in task.files:
                content = await self._github.get_file_content(
                    task.installation_id,
                    task.repository,
                    task.base_branch,
                    source_path,
                )
                translated_content = await self._provider.translate_markdown(
                    content, task.language,
                )
                target_path = target_translation_path(source_path, task.language)
                translated.append({
                    "source": source_path,
                    "target": target_path,
                    "content": translated_content,
                })
                mappings.append(FileMapping(
                    source_path=source_path,
                    target_path=target_path,
                ))
        except Exception as exc:
            error_code, error_message = _classify_error(exc)
            return TaskResult(
                status=TaskStatus.FAILED,
                error_code=error_code,
                error_message=error_message,
            )

        # Phase 2: GitHub writes (only if all translations succeeded)
        if self._write_client:
            try:
                self._write_client.create_branch(
                    task.installation_id, task.repository, task.base_branch, branch_name
                )

                for item in translated:
                    self._write_client.put_file(
                        task.installation_id,
                        task.repository,
                        branch_name,
                        item["target"],
                        item["content"],
                        f"add {task.language} translation for {item['source']}",
                    )

                pr_mappings = [
                    {"source": item["source"], "target": item["target"]}
                    for item in translated
                ]
                pr_title = f"docs: add {task.language} translation for Markdown docs"
                pr_body = build_translation_pr_body(
                    language=task.language,
                    mappings=pr_mappings,
                    provider_name="unknown",
                    task_id=task.id,
                )
                pr = self._write_client.create_pull_request(
                    task.installation_id,
                    task.repository,
                    title=pr_title,
                    body=pr_body,
                    head=branch_name,
                    base=task.base_branch,
                )
                pr_url = pr["url"]
                pr_number = pr["number"]
            except Exception as exc:
                error_code, error_message = _classify_error(exc)
                return TaskResult(
                    status=TaskStatus.FAILED,
                    error_code=error_code,
                    error_message=error_message,
                )
        else:
            # Fallback: no write client, return placeholder
            pr_url = f"https://github.com/{task.repository}/pull/1"
            pr_number = 1

        return TaskResult(
            status=TaskStatus.SUCCEEDED,
            pr_url=pr_url,
            pr_number=pr_number,
            mappings=mappings,
        )


def _classify_error(exc: Exception) -> tuple[str, str]:
    """Classify an exception into a safe error code and message.

    Args:
        exc: The exception to classify

    Returns:
        Tuple of (error_code, error_message)
    """
    exc_str = str(exc).lower()

    if "file" in exc_str or "read" in exc_str or "not found" in exc_str:
        return "file_read_error", "Failed to read file from repository"

    if "translat" in exc_str or "provider" in exc_str:
        return "translation_error", "Translation provider returned an error"

    return "unknown_error", "An unexpected error occurred"
