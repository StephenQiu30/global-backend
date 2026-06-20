import pytest

from app.domain.repository import RepositoryRef, parse_repository_input


class TestParseRepositoryInput:
    """Tests for parse_repository_input function."""

    def test_full_https_url(self):
        """Parse https://github.com/owner/repo."""
        result = parse_repository_input("https://github.com/owner/repo")
        assert result.owner == "owner"
        assert result.repo == "repo"
        assert result.full_name == "owner/repo"

    def test_full_https_url_with_trailing_slash(self):
        """Parse https://github.com/owner/repo/."""
        result = parse_repository_input("https://github.com/owner/repo/")
        assert result.owner == "owner"
        assert result.repo == "repo"
        assert result.full_name == "owner/repo"

    def test_github_url_without_protocol(self):
        """Parse github.com/owner/repo."""
        result = parse_repository_input("github.com/owner/repo")
        assert result.owner == "owner"
        assert result.repo == "repo"
        assert result.full_name == "owner/repo"

    def test_owner_repo_shorthand(self):
        """Parse owner/repo."""
        result = parse_repository_input("owner/repo")
        assert result.owner == "owner"
        assert result.repo == "repo"
        assert result.full_name == "owner/repo"

    def test_normalizes_to_lowercase(self):
        """Normalize Owner/Repo to owner/repo."""
        result = parse_repository_input("Owner/Repo")
        assert result.owner == "owner"
        assert result.repo == "repo"
        assert result.full_name == "owner/repo"

    def test_strips_git_suffix(self):
        """Strip .git suffix from repo name."""
        result = parse_repository_input("https://github.com/owner/repo.git")
        assert result.owner == "owner"
        assert result.repo == "repo"
        assert result.full_name == "owner/repo"

    def test_rejects_empty_string(self):
        """Reject empty input."""
        with pytest.raises(ValueError, match="invalid"):
            parse_repository_input("")

    def test_rejects_whitespace_only(self):
        """Reject whitespace-only input."""
        with pytest.raises(ValueError, match="invalid"):
            parse_repository_input("   ")

    def test_rejects_ssh_url(self):
        """Reject git@github.com:owner/repo.git."""
        with pytest.raises(ValueError, match="invalid"):
            parse_repository_input("git@github.com:owner/repo.git")

    def test_rejects_gitlab_url(self):
        """Reject https://gitlab.com/owner/repo."""
        with pytest.raises(ValueError, match="invalid"):
            parse_repository_input("https://gitlab.com/owner/repo")

    def test_rejects_bitbucket_url(self):
        """Reject https://bitbucket.org/owner/repo."""
        with pytest.raises(ValueError, match="invalid"):
            parse_repository_input("https://bitbucket.org/owner/repo")

    def test_rejects_github_subpath(self):
        """Reject https://github.com/owner/repo/tree/main/path."""
        with pytest.raises(ValueError, match="invalid"):
            parse_repository_input("https://github.com/owner/repo/tree/main/path")

    def test_rejects_gist_url(self):
        """Reject https://gist.github.com/owner/abc123."""
        with pytest.raises(ValueError, match="invalid"):
            parse_repository_input("https://gist.github.com/owner/abc123")


class TestRepositoryRef:
    """Tests for RepositoryRef model."""

    def test_model_creation(self):
        """Create RepositoryRef with valid data."""
        ref = RepositoryRef(owner="owner", repo="repo", full_name="owner/repo")
        assert ref.owner == "owner"
        assert ref.repo == "repo"
        assert ref.full_name == "owner/repo"

    def test_model_serialization(self):
        """Serialize RepositoryRef to dict."""
        ref = RepositoryRef(owner="owner", repo="repo", full_name="owner/repo")
        data = ref.model_dump()
        assert data == {"owner": "owner", "repo": "repo", "full_name": "owner/repo"}
