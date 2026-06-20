"""Tests for task API error mapping."""

import pytest

from fastapi import HTTPException

from app.api.tasks import map_error_to_response
from app.core.errors import AppError


class TestMapAppError:
    """Test map_error_to_response with known AppError codes."""

    def test_github_permission_denied(self):
        """GIVEN AppError github_permission_denied THEN returns 403."""
        err = AppError(code="github_permission_denied", message="GitHub App lacks repository access")
        exc = map_error_to_response(err)
        assert isinstance(exc, HTTPException)
        assert exc.status_code == 403
        assert exc.detail["error"] == "github_permission_denied"
        assert exc.detail["message"] == "GitHub App lacks repository access"
        assert exc.detail["retryable"] is False

    def test_github_rate_limited(self):
        """GIVEN AppError github_rate_limited with retryable=True THEN returns 429."""
        err = AppError(code="github_rate_limited", message="Rate limit exceeded", retryable=True)
        exc = map_error_to_response(err)
        assert isinstance(exc, HTTPException)
        assert exc.status_code == 429
        assert exc.detail["error"] == "github_rate_limited"
        assert exc.detail["retryable"] is True

    def test_model_timeout(self):
        """GIVEN AppError model_timeout with retryable=True THEN returns 504."""
        err = AppError(code="model_timeout", message="LLM provider timed out", retryable=True)
        exc = map_error_to_response(err)
        assert isinstance(exc, HTTPException)
        assert exc.status_code == 504
        assert exc.detail["error"] == "model_timeout"
        assert exc.detail["retryable"] is True

    def test_model_rate_limited(self):
        """GIVEN AppError model_rate_limited with retryable=True THEN returns 429."""
        err = AppError(code="model_rate_limited", message="Rate limit exceeded", retryable=True)
        exc = map_error_to_response(err)
        assert isinstance(exc, HTTPException)
        assert exc.status_code == 429
        assert exc.detail["retryable"] is True

    def test_translation_failed(self):
        """GIVEN AppError translation_failed THEN returns 500."""
        err = AppError(code="translation_failed", message="Translation process failed")
        exc = map_error_to_response(err)
        assert isinstance(exc, HTTPException)
        assert exc.status_code == 500
        assert exc.detail["error"] == "translation_failed"
        assert exc.detail["retryable"] is False


class TestMapUnknownAppError:
    """Test map_error_to_response with unknown AppError codes."""

    def test_unknown_code_defaults_to_500(self):
        """GIVEN AppError with unknown code THEN returns 500 with internal_error."""
        err = AppError(code="something_new", message="New error type")
        exc = map_error_to_response(err)
        assert isinstance(exc, HTTPException)
        assert exc.status_code == 500
        assert exc.detail["error"] == "internal_error"
        assert exc.detail["message"] == "An unexpected error occurred"
        assert exc.detail["retryable"] is False


class TestMapUnhandledException:
    """Test map_error_to_response with unhandled exceptions."""

    def test_generic_exception_returns_500(self):
        """GIVEN generic Exception THEN returns 500 with safe message."""
        err = ValueError("secret token abc123 leaked in message")
        exc = map_error_to_response(err)
        assert isinstance(exc, HTTPException)
        assert exc.status_code == 500
        assert exc.detail["error"] == "internal_error"
        assert exc.detail["message"] == "An unexpected error occurred"
        assert exc.detail["retryable"] is False

    def test_runtime_error_returns_500(self):
        """GIVEN RuntimeError THEN returns 500 with safe message."""
        err = RuntimeError("stack trace and secret info here")
        exc = map_error_to_response(err)
        assert isinstance(exc, HTTPException)
        assert exc.status_code == 500
        assert exc.detail["error"] == "internal_error"


class TestNoSecretLeakage:
    """Test that API error responses never leak secrets."""

    def test_no_token_in_response(self):
        """GIVEN Exception with token in message THEN response has no token."""
        err = Exception("Authorization failed: token ghp_abc123secret")
        exc = map_error_to_response(err)
        detail_str = str(exc.detail)
        assert "ghp_abc123secret" not in detail_str
        assert "token" not in detail_str

    def test_no_stack_trace_in_response(self):
        """GIVEN Exception with stack info THEN response has no stack."""
        err = Exception("Traceback (most recent call last): File '/app/secret.py'")
        exc = map_error_to_response(err)
        detail_str = str(exc.detail)
        assert "Traceback" not in detail_str
        assert "/app/secret.py" not in detail_str

    def test_no_secret_keyword_in_response(self):
        """GIVEN Exception with 'secret' in message THEN response has no secret."""
        err = Exception("Database password: secret123")
        exc = map_error_to_response(err)
        detail_str = str(exc.detail)
        assert "secret123" not in detail_str
        assert "password" not in detail_str

    def test_response_has_required_fields(self):
        """GIVEN any error response THEN it has error, message, retryable fields."""
        err = AppError(code="test", message="test msg")
        exc = map_error_to_response(err)
        assert "error" in exc.detail
        assert "message" in exc.detail
        assert "retryable" in exc.detail
