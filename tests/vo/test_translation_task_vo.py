"""Tests for VO serialization and structure."""

from app.vo.installation_vo import InstallationVO, RepositoryItemVO, RepositoryListVO
from app.vo.translation_task_vo import (
    TranslationTaskVO,
    FileMappingVO,
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


class TestFileMappingVO:
    """Tests for FileMappingVO serialization."""

    def test_serialization(self):
        vo = FileMappingVO(
            source_path="README.md",
            target_path="README.zh-CN.md",
        )
        data = vo.model_dump()
        assert data["source_path"] == "README.md"
        assert data["target_path"] == "README.zh-CN.md"


class TestTranslationTaskVO:
    """Tests for TranslationTaskVO serialization."""

    def test_success_serialization(self):
        vo = TranslationTaskVO(
            status="succeeded",
            pr_url="https://github.com/owner/repo/pull/123",
            pr_number=123,
            mappings=[
                FileMappingVO(
                    source_path="README.md",
                    target_path="README.zh-CN.md",
                )
            ],
            error_code=None,
            error_message=None,
        )
        data = vo.model_dump()
        assert data["status"] == "succeeded"
        assert data["pr_url"] == "https://github.com/owner/repo/pull/123"
        assert data["pr_number"] == 123
        assert len(data["mappings"]) == 1
        assert data["error_code"] is None
        assert data["error_message"] is None

    def test_failure_serialization(self):
        vo = TranslationTaskVO(
            status="failed",
            pr_url=None,
            pr_number=None,
            mappings=None,
            error_code="translation_error",
            error_message="Translation provider returned an error",
        )
        data = vo.model_dump()
        assert data["status"] == "failed"
        assert data["pr_url"] is None
        assert data["pr_number"] is None
        assert data["mappings"] is None
        assert data["error_code"] == "translation_error"
        assert data["error_message"] == "Translation provider returned an error"

    def test_status_field_is_string(self):
        vo = TranslationTaskVO(
            status="succeeded",
            pr_url=None,
            pr_number=None,
            mappings=None,
            error_code=None,
            error_message=None,
        )
        assert isinstance(vo.status, str)


class TestFilePreviewVO:
    """Tests for FilePreviewVO serialization."""

    def test_serialization(self):
        vo = FilePreviewVO(
            source_path="README.md",
            target_path="README.zh-CN.md",
            translated_content="# 你好世界",
        )
        data = vo.model_dump()
        assert data["source_path"] == "README.md"
        assert data["target_path"] == "README.zh-CN.md"
        assert data["translated_content"] == "# 你好世界"


class TestPublicPreviewVO:
    """Tests for PublicPreviewVO serialization."""

    def test_serialization(self):
        vo = PublicPreviewVO(
            previews=[
                FilePreviewVO(
                    source_path="README.md",
                    target_path="README.zh-CN.md",
                    translated_content="# 你好世界",
                )
            ]
        )
        data = vo.model_dump()
        assert len(data["previews"]) == 1
        assert data["previews"][0]["source_path"] == "README.md"
        assert data["previews"][0]["translated_content"] == "# 你好世界"

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
                    translated_content="# 你好",
                ),
                FilePreviewVO(
                    source_path="docs/guide.md",
                    target_path="docs/guide.zh-CN.md",
                    translated_content="# 指南",
                ),
            ]
        )
        data = vo.model_dump()
        assert len(data["previews"]) == 2
