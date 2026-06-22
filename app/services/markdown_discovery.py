"""Service for discovering Markdown files in GitHub repositories."""

from dataclasses import dataclass
from typing import List, Optional

from app.core.exceptions import AppException
from app.core.response import ErrorCode
from app.domain.markdown_files import (
    is_supported_markdown_path,
    is_translated_variant,
    is_safe_path,
    is_in_excluded_directory,
    is_default_readme,
    target_translation_path,
    MAX_TOTAL_SIZE,
)


@dataclass
class MarkdownFileInfo:
    """Information about a discovered Markdown file."""

    path: str
    size_bytes: int
    is_default_readme: bool
    is_translated_variant: bool
    disabled_reason: Optional[str]
    target_path_preview: str
    target_exists: bool


def get_repository_tree(
    owner: str,
    repo: str,
    branch: str,
    installation_id: int | str,
    github_client,
) -> List[dict]:
    """Fetch repository tree from GitHub API."""
    if github_client is None:
        raise AppException(
            code=ErrorCode.VALIDATION_ERROR,
            message="github_client is required",
            http_status=422,
        )

    return github_client.get_repository_tree(
        installation_id=installation_id,
        full_name=f"{owner}/{repo}",
        branch=branch,
    )


def discover_markdown_files(
    tree_items: List[dict],
    language: str = 'zh-CN',
    max_total_size: int = MAX_TOTAL_SIZE,
) -> List[MarkdownFileInfo]:
    """Discover eligible Markdown files from a repository tree.

    Args:
        tree_items: List of tree items from GitHub API
        language: Target language for path previews
        max_total_size: Maximum total size for enabled files

    Returns:
        List of MarkdownFileInfo for eligible files
    """
    eligible_files = []
    tree_paths = {
        item.get("path")
        for item in tree_items
        if item.get("type") == "blob" and item.get("path")
    }

    for item in tree_items:
        path = item.get('path', '')
        size = item.get('size', 0)
        item_type = item.get('type', '')

        # Only process blobs (files)
        if item_type != 'blob':
            continue

        # Skip unsafe paths
        if not is_safe_path(path):
            continue

        # Skip excluded directories
        if is_in_excluded_directory(path):
            continue

        # Skip unsupported extensions
        if not is_supported_markdown_path(path):
            continue

        # Skip translated variants
        if is_translated_variant(path):
            continue

        # Determine if this is the default README
        default_readme = is_default_readme(path)

        # Generate target path preview
        target_path = target_translation_path(path, language)

        # Check if target already exists in repository tree
        target_exists = target_path in tree_paths

        # Determine disabled reason
        disabled_reason = None
        if size > max_total_size:
            disabled_reason = f"File size ({size} bytes) exceeds maximum ({max_total_size} bytes)"

        eligible_files.append(MarkdownFileInfo(
            path=path,
            size_bytes=size,
            is_default_readme=default_readme,
            is_translated_variant=False,  # We already filtered these out
            disabled_reason=disabled_reason,
            target_path_preview=target_path,
            target_exists=target_exists,
        ))

    # Sort: README first, then alphabetically
    def sort_key(f: MarkdownFileInfo):
        # README.md comes first, then README.markdown
        if f.path == 'README.md':
            return (0, f.path)
        if f.path == 'README.markdown':
            return (1, f.path)
        return (2, f.path)

    eligible_files.sort(key=sort_key)

    return eligible_files
