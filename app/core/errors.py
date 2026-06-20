"""Application error types for safe error mapping."""


class AppError(Exception):
    """Structured application error with code and retryability."""

    def __init__(self, code: str, message: str, *, retryable: bool = False):
        self.code = code
        self.message = message
        self.retryable = retryable
        super().__init__(message)
