"""Domain rules for Markdown file classification and selection."""

import re
from pathlib import PurePosixPath
from typing import List, Optional

# Constants
SUPPORTED_EXTENSIONS = {'.md', '.markdown'}
EXCLUDED_DIRS = {'.git', 'node_modules', 'dist', 'build', '.next'}
MAX_FILE_COUNT = 10
MAX_TOTAL_SIZE = 200 * 1024  # 200KB

# Pattern for translated variants: README.zh-CN.md, guide.en.md, etc.
TRANSLATED_VARIANT_PATTERN = re.compile(
    r'^(.+)\.([a-z]{2}(?:-[A-Z]{2})?)\.(md|markdown)$'
)


def is_supported_markdown_path(path: str) -> bool:
    """Check if path has .md or .markdown extension.

    Args:
        path: File path to check

    Returns:
        True if the file has a supported Markdown extension
    """
    ext = PurePosixPath(path).suffix.lower()
    return ext in SUPPORTED_EXTENSIONS


def is_translated_variant(path: str) -> bool:
    """Check if path matches language suffix pattern.

    Examples:
        - README.zh-CN.md -> True
        - guide.en.md -> True
        - README.md -> False

    Args:
        path: File path to check

    Returns:
        True if the file appears to be a translated variant
    """
    filename = PurePosixPath(path).name
    return bool(TRANSLATED_VARIANT_PATTERN.match(filename))


def is_safe_path(path: str) -> bool:
    """Reject directory traversal and absolute paths.

    Args:
        path: File path to validate

    Returns:
        True if the path is safe (no traversal, not absolute)
    """
    # Reject absolute paths
    if path.startswith('/'):
        return False

    # Normalize and check for directory traversal
    parts = PurePosixPath(path).parts
    if '..' in parts:
        return False

    return True


def is_in_excluded_directory(path: str) -> bool:
    """Check if path is in an excluded directory.

    Args:
        path: File path to check

    Returns:
        True if the path is in .git, node_modules, dist, build, or .next
    """
    parts = PurePosixPath(path).parts
    return any(part in EXCLUDED_DIRS for part in parts)


def target_translation_path(source_path: str, language: str) -> str:
    """Generate target path with language suffix.

    Examples:
        - README.md + zh-CN -> README.zh-CN.md
        - docs/guide.md + ja -> docs/guide.ja.md

    Args:
        source_path: Original file path
        language: Target language code

    Returns:
        Target path with language suffix inserted before extension
    """
    p = PurePosixPath(source_path)
    ext = p.suffix
    stem = p.stem
    parent = p.parent

    # Handle .markdown extension
    if ext == '.markdown':
        new_name = f"{stem}.{language}.markdown"
    else:
        new_name = f"{stem}.{language}.md"

    return str(parent / new_name) if str(parent) != '.' else new_name


def validate_selection(
    files: List[dict],
    max_count: int = MAX_FILE_COUNT,
    max_total_size: int = MAX_TOTAL_SIZE,
) -> Optional[str]:
    """Validate selection against count and size limits.

    Args:
        files: List of file dicts with 'size_bytes' key
        max_count: Maximum number of files allowed
        max_total_size: Maximum total size in bytes

    Returns:
        Error message if validation fails, None if valid
    """
    if len(files) > max_count:
        return f"Selection exceeds maximum file count ({max_count})"

    total_size = sum(f.get('size_bytes', 0) for f in files)
    if total_size > max_total_size:
        return f"Selection exceeds maximum total size ({max_total_size} bytes)"

    return None


def is_default_readme(path: str) -> bool:
    """Check if path is the root README.md.

    Args:
        path: File path to check

    Returns:
        True if this is the root README.md
    """
    return path in ('README.md', 'README.markdown')
