"""Tests for translation task request DTO validation."""

import pytest
from pydantic import ValidationError

from app.dto.translation_task import (
    CreatePublicPreviewRequest,
    CreateTranslationTaskRequest,
    GetTranslationTaskFilePreviewsRequest,
    GetTranslationTaskStatusRequest,
)


class TestCreateTranslationTaskRequest:
    def test_valid_data(self):
        request = CreateTranslationTaskRequest(
            installation_id="inst-123",
            repository="owner/repo",
            base_branch="main",
            files=["README.md"],
            language="zh-CN",
        )
        assert request.installation_id == "inst-123"
        assert request.repository == "owner/repo"
        assert request.base_branch == "main"
        assert request.files == ["README.md"]
        assert request.language == "zh-CN"

    def test_missing_installation_id(self):
        with pytest.raises(ValidationError):
            CreateTranslationTaskRequest(
                repository="owner/repo",
                base_branch="main",
                files=["README.md"],
                language="zh-CN",
            )

    def test_empty_installation_id(self):
        with pytest.raises(ValidationError):
            CreateTranslationTaskRequest(
                installation_id="",
                repository="owner/repo",
                base_branch="main",
                files=["README.md"],
                language="zh-CN",
            )

    def test_missing_repository(self):
        with pytest.raises(ValidationError):
            CreateTranslationTaskRequest(
                installation_id="inst-123",
                base_branch="main",
                files=["README.md"],
                language="zh-CN",
            )

    def test_empty_repository(self):
        with pytest.raises(ValidationError):
            CreateTranslationTaskRequest(
                installation_id="inst-123",
                repository="",
                base_branch="main",
                files=["README.md"],
                language="zh-CN",
            )

    def test_missing_base_branch(self):
        with pytest.raises(ValidationError):
            CreateTranslationTaskRequest(
                installation_id="inst-123",
                repository="owner/repo",
                files=["README.md"],
                language="zh-CN",
            )

    def test_empty_base_branch(self):
        with pytest.raises(ValidationError):
            CreateTranslationTaskRequest(
                installation_id="inst-123",
                repository="owner/repo",
                base_branch="",
                files=["README.md"],
                language="zh-CN",
            )

    def test_missing_files(self):
        with pytest.raises(ValidationError):
            CreateTranslationTaskRequest(
                installation_id="inst-123",
                repository="owner/repo",
                base_branch="main",
                language="zh-CN",
            )

    def test_empty_files(self):
        with pytest.raises(ValidationError):
            CreateTranslationTaskRequest(
                installation_id="inst-123",
                repository="owner/repo",
                base_branch="main",
                files=[],
                language="zh-CN",
            )

    def test_missing_language(self):
        with pytest.raises(ValidationError):
            CreateTranslationTaskRequest(
                installation_id="inst-123",
                repository="owner/repo",
                base_branch="main",
                files=["README.md"],
            )

    def test_empty_language(self):
        with pytest.raises(ValidationError):
            CreateTranslationTaskRequest(
                installation_id="inst-123",
                repository="owner/repo",
                base_branch="main",
                files=["README.md"],
                language="",
            )

    def test_multiple_files(self):
        request = CreateTranslationTaskRequest(
            installation_id="inst-123",
            repository="owner/repo",
            base_branch="main",
            files=["README.md", "docs/guide.md"],
            language="zh-CN",
        )
        assert len(request.files) == 2


class TestCreatePublicPreviewRequest:
    def test_valid_data(self):
        request = CreatePublicPreviewRequest(
            repository="owner/repo",
            files=["README.md"],
            language="zh-CN",
        )
        assert request.repository == "owner/repo"
        assert request.files == ["README.md"]
        assert request.language == "zh-CN"

    def test_missing_repository(self):
        with pytest.raises(ValidationError):
            CreatePublicPreviewRequest(
                files=["README.md"],
                language="zh-CN",
            )

    def test_empty_repository(self):
        with pytest.raises(ValidationError):
            CreatePublicPreviewRequest(
                repository="",
                files=["README.md"],
                language="zh-CN",
            )

    def test_missing_files(self):
        with pytest.raises(ValidationError):
            CreatePublicPreviewRequest(
                repository="owner/repo",
                language="zh-CN",
            )

    def test_empty_files(self):
        with pytest.raises(ValidationError):
            CreatePublicPreviewRequest(
                repository="owner/repo",
                files=[],
                language="zh-CN",
            )

    def test_missing_language(self):
        with pytest.raises(ValidationError):
            CreatePublicPreviewRequest(
                repository="owner/repo",
                files=["README.md"],
            )

    def test_empty_language(self):
        with pytest.raises(ValidationError):
            CreatePublicPreviewRequest(
                repository="owner/repo",
                files=["README.md"],
                language="",
            )

    def test_multiple_files(self):
        request = CreatePublicPreviewRequest(
            repository="owner/repo",
            files=["README.md", "docs/guide.md"],
            language="ja",
        )
        assert len(request.files) == 2


class TestGetTranslationTaskStatusRequest:
    def test_valid_data(self):
        request = GetTranslationTaskStatusRequest(task_id="abc-123")
        assert request.task_id == "abc-123"

    def test_missing_task_id(self):
        with pytest.raises(ValidationError):
            GetTranslationTaskStatusRequest()


class TestGetTranslationTaskFilePreviewsRequest:
    def test_valid_data(self):
        request = GetTranslationTaskFilePreviewsRequest(task_id="abc-123")
        assert request.task_id == "abc-123"

    def test_missing_task_id(self):
        with pytest.raises(ValidationError):
            GetTranslationTaskFilePreviewsRequest()
