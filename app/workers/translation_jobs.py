import logging

logger = logging.getLogger(__name__)


def run_translation_task(task_id: str) -> None:
    """Worker job entrypoint for translation tasks.

    Loads a task by ID and delegates to application service execution.
    Currently a stub implementation; will delegate to
    TranslationTaskService when the application service layer is built.
    """
    logger.info("Processing translation task %s", task_id)
