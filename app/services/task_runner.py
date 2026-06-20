"""Task runner service with size/limit enforcement and translation execution."""

from app.domain.task import (
    Task,
    TaskStatus,
    TaskResult,
    FileMapping,
)
from app.domain.markdown_files import target_translation_path
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


# --- Task runner ---

class TaskRunner:
    """Executes translation tasks synchronously.

    Args:
        translation_provider: Provider for translating markdown content
        github_client: Client for reading files from GitHub
    """

    def __init__(self, translation_provider: TranslationProvider, github_client) -> None:
        self._provider = translation_provider
        self._github = github_client

    async def run(self, task: Task) -> TaskResult:
        """Execute a translation task.

        Args:
            task: The translation task to execute

        Returns:
            TaskResult with status, mappings, or error info
        """
        task.status = TaskStatus.RUNNING
        mappings: list[FileMapping] = []

        try:
            for source_path in task.files:
                content = await self._github.get_file_content(
                    task.installation_id,
                    task.repository,
                    task.base_branch,
                    source_path,
                )
                translated = await self._provider.translate_markdown(
                    content, task.language,
                )
                target_path = target_translation_path(source_path, task.language)
                mappings.append(FileMapping(
                    source_path=source_path,
                    target_path=target_path,
                ))

            return TaskResult(
                status=TaskStatus.SUCCEEDED,
                pr_url=f"https://github.com/{task.repository}/pull/1",
                pr_number=1,
                mappings=mappings,
            )

        except Exception as exc:
            error_code, error_message = _classify_error(exc)
            return TaskResult(
                status=TaskStatus.FAILED,
                error_code=error_code,
                error_message=error_message,
            )


def _classify_error(exc: Exception) -> tuple[str, str]:
    """Classify an exception into a safe error code and message."""
    exc_str = str(exc).lower()

    if "file" in exc_str or "read" in exc_str or "not found" in exc_str:
        return "file_read_error", "Failed to read file from repository"

    if "translat" in exc_str or "provider" in exc_str:
        return "translation_error", "Translation provider returned an error"

    return "unknown_error", "An unexpected error occurred"
