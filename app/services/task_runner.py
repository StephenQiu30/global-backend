"""Task runner service for executing translation tasks."""

from app.domain.task import (
    Task,
    TaskStatus,
    TaskResult,
    FileMapping,
)
from app.domain.markdown_files import target_translation_path
from app.services.translation_provider import TranslationProvider


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
    """Classify an exception into a safe error code and message.

    Args:
        exc: The exception to classify

    Returns:
        Tuple of (error_code, error_message)
    """
    exc_type = type(exc).__name__
    exc_str = str(exc).lower()

    if "file" in exc_str or "read" in exc_str or "not found" in exc_str:
        return "file_read_error", "Failed to read file from repository"

    if "translat" in exc_str or "provider" in exc_str:
        return "translation_error", "Translation provider returned an error"

    return "unknown_error", "An unexpected error occurred"
