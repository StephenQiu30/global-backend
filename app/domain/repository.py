import re
from urllib.parse import urlparse

from pydantic import BaseModel


class RepositoryRef(BaseModel):
    """Reference to a GitHub repository."""

    owner: str
    repo: str
    full_name: str


# Patterns for valid repository input
_OWNER_REPO_PATTERN = re.compile(r"^[a-zA-Z0-9]([a-zA-Z0-9-]*[a-zA-Z0-9])?/[a-zA-Z0-9._-]+$")
_GITHUB_HOSTS = {"github.com", "www.github.com"}


def parse_repository_input(value: str) -> RepositoryRef:
    """Parse a repository input string into a RepositoryRef.

    Accepted formats:
    - https://github.com/owner/repo
    - github.com/owner/repo
    - owner/repo

    Rejected formats:
    - Empty or whitespace-only strings
    - Git SSH URLs (git@github.com:owner/repo.git)
    - Non-GitHub URLs
    - GitHub subpath URLs (/owner/repo/tree/...)
    - Gist URLs
    """
    if not value or not value.strip():
        raise ValueError("invalid repository URL")

    value = value.strip()

    # Try parsing as URL
    if value.startswith(("http://", "https://")):
        parsed = urlparse(value)
        if parsed.hostname not in _GITHUB_HOSTS:
            raise ValueError("invalid repository URL")
        # Reject Gist
        if parsed.hostname and "gist" in parsed.hostname:
            raise ValueError("invalid repository URL")
        path = parsed.path.strip("/")
        return _parse_path(path)

    # Try parsing as github.com/owner/repo (without protocol)
    if value.startswith("github.com/"):
        path = value[len("github.com/"):]
        return _parse_path(path)

    # Try parsing as owner/repo
    if "/" in value and not value.startswith(("git@", "http://", "https://")):
        return _parse_owner_repo(value)

    raise ValueError("invalid repository URL")


def _parse_path(path: str) -> RepositoryRef:
    """Parse a GitHub path (owner/repo) into RepositoryRef."""
    parts = path.split("/")
    if len(parts) != 2:
        raise ValueError("invalid repository URL")
    return _parse_owner_repo(f"{parts[0]}/{parts[1]}")


def _parse_owner_repo(value: str) -> RepositoryRef:
    """Parse owner/repo format into RepositoryRef."""
    # Strip .git suffix
    if value.endswith(".git"):
        value = value[:-4]

    if not _OWNER_REPO_PATTERN.match(value):
        raise ValueError("invalid repository URL")

    owner, repo = value.split("/", 1)
    owner = owner.lower()
    repo = repo.lower()
    full_name = f"{owner}/{repo}"

    return RepositoryRef(owner=owner, repo=repo, full_name=full_name)
