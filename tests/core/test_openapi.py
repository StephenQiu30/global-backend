"""Tests for the shared OpenAPI error response helper."""

import pytest

from app.core.response import ErrorCode


class TestCommonErrorResponses:
    """Verify common_error_responses builds correct OpenAPI responses dict."""

    def test_returns_empty_dict_for_no_codes(self):
        from app.core.openapi import common_error_responses

        result = common_error_responses()
        assert result == {}

    def test_returns_dict_with_status_code_keys(self):
        from app.core.openapi import common_error_responses

        result = common_error_responses(
            ErrorCode.VALIDATION_ERROR, ErrorCode.INTERNAL_ERROR
        )
        assert 422 in result
        assert 500 in result

    def test_entry_has_description(self):
        from app.core.openapi import common_error_responses

        result = common_error_responses(ErrorCode.VALIDATION_ERROR)
        entry = result[422]
        assert "description" in entry
        assert isinstance(entry["description"], str)
        assert len(entry["description"]) > 0

    def test_entry_has_content_with_json_schema(self):
        from app.core.openapi import common_error_responses

        result = common_error_responses(ErrorCode.VALIDATION_ERROR)
        entry = result[422]
        assert "content" in entry
        assert "application/json" in entry["content"]
        schema = entry["content"]["application/json"]["schema"]
        assert "$ref" in schema or "properties" in schema

    def test_schema_references_api_response_vo(self):
        from app.core.openapi import common_error_responses

        result = common_error_responses(ErrorCode.VALIDATION_ERROR)
        schema = result[422]["content"]["application/json"]["schema"]
        # The schema should reference ApiResponseVO
        if "$ref" in schema:
            assert "ApiResponseVO" in schema["$ref"]
        else:
            # Inline schema with code, message, data, trace_id
            props = schema.get("properties", {})
            assert "code" in props
            assert "message" in props
            assert "data" in props
            assert "trace_id" in props

    def test_multiple_codes_produce_multiple_entries(self):
        from app.core.openapi import common_error_responses

        result = common_error_responses(
            ErrorCode.VALIDATION_ERROR,
            ErrorCode.TASK_NOT_FOUND,
            ErrorCode.INTERNAL_ERROR,
        )
        assert len(result) == 3
        assert 422 in result
        assert 404 in result
        assert 500 in result

    def test_duplicate_status_codes_merge(self):
        """When two ErrorCode values map to the same HTTP status, keep one entry."""
        from app.core.openapi import common_error_responses

        result = common_error_responses(
            ErrorCode.TASK_NOT_FOUND,
            ErrorCode.REPOSITORY_NOT_FOUND,
        )
        # Both map to 404 — should produce one entry, not two
        assert 404 in result
        assert len(result) == 1


class TestPrebuiltTuples:
    """Verify pre-built error code tuples exist and are correct."""

    def test_validation_errors_tuple(self):
        from app.core.openapi import VALIDATION_ERRORS

        assert isinstance(VALIDATION_ERRORS, tuple)
        assert ErrorCode.VALIDATION_ERROR in VALIDATION_ERRORS

    def test_not_found_errors_tuple(self):
        from app.core.openapi import NOT_FOUND_ERRORS

        assert isinstance(NOT_FOUND_ERRORS, tuple)
        assert ErrorCode.TASK_NOT_FOUND in NOT_FOUND_ERRORS
        assert ErrorCode.REPOSITORY_NOT_FOUND in NOT_FOUND_ERRORS
        assert ErrorCode.INSTALLATION_NOT_FOUND in NOT_FOUND_ERRORS

    def test_server_errors_tuple(self):
        from app.core.openapi import SERVER_ERRORS

        assert isinstance(SERVER_ERRORS, tuple)
        assert ErrorCode.INTERNAL_ERROR in SERVER_ERRORS
