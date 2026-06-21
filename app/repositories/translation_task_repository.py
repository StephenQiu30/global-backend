"""Repository for translation task persistence."""

import json
from dataclasses import dataclass
from typing import List, Optional

from sqlalchemy import select, update
from sqlalchemy.ext.asyncio import AsyncSession

from app.domain.task import FileMapping, TaskStatus
from app.models.translation_task import TranslationTaskModel


@dataclass
class TranslationTaskData:
    """Domain data for a translation task (VO-friendly)."""

    task_id: str
    installation_id: str
    repository: str
    base_branch: str
    files: List[str]
    language: str
    status: TaskStatus
    pr_url: Optional[str] = None
    pr_number: Optional[int] = None
    mappings: Optional[List[FileMapping]] = None
    error_code: Optional[str] = None
    error_message: Optional[str] = None


# Safe error codes that can be stored
_SAFE_ERROR_CODES = {"file_read_error", "translation_error", "unknown_error"}

# Default safe error message for unsafe input
_DEFAULT_SAFE_ERROR_MESSAGE = "An unexpected error occurred"


def _sanitize_error(code: str | None, message: str | None) -> tuple[str | None, str | None]:
    """Sanitize error info to ensure only safe data is stored.

    Args:
        code: Error code to sanitize
        message: Error message to sanitize

    Returns:
        Tuple of (safe_code, safe_message)
    """
    if code is None or message is None:
        return None, None

    # Only allow known safe error codes
    safe_code = code if code in _SAFE_ERROR_CODES else "unknown_error"

    # Sanitize message: remove potential sensitive info
    safe_message = message
    unsafe_patterns = [
        "traceback", "stack trace", "ghp_", "gho_", "token",
        "secret", "password", "private_key", "-----BEGIN",
    ]
    message_lower = message.lower()
    for pattern in unsafe_patterns:
        if pattern in message_lower:
            safe_message = _DEFAULT_SAFE_ERROR_MESSAGE
            break

    # Truncate if too long
    if len(safe_message) > 500:
        safe_message = safe_message[:497] + "..."

    return safe_code, safe_message


def _model_to_data(model: TranslationTaskModel) -> TranslationTaskData:
    """Convert ORM model to domain data.

    Args:
        model: ORM model instance

    Returns:
        Domain data instance
    """
    files = json.loads(model.files) if model.files else []
    mappings = None
    if model.mappings:
        mappings = json.loads(model.mappings)

    return TranslationTaskData(
        task_id=model.task_id,
        installation_id=model.installation_id,
        repository=model.repository,
        base_branch=model.base_branch,
        files=files,
        language=model.language,
        status=TaskStatus(model.status),
        pr_url=model.pr_url,
        pr_number=model.pr_number,
        mappings=mappings,
        error_code=model.error_code,
        error_message=model.error_message,
    )


class TranslationTaskRepository:
    """Repository for translation task persistence.

    Args:
        session: Async SQLAlchemy session
    """

    def __init__(self, session: AsyncSession) -> None:
        self._session = session

    async def create(
        self,
        installation_id: str,
        repository: str,
        base_branch: str,
        files: List[str],
        language: str,
    ) -> TranslationTaskData:
        """Create a new translation task with queued status.

        Args:
            installation_id: GitHub App installation ID
            repository: Repository full name (owner/repo)
            base_branch: Base branch name
            files: List of file paths to translate
            language: Target language code

        Returns:
            Created task data
        """
        model = TranslationTaskModel(
            installation_id=installation_id,
            repository=repository,
            base_branch=base_branch,
            files=json.dumps(files),
            language=language,
            status=TaskStatus.QUEUED.value,
        )
        self._session.add(model)
        await self._session.flush()
        await self._session.refresh(model)
        return _model_to_data(model)

    async def get_by_id(self, task_id: str) -> Optional[TranslationTaskData]:
        """Get a task by its ID.

        Args:
            task_id: Task ID to look up

        Returns:
            Task data if found, None otherwise
        """
        stmt = select(TranslationTaskModel).where(
            TranslationTaskModel.task_id == task_id
        )
        result = await self._session.execute(stmt)
        model = result.scalar_one_or_none()
        if model is None:
            return None
        return _model_to_data(model)

    async def update_status(
        self,
        task_id: str,
        status: TaskStatus,
        *,
        pr_url: Optional[str] = None,
        pr_number: Optional[int] = None,
        mappings: Optional[List[FileMapping]] = None,
        error_code: Optional[str] = None,
        error_message: Optional[str] = None,
    ) -> Optional[TranslationTaskData]:
        """Update task status and optional result/error info.

        Args:
            task_id: Task ID to update
            status: New status
            pr_url: PR URL (for succeeded tasks)
            pr_number: PR number (for succeeded tasks)
            mappings: File mappings (for succeeded tasks)
            error_code: Error code (for failed tasks)
            error_message: Error message (for failed tasks)

        Returns:
            Updated task data if found, None otherwise
        """
        # Sanitize error info for failed tasks
        if status == TaskStatus.FAILED:
            error_code, error_message = _sanitize_error(error_code, error_message)

        # Build update values
        values = {"status": status.value}
        if pr_url is not None:
            values["pr_url"] = pr_url
        if pr_number is not None:
            values["pr_number"] = pr_number
        if mappings is not None:
            # Handle both dict and FileMapping inputs
            mappings_data = []
            for m in mappings:
                if isinstance(m, dict):
                    mappings_data.append(m)
                else:
                    mappings_data.append(m.model_dump())
            values["mappings"] = json.dumps(mappings_data)
        if error_code is not None:
            values["error_code"] = error_code
        if error_message is not None:
            values["error_message"] = error_message

        stmt = (
            update(TranslationTaskModel)
            .where(TranslationTaskModel.task_id == task_id)
            .values(**values)
            .returning(TranslationTaskModel)
        )
        result = await self._session.execute(stmt)
        model = result.scalar_one_or_none()
        if model is None:
            return None
        await self._session.flush()
        return _model_to_data(model)

    async def get_file_previews(self, task_id: str) -> List[dict]:
        """Get file preview mappings for a succeeded task.

        Args:
            task_id: Task ID to get previews for

        Returns:
            List of file mapping dicts (empty if task not succeeded)
        """
        task = await self.get_by_id(task_id)
        if task is None or task.status != TaskStatus.SUCCEEDED:
            return []
        return task.mappings or []
