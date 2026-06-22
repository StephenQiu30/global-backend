"""Application service for translation task lifecycle."""

from app.core.exceptions import AppException
from app.core.response import ErrorCode
from app.domain.task import TaskStatus
from app.domain.languages import validate_language_code
from app.repositories.translation_task_repository import TranslationTaskRepository
from app.queues.translation_task_queue import TranslationTaskQueue
from app.vo.translation_task_vo import (
    FilePreviewVO,
    TranslationTaskCreateVO,
    TranslationTaskStatusVO,
)


class TranslationTaskService:
    """Orchestrates translation task creation, status, and file previews."""

    def __init__(
        self,
        repository: TranslationTaskRepository,
        queue: TranslationTaskQueue,
    ) -> None:
        self._repo = repository
        self._queue = queue

    async def create_task(
        self,
        installation_id: str,
        repository: str,
        base_branch: str,
        files: list[str],
        language: str,
    ) -> TranslationTaskCreateVO:
        """Create a queued translation task and enqueue it.

        Args:
            installation_id: GitHub App installation ID.
            repository: Repository full name (owner/repo).
            base_branch: Base branch name.
            files: List of file paths to translate.
            language: Target language code.

        Returns:
            TranslationTaskCreateVO with task_id and queued status.

        Raises:
            AppException: If language code is not supported.
        """
        if not validate_language_code(language):
            raise AppException(
                code=ErrorCode.UNSUPPORTED_LANGUAGE,
                message=f"Language '{language}' is not supported",
                http_status=400,
            )

        task = await self._repo.create(
            installation_id=installation_id,
            repository=repository,
            base_branch=base_branch,
            files=files,
            language=language,
        )
        self._queue.enqueue(task.task_id)
        return TranslationTaskCreateVO(task_id=task.task_id, status=task.status.value)

    async def get_task_status(self, task_id: str) -> TranslationTaskStatusVO | None:
        """Retrieve persisted task status by task_id.

        Args:
            task_id: The translation task identifier.

        Returns:
            TranslationTaskStatusVO if found, None otherwise.
        """
        task = await self._repo.get_by_id(task_id)
        if task is None:
            return None

        return TranslationTaskStatusVO(
            task_id=task.task_id,
            status=task.status.value,
            repository=task.repository,
            language=task.language,
            pr_url=task.pr_url,
            pr_number=task.pr_number,
            file_mappings=task.mappings,
            error_code=task.error_code,
            error_message=task.error_message,
            created_at="",
            updated_at="",
        )

    async def get_file_previews(self, task_id: str) -> list[FilePreviewVO] | None:
        """Retrieve file preview metadata for a task.

        Args:
            task_id: The translation task identifier.

        Returns:
            List of FilePreviewVO if task exists, None if task not found.
        """
        task = await self._repo.get_by_id(task_id)
        if task is None:
            return None

        previews = await self._repo.get_file_previews(task_id)
        return [
            FilePreviewVO(
                source_path=p["source_path"],
                target_path=p["target_path"],
                status="translated",
            )
            for p in previews
        ]
