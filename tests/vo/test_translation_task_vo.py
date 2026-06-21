"""Tests for VO serialization and structure."""

from app.vo.installation_vo import InstallationVO, RepositoryItemVO, RepositoryListVO
from app.vo.translation_task_vo import (
    PublicPreviewVO,
    FilePreviewVO,
)


class TestInstallationVO:
    """Tests for InstallationVO serialization."""

    def test_serialization(self):
        vo = InstallationVO(
            installation_id=12345,
            account_login="test-org",
            account_type="Organization",
            repository_selection="all",
        )
        data = vo.model_dump()
        assert data["installation_id"] == 12345
        assert data["account_login"] == "test-org"
        assert data["account_type"] == "Organization"
        assert data["repository_selection"] == "all"

    def test_field_types(self):
        vo = InstallationVO(
            installation_id=12345,
            account_login="test-org",
            account_type="Organization",
            repository_selection="all",
        )
        assert isinstance(vo.installation_id, int)
        assert isinstance(vo.account_login, str)
        assert isinstance(vo.account_type, str)
        assert isinstance(vo.repository_selection, str)


class TestRepositoryItemVO:
    """Tests for RepositoryItemVO serialization."""

    def test_serialization(self):
        vo = RepositoryItemVO(
            full_name="owner/repo",
            default_branch="main",
            private=False,
        )
        data = vo.model_dump()
        assert data["full_name"] == "owner/repo"
        assert data["default_branch"] == "main"
        assert data["private"] is False

    def test_private_repository(self):
        vo = RepositoryItemVO(
            full_name="owner/repo",
            default_branch="main",
            private=True,
        )
        assert vo.private is True


class TestRepositoryListVO:
    """Tests for RepositoryListVO serialization."""

    def test_serialization(self):
        vo = RepositoryListVO(
            repositories=[
                RepositoryItemVO(
                    full_name="owner/repo1",
                    default_branch="main",
                    private=False,
                ),
                RepositoryItemVO(
                    full_name="owner/repo2",
                    default_branch="develop",
                    private=True,
                ),
            ]
        )
        data = vo.model_dump()
        assert len(data["repositories"]) == 2
        assert data["repositories"][0]["full_name"] == "owner/repo1"
        assert data["repositories"][1]["full_name"] == "owner/repo2"

    def test_empty_list(self):
        vo = RepositoryListVO(repositories=[])
        data = vo.model_dump()
        assert data["repositories"] == []


class TestFilePreviewVO:
    """Tests for FilePreviewVO serialization."""

    def test_serialization(self):
        vo = FilePreviewVO(
            source_path="README.md",
            target_path="README.zh-CN.md",
            status="translated",
        )
        data = vo.model_dump()
        assert data["source_path"] == "README.md"
        assert data["target_path"] == "README.zh-CN.md"
        assert data["status"] == "translated"

    def test_default_status(self):
        vo = FilePreviewVO(
            source_path="README.md",
            target_path="README.zh-CN.md",
        )
        assert vo.status == "translated"


class TestPublicPreviewVO:
    """Tests for PublicPreviewVO serialization."""

    def test_serialization(self):
        vo = PublicPreviewVO(
            previews=[
                FilePreviewVO(
                    source_path="README.md",
                    target_path="README.zh-CN.md",
                    status="translated",
                )
            ]
        )
        data = vo.model_dump()
        assert len(data["previews"]) == 1
        assert data["previews"][0]["source_path"] == "README.md"
        assert data["previews"][0]["status"] == "translated"

    def test_empty_previews(self):
        vo = PublicPreviewVO(previews=[])
        data = vo.model_dump()
        assert data["previews"] == []

    def test_multiple_previews(self):
        vo = PublicPreviewVO(
            previews=[
                FilePreviewVO(
                    source_path="README.md",
                    target_path="README.zh-CN.md",
                    status="translated",
                ),
                FilePreviewVO(
                    source_path="docs/guide.md",
                    target_path="docs/guide.zh-CN.md",
                    status="translated",
                ),
            ]
        )
        data = vo.model_dump()
        assert len(data["previews"]) == 2
