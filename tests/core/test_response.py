"""Tests for ErrorCode enum, ApiResponseVO, and response helpers."""

import re
import uuid

import pytest

from app.core.response import (
    ErrorCode,
    ApiResponseVO,
    success_response,
    error_response,
)


# --- ErrorCode enum ---

class TestErrorCodeEnum:
    """Verify the ErrorCode enum matches the OpenSpec contract."""

    REQUIRED_CODES = {
        "SUCCESS",
        "VALIDATION_ERROR",
        "INTERNAL_ERROR",
        "GITHUB_API_ERROR",
        "TASK_NOT_FOUND",
        "INSTALLATION_NOT_FOUND",
        "REPOSITORY_NOT_FOUND",
        "REPOSITORY_NOT_INSTALLED",
        "GITHUB_RATE_LIMITED",
        "TRANSLATION_ERROR",
        "UNSUPPORTED_LANGUAGE",
    }

    def test_has_all_required_codes(self):
        actual = {member.name for member in ErrorCode}
        assert actual == self.REQUIRED_CODES

    def test_enum_count(self):
        assert len(ErrorCode) == 11

    def test_values_are_uppercase_strings(self):
        for member in ErrorCode:
            assert member.value == member.name
            assert member.value.isupper()
            assert isinstance(member.value, str)

    def test_is_string_enum(self):
        assert isinstance(ErrorCode.SUCCESS, str)
        assert ErrorCode.SUCCESS == "SUCCESS"


# --- ApiResponseVO model ---

class TestApiResponseVO:
    """Verify the generic response envelope Pydantic model."""

    def test_has_required_fields(self):
        fields = ApiResponseVO.model_fields
        assert "code" in fields
        assert "message" in fields
        assert "data" in fields
        assert "trace_id" in fields

    def test_field_count(self):
        assert len(ApiResponseVO.model_fields) == 4

    def test_code_accepts_error_code_enum(self):
        trace_id = str(uuid.uuid4())
        envelope = ApiResponseVO(
            code=ErrorCode.SUCCESS,
            message="OK",
            data={"key": "value"},
            trace_id=trace_id,
        )
        assert envelope.code == ErrorCode.SUCCESS

    def test_data_accepts_none(self):
        trace_id = str(uuid.uuid4())
        envelope = ApiResponseVO(
            code=ErrorCode.INTERNAL_ERROR,
            message="An unexpected error occurred",
            data=None,
            trace_id=trace_id,
        )
        assert envelope.data is None

    def test_data_accepts_dict(self):
        trace_id = str(uuid.uuid4())
        envelope = ApiResponseVO(
            code=ErrorCode.SUCCESS,
            message="OK",
            data={"id": 1, "name": "test"},
            trace_id=trace_id,
        )
        assert envelope.data == {"id": 1, "name": "test"}

    def test_data_accepts_list(self):
        trace_id = str(uuid.uuid4())
        envelope = ApiResponseVO(
            code=ErrorCode.SUCCESS,
            message="OK",
            data=[1, 2, 3],
            trace_id=trace_id,
        )
        assert envelope.data == [1, 2, 3]

    def test_serialization_produces_correct_json_keys(self):
        trace_id = str(uuid.uuid4())
        envelope = ApiResponseVO(
            code=ErrorCode.SUCCESS,
            message="OK",
            data={"id": 1},
            trace_id=trace_id,
        )
        dumped = envelope.model_dump()
        assert set(dumped.keys()) == {"code", "message", "data", "trace_id"}

    def test_code_serializes_as_string_value(self):
        trace_id = str(uuid.uuid4())
        envelope = ApiResponseVO(
            code=ErrorCode.VALIDATION_ERROR,
            message="bad input",
            data=None,
            trace_id=trace_id,
        )
        dumped = envelope.model_dump()
        assert dumped["code"] == "VALIDATION_ERROR"

    def test_trace_id_is_string(self):
        trace_id = str(uuid.uuid4())
        envelope = ApiResponseVO(
            code=ErrorCode.SUCCESS,
            message="OK",
            data=None,
            trace_id=trace_id,
        )
        assert isinstance(envelope.trace_id, str)


# --- success_response helper ---

class TestSuccessResponse:
    """Verify the success_response helper builds the correct envelope."""

    def test_returns_api_response_vo(self):
        trace_id = str(uuid.uuid4())
        result = success_response(data={"id": 1}, trace_id=trace_id)
        assert isinstance(result, ApiResponseVO)

    def test_code_is_success(self):
        trace_id = str(uuid.uuid4())
        result = success_response(data=None, trace_id=trace_id)
        assert result.code == ErrorCode.SUCCESS

    def test_message_is_ok(self):
        trace_id = str(uuid.uuid4())
        result = success_response(data=None, trace_id=trace_id)
        assert result.message == "OK"

    def test_data_passed_through(self):
        trace_id = str(uuid.uuid4())
        payload = {"user": "test", "count": 42}
        result = success_response(data=payload, trace_id=trace_id)
        assert result.data == payload

    def test_none_data_passed_through(self):
        trace_id = str(uuid.uuid4())
        result = success_response(data=None, trace_id=trace_id)
        assert result.data is None

    def test_trace_id_preserved(self):
        trace_id = str(uuid.uuid4())
        result = success_response(data=None, trace_id=trace_id)
        assert result.trace_id == trace_id

    def test_list_data_passed_through(self):
        trace_id = str(uuid.uuid4())
        items = [1, 2, 3]
        result = success_response(data=items, trace_id=trace_id)
        assert result.data == items


# --- error_response helper ---

class TestErrorResponse:
    """Verify the error_response helper builds the correct envelope."""

    def test_returns_api_response_vo(self):
        trace_id = str(uuid.uuid4())
        result = error_response(
            code=ErrorCode.VALIDATION_ERROR,
            message="bad input",
            trace_id=trace_id,
        )
        assert isinstance(result, ApiResponseVO)

    def test_code_is_error_code(self):
        trace_id = str(uuid.uuid4())
        result = error_response(
            code=ErrorCode.TASK_NOT_FOUND,
            message="task not found",
            trace_id=trace_id,
        )
        assert result.code == ErrorCode.TASK_NOT_FOUND

    def test_message_preserved(self):
        trace_id = str(uuid.uuid4())
        result = error_response(
            code=ErrorCode.INTERNAL_ERROR,
            message="An unexpected error occurred",
            trace_id=trace_id,
        )
        assert result.message == "An unexpected error occurred"

    def test_data_is_none(self):
        trace_id = str(uuid.uuid4())
        result = error_response(
            code=ErrorCode.VALIDATION_ERROR,
            message="bad input",
            trace_id=trace_id,
        )
        assert result.data is None

    def test_trace_id_preserved(self):
        trace_id = str(uuid.uuid4())
        result = error_response(
            code=ErrorCode.INTERNAL_ERROR,
            message="error",
            trace_id=trace_id,
        )
        assert result.trace_id == trace_id

    def test_various_error_codes(self):
        trace_id = str(uuid.uuid4())
        for code in ErrorCode:
            if code == ErrorCode.SUCCESS:
                continue
            result = error_response(code=code, message="test", trace_id=trace_id)
            assert result.code == code
            assert result.data is None
