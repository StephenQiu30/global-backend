"""Repository for translation task persistence."""

from sqlalchemy import select
from sqlalchemy.ext.asyncio import AsyncSession

from app.models.translation_file_model import TranslationFileModel
from app.models.translation_task_model import TranslationTaskModel


class TranslationTaskRepository:
    """Data access for translation tasks and file previews."""

    def __init__(self, session: AsyncSession) -> None:
        self._session = session

    async def create_task(
        self,
        task_id: str,
        installation_id: str,
        repository: str,
        base_branch: str,
        source_files: list[str],
        language: str,
    ) -> TranslationTaskModel:
        """Create a new queued translation task."""
        model = TranslationTaskModel(
            task_id=task_id,
            installation_id=installation_id,
            repository=repository,
            base_branch=base_branch,
            source_files=source_files,
            language=language,
            status="queued",
        )
        self._session.add(model)
        await self._session.commit()
        await self._session.refresh(model)
        return model

    async def get_by_task_id(self, task_id: str) -> TranslationTaskModel | None:
        """Retrieve a task by its task_id."""
        stmt = select(TranslationTaskModel).where(
            TranslationTaskModel.task_id == task_id
        )
        result = await self._session.execute(stmt)
        return result.scalar_one_or_none()

    async def update_status(
        self,
        task_id: str,
        status: str,
        *,
        pr_url: str | None = None,
        pr_number: int | None = None,
        file_mappings: list[dict] | None = None,
        error_code: str | None = None,
        error_message: str | None = None,
    ) -> None:
        """Update task status and result fields."""
        task = await self.get_by_task_id(task_id)
        if task is None:
            return
        task.status = status
        if pr_url is not None:
            task.pr_url = pr_url
        if pr_number is not None:
            task.pr_number = pr_number
        if file_mappings is not None:
            task.file_mappings = file_mappings
        if error_code is not None:
            task.error_code = error_code
        if error_message is not None:
            task.error_message = error_message
        await self._session.commit()

    async def get_file_previews(
        self, task_id: str
    ) -> list[TranslationFileModel]:
        """Retrieve file preview metadata for a task."""
        stmt = select(TranslationFileModel).where(
            TranslationFileModel.task_id == task_id
        )
        result = await self._session.execute(stmt)
        return list(result.scalars().all())

    async def create_file_previews(
        self,
        task_id: str,
        file_mappings: list[dict],
    ) -> list[TranslationFileModel]:
        """Create file preview records from task file mappings."""
        models = []
        for mapping in file_mappings:
            model = TranslationFileModel(
                task_id=task_id,
                source_path=mapping["source_path"],
                target_path=mapping["target_path"],
                status="translated",
            )
            self._session.add(model)
            models.append(model)
        await self._session.commit()
        return models
