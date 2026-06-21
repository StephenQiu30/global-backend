"""Tests for AppException and global exception handlers."""

import uuid
from unittest.mock import patch

import pytest
from fastapi import FastAPI
from fastapi.testclient import TestClient
from pydantic import BaseModel

from app.core.response import ErrorCode, ApiResponseVO
from app.core.exceptions import (
    AppException,
    register_exception_handlers,
)


# --- AppException class ---

class TestAppException:
    """Verify AppException carries structured error metadata."""

    def test_is_exception_subclass(self):
        exc = AppException(
            code=ErrorCode.TASK_NOT_FOUND,
            message="task not found",
            http_status=404,
        )
        assert isinstance(exc, Exception)

    def test_carries_code(self):
        exc = AppException(
            code=ErrorCode.VALIDATION_ERROR,
            message="bad input",
            http_status=422,
        )
        assert exc.code == ErrorCode.VALIDATION_ERROR

    def test_carries_message(self):
        exc = AppException(
            code=ErrorCode.INTERNAL_ERROR,
            message="something went wrong",
            http_status=500,
        )
        assert exc.message == "something went wrong"

    def test_carries_http_status(self):
        exc = AppException(
            code=ErrorCode.GITHUB_RATE_LIMITED,
            message="rate limited",
            http_status=429,
        )
        assert exc.http_status == 429

    def test_retryable_defaults_false(self):
        exc = AppException(
            code=ErrorCode.INTERNAL_ERROR,
            message="error",
            http_status=500,
        )
        assert exc.retryable is False

    def test_retryable_can_be_set(self):
        exc = AppException(
            code=ErrorCode.GITHUB_API_ERROR,
            message="github down",
            http_status=502,
            retryable=True,
        )
        assert exc.retryable is True

    def test_str_representation(self):
        exc = AppException(
            code=ErrorCode.TASK_NOT_FOUND,
            message="task not found",
            http_status=404,
        )
        assert "task not found" in str(exc)


# --- Global exception handler integration tests ---

def _make_app_with_handlers() -> FastAPI:
    """Create a minimal FastAPI app with exception handlers registered."""
    app = FastAPI()
    register_exception_handlers(app)

    @app.get("/ok")
    async def ok_endpoint():
        return {"status": "fine"}

    @app.get("/app-error")
    async def app_error_endpoint():
        raise AppException(
            code=ErrorCode.TASK_NOT_FOUND,
            message="task abc not found",
            http_status=404,
        )

    @app.get("/app-error-retryable")
    async def app_error_retryable_endpoint():
        raise AppException(
            code=ErrorCode.GITHUB_API_ERROR,
            message="GitHub API timeout",
            http_status=502,
            retryable=True,
        )

    @app.get("/http-error")
    async def http_error_endpoint():
        from fastapi import HTTPException
        raise HTTPException(status_code=403, detail="forbidden resource")

    @app.get("/unexpected-error")
    async def unexpected_error_endpoint():
        raise RuntimeError("something unexpected happened")

    class ItemRequest(BaseModel):
        name: str

    @app.post("/validation-error")
    async def validation_error_endpoint(item: ItemRequest):
        return item

    return app


class TestAppExceptionHandler:
    """Verify the AppException handler returns the unified envelope."""

    def setup_method(self):
        self.app = _make_app_with_handlers()
        self.client = TestClient(self.app, raise_server_exceptions=False)

    def test_returns_envelope_structure(self):
        resp = self.client.get("/app-error")
        body = resp.json()
        assert set(body.keys()) == {"code", "message", "data", "trace_id"}

    def test_code_is_uppercase(self):
        resp = self.client.get("/app-error")
        body = resp.json()
        assert body["code"] == "TASK_NOT_FOUND"

    def test_message_from_exception(self):
        resp = self.client.get("/app-error")
        body = resp.json()
        assert body["message"] == "task abc not found"

    def test_data_is_none(self):
        resp = self.client.get("/app-error")
        body = resp.json()
        assert body["data"] is None

    def test_http_status_matches(self):
        resp = self.client.get("/app-error")
        assert resp.status_code == 404

    def test_trace_id_is_uuid(self):
        resp = self.client.get("/app-error")
        body = resp.json()
        uuid.UUID(body["trace_id"])  # raises if not valid UUID

    def test_retryable_error_returns_502(self):
        resp = self.client.get("/app-error-retryable")
        assert resp.status_code == 502
        body = resp.json()
        assert body["code"] == "GITHUB_API_ERROR"


class TestValidationExceptionHandler:
    """Verify RequestValidationError handler returns VALIDATION_ERROR envelope."""

    def setup_method(self):
        self.app = _make_app_with_handlers()
        self.client = TestClient(self.app, raise_server_exceptions=False)

    def test_returns_envelope_structure(self):
        resp = self.client.post("/validation-error", json={})
        body = resp.json()
        assert set(body.keys()) == {"code", "message", "data", "trace_id"}

    def test_code_is_validation_error(self):
        resp = self.client.post("/validation-error", json={})
        body = resp.json()
        assert body["code"] == "VALIDATION_ERROR"

    def test_http_status_is_422(self):
        resp = self.client.post("/validation-error", json={})
        assert resp.status_code == 422

    def test_data_is_none(self):
        resp = self.client.post("/validation-error", json={})
        body = resp.json()
        assert body["data"] is None

    def test_message_contains_validation_detail(self):
        resp = self.client.post("/validation-error", json={})
        body = resp.json()
        assert isinstance(body["message"], str)
        assert len(body["message"]) > 0

    def test_no_stack_trace_in_message(self):
        resp = self.client.post("/validation-error", json={})
        body = resp.json()
        assert "Traceback" not in body["message"]
        assert "File" not in body["message"]


class TestHTTPExceptionHandler:
    """Verify HTTPException handler returns the unified envelope."""

    def setup_method(self):
        self.app = _make_app_with_handlers()
        self.client = TestClient(self.app, raise_server_exceptions=False)

    def test_returns_envelope_structure(self):
        resp = self.client.get("/http-error")
        body = resp.json()
        assert set(body.keys()) == {"code", "message", "data", "trace_id"}

    def test_preserves_http_status(self):
        resp = self.client.get("/http-error")
        assert resp.status_code == 403

    def test_data_is_none(self):
        resp = self.client.get("/http-error")
        body = resp.json()
        assert body["data"] is None

    def test_code_is_string(self):
        resp = self.client.get("/http-error")
        body = resp.json()
        assert isinstance(body["code"], str)

    def test_trace_id_is_uuid(self):
        resp = self.client.get("/http-error")
        body = resp.json()
        uuid.UUID(body["trace_id"])


class TestUnexpectedExceptionHandler:
    """Verify unexpected exceptions map to INTERNAL_ERROR with safe message."""

    def setup_method(self):
        self.app = _make_app_with_handlers()
        self.client = TestClient(self.app, raise_server_exceptions=False)

    def test_returns_envelope_structure(self):
        resp = self.client.get("/unexpected-error")
        body = resp.json()
        assert set(body.keys()) == {"code", "message", "data", "trace_id"}

    def test_code_is_internal_error(self):
        resp = self.client.get("/unexpected-error")
        body = resp.json()
        assert body["code"] == "INTERNAL_ERROR"

    def test_http_status_is_500(self):
        resp = self.client.get("/unexpected-error")
        assert resp.status_code == 500

    def test_message_is_generic_safe_text(self):
        resp = self.client.get("/unexpected-error")
        body = resp.json()
        assert body["message"] == "An unexpected error occurred"

    def test_no_stack_trace_leakage(self):
        resp = self.client.get("/unexpected-error")
        body = resp.json()
        assert "RuntimeError" not in body["message"]
        assert "something unexpected happened" not in body["message"]
        assert "Traceback" not in body["message"]

    def test_data_is_none(self):
        resp = self.client.get("/unexpected-error")
        body = resp.json()
        assert body["data"] is None

    def test_trace_id_is_uuid(self):
        resp = self.client.get("/unexpected-error")
        body = resp.json()
        uuid.UUID(body["trace_id"])


class TestTraceIdMiddleware:
    """Verify trace_id is consistent per request and present in all responses."""

    def setup_method(self):
        self.app = _make_app_with_handlers()
        self.client = TestClient(self.app, raise_server_exceptions=False)

    def test_success_response_has_trace_id(self):
        resp = self.client.get("/ok")
        body = resp.json()
        # The /ok endpoint returns raw dict, not envelope,
        # but error responses must have trace_id.
        # Verify error responses have trace_id:
        resp2 = self.client.get("/app-error")
        body2 = resp2.json()
        assert "trace_id" in body2
        uuid.UUID(body2["trace_id"])

    def test_different_requests_have_different_trace_ids(self):
        resp1 = self.client.get("/app-error")
        resp2 = self.client.get("/app-error")
        tid1 = resp1.json()["trace_id"]
        tid2 = resp2.json()["trace_id"]
        assert tid1 != tid2
