"""Tests for repository request DTO validation."""

import pytest
from pydantic import ValidationError

from app.dto.repository import (
    GetMarkdownFilesRequest,
    ResolveRepositoryRequest,
)


class TestResolveRepositoryRequest:
    def test_valid_data(self):
        request = ResolveRepositoryRequest(input="owner/repo", installation_id=12345)
        assert request.input == "owner/repo"
        assert request.installation_id == 12345

    def test_missing_input(self):
        with pytest.raises(ValidationError):
            ResolveRepositoryRequest(installation_id=12345)


class TestGetMarkdownFilesRequest:
    def test_defaults(self):
        request = GetMarkdownFilesRequest()
        assert request.language == "zh-CN"
        assert request.installation_id is None

    def test_custom_values(self):
        request = GetMarkdownFilesRequest(language="ja", installation_id="999")
        assert request.language == "ja"
        assert request.installation_id == "999"
