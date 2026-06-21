"""Tests for DTO field validation."""

import pytest
from pydantic import ValidationError

from app.dto.installation_dto import VerifyInstallationDTO
from app.dto.translation_task_dto import (
    CreateTranslationTaskDTO,
    CreatePublicPreviewDTO,
)


class TestVerifyInstallationDTO:
    """Tests for VerifyInstallationDTO validation."""

    def test_valid_data(self):
        dto = VerifyInstallationDTO(installation_id=12345)
        assert dto.installation_id == 12345

    def test_missing_installation_id(self):
        with pytest.raises(ValidationError):
            VerifyInstallationDTO()


class TestCreateTranslationTaskDTO:
    """Tests for CreateTranslationTaskDTO validation."""

    def test_valid_data(self):
        dto = CreateTranslationTaskDTO(
            installation_id="inst-123",
            repository="owner/repo",
            base_branch="main",
            files=["README.md"],
            language="zh-CN",
        )
        assert dto.installation_id == "inst-123"
        assert dto.repository == "owner/repo"
        assert dto.base_branch == "main"
        assert dto.files == ["README.md"]
        assert dto.language == "zh-CN"

    def test_missing_installation_id(self):
        with pytest.raises(ValidationError):
            CreateTranslationTaskDTO(
                repository="owner/repo",
                base_branch="main",
                files=["README.md"],
                language="zh-CN",
            )

    def test_empty_installation_id(self):
        with pytest.raises(ValidationError):
            CreateTranslationTaskDTO(
                installation_id="",
                repository="owner/repo",
                base_branch="main",
                files=["README.md"],
                language="zh-CN",
            )

    def test_missing_repository(self):
        with pytest.raises(ValidationError):
            CreateTranslationTaskDTO(
                installation_id="inst-123",
                base_branch="main",
                files=["README.md"],
                language="zh-CN",
            )

    def test_empty_repository(self):
        with pytest.raises(ValidationError):
            CreateTranslationTaskDTO(
                installation_id="inst-123",
                repository="",
                base_branch="main",
                files=["README.md"],
                language="zh-CN",
            )

    def test_missing_base_branch(self):
        with pytest.raises(ValidationError):
            CreateTranslationTaskDTO(
                installation_id="inst-123",
                repository="owner/repo",
                files=["README.md"],
                language="zh-CN",
            )

    def test_empty_base_branch(self):
        with pytest.raises(ValidationError):
            CreateTranslationTaskDTO(
                installation_id="inst-123",
                repository="owner/repo",
                base_branch="",
                files=["README.md"],
                language="zh-CN",
            )

    def test_missing_files(self):
        with pytest.raises(ValidationError):
            CreateTranslationTaskDTO(
                installation_id="inst-123",
                repository="owner/repo",
                base_branch="main",
                language="zh-CN",
            )

    def test_empty_files(self):
        with pytest.raises(ValidationError):
            CreateTranslationTaskDTO(
                installation_id="inst-123",
                repository="owner/repo",
                base_branch="main",
                files=[],
                language="zh-CN",
            )

    def test_missing_language(self):
        with pytest.raises(ValidationError):
            CreateTranslationTaskDTO(
                installation_id="inst-123",
                repository="owner/repo",
                base_branch="main",
                files=["README.md"],
            )

    def test_empty_language(self):
        with pytest.raises(ValidationError):
            CreateTranslationTaskDTO(
                installation_id="inst-123",
                repository="owner/repo",
                base_branch="main",
                files=["README.md"],
                language="",
            )

    def test_multiple_files(self):
        dto = CreateTranslationTaskDTO(
            installation_id="inst-123",
            repository="owner/repo",
            base_branch="main",
            files=["README.md", "docs/guide.md"],
            language="zh-CN",
        )
        assert len(dto.files) == 2


class TestCreatePublicPreviewDTO:
    """Tests for CreatePublicPreviewDTO validation."""

    def test_valid_data(self):
        dto = CreatePublicPreviewDTO(
            repository="owner/repo",
            files=["README.md"],
            language="zh-CN",
        )
        assert dto.repository == "owner/repo"
        assert dto.files == ["README.md"]
        assert dto.language == "zh-CN"

    def test_missing_repository(self):
        with pytest.raises(ValidationError):
            CreatePublicPreviewDTO(
                files=["README.md"],
                language="zh-CN",
            )

    def test_empty_repository(self):
        with pytest.raises(ValidationError):
            CreatePublicPreviewDTO(
                repository="",
                files=["README.md"],
                language="zh-CN",
            )

    def test_missing_files(self):
        with pytest.raises(ValidationError):
            CreatePublicPreviewDTO(
                repository="owner/repo",
                language="zh-CN",
            )

    def test_empty_files(self):
        with pytest.raises(ValidationError):
            CreatePublicPreviewDTO(
                repository="owner/repo",
                files=[],
                language="zh-CN",
            )

    def test_missing_language(self):
        with pytest.raises(ValidationError):
            CreatePublicPreviewDTO(
                repository="owner/repo",
                files=["README.md"],
            )

    def test_empty_language(self):
        with pytest.raises(ValidationError):
            CreatePublicPreviewDTO(
                repository="owner/repo",
                files=["README.md"],
                language="",
            )

    def test_multiple_files(self):
        dto = CreatePublicPreviewDTO(
            repository="owner/repo",
            files=["README.md", "docs/guide.md"],
            language="ja",
        )
        assert len(dto.files) == 2
