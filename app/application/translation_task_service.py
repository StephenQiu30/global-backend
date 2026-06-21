"""Application service for translation task operations."""

from pydantic import BaseModel, Field

from app.domain.languages import validate_language_code
from app.domain.task import Task, TaskResult, TaskStatus
from app.services.task_runner import TaskRunner


class UnsupportedLanguageError(Exception):
    """Raised when a language code is not supported."""

    def __init__(self, language: str) -> None:
        self.language = language
        super().__init__(f"Language '{language}' is not supported")


class TranslationTaskRequest(BaseModel):
    """Request DTO for creating a translation task."""

    installation_id: str = Field(..., min_length=1)
    repository: str = Field(..., min_length=1)
    base_branch: str = Field(..., min_length=1)
    files: list[str] = Field(..., min_length=1)
    language: str = Field(..., min_length=1)


class TranslationTaskService:
    """Service for translation task creation and execution.

    Args:
        task_runner: Task runner for executing translation tasks.
    """

    def __init__(self, task_runner: TaskRunner) -> None:
        self._runner = task_runner

    async def create_task(self, request: TranslationTaskRequest) -> TaskResult:
        """Create and execute a translation task.

        Args:
            request: Translation task request DTO.

        Returns:
            TaskResult with status, PR info, or error details.

        Raises:
            UnsupportedLanguageError: If language code is not supported.
        """
        if not validate_language_code(request.language):
            raise UnsupportedLanguageError(request.language)

        task = Task(
            task_id="generated",
            installation_id=request.installation_id,
            repository=request.repository,
            base_branch=request.base_branch,
            files=request.files,
            language=request.language,
        )
        return await self._runner.run(task)
