"""Task runner service with size and limit enforcement."""

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
