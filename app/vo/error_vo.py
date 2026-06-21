"""Shared API error response value objects."""

from pydantic import BaseModel


class SimpleErrorVO(BaseModel):
    """Error response with a single error code."""

    error: str


class MessageErrorVO(BaseModel):
    """Error response with code and message."""

    error: str
    message: str


class RetryableErrorVO(BaseModel):
    """Error response with retry hint."""

    error: str
    message: str
    retryable: bool = False


class CodeMessageErrorVO(BaseModel):
    """Error response using error_code field name."""

    error_code: str
    message: str
