"""Domain models for translation tasks."""

from enum import Enum
from typing import List, Optional

from pydantic import BaseModel


class TaskStatus(str, Enum):
    """Status of a translation task."""

    QUEUED = "queued"
    RUNNING = "running"
    SUCCEEDED = "succeeded"
    FAILED = "failed"


class FileMapping(BaseModel):
    """Mapping between source and translated file paths."""

    source_path: str
    target_path: str


class Task(BaseModel):
    """Translation task input model."""

    task_id: str
    installation_id: str
    repository: str
    base_branch: str
    files: List[str]
    language: str
    status: TaskStatus = TaskStatus.QUEUED


class TaskResult(BaseModel):
    """Translation task output model."""

    status: TaskStatus
    pr_url: Optional[str] = None
    pr_number: Optional[int] = None
    mappings: Optional[List[FileMapping]] = None
    error_code: Optional[str] = None
    error_message: Optional[str] = None
