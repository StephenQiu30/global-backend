"""Domain rules for Markdown file classification, selection, and safety validation."""

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

# Security validation pattern (PRD 09)
_SECURITY_TRANSLATED_PATTERN = re.compile(r"\.[a-z]{2}(-[A-Z]{2})?\.md$")
_MARKDOWN_EXTENSIONS = {".md", ".markdown"}


def validate_markdown_path(path: str) -> str:
    """Validate a Markdown file path for safety (PRD 09).

    Returns normalized path on success.
    Raises ValueError with error code as message prefix on failure.
    """
    if not path or not path.strip():
        raise ValueError("empty_path: path is empty or whitespace")

    path = path.strip()

    if ".." in path:
        raise ValueError("path_traversal: path must not contain ..")

    if path.startswith("/"):
        raise ValueError("absolute_path: path must not be absolute")

    dot_pos = path.rfind(".")
    if dot_pos == -1:
        raise ValueError("unsupported_file_type: only .md and .markdown allowed")

    ext = path[dot_pos:].lower()
    if ext not in _MARKDOWN_EXTENSIONS:
        raise ValueError("unsupported_file_type: only .md and .markdown allowed")

    if _SECURITY_TRANSLATED_PATTERN.search(path):
        raise ValueError("translated_variant: translated files cannot be source")

    return path


def is_supported_markdown_path(path: str) -> bool:
    """Check if path has .md or .markdown extension."""
    ext = PurePosixPath(path).suffix.lower()
    return ext in SUPPORTED_EXTENSIONS


def is_translated_variant(path: str) -> bool:
    """Check if path matches language suffix pattern.

    Examples:
        - README.zh-CN.md -> True
        - guide.en.md -> True
        - README.md -> False
    """
    filename = PurePosixPath(path).name
    return bool(TRANSLATED_VARIANT_PATTERN.match(filename))


def is_safe_path(path: str) -> bool:
    """Reject directory traversal and absolute paths."""
    if path.startswith('/'):
        return False
    parts = PurePosixPath(path).parts
    if '..' in parts:
        return False
    return True


def is_in_excluded_directory(path: str) -> bool:
    """Check if path is in an excluded directory."""
    parts = PurePosixPath(path).parts
    return any(part in EXCLUDED_DIRS for part in parts)


def target_translation_path(source_path: str, language: str) -> str:
    """Generate target path with language suffix.

    Examples:
        - README.md + zh-CN -> README.zh-CN.md
        - docs/guide.md + ja -> docs/guide.ja.md
    """
    p = PurePosixPath(source_path)
    ext = p.suffix
    stem = p.stem
    parent = p.parent

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

    Returns error message if validation fails, None if valid.
    """
    if len(files) > max_count:
        return f"Selection exceeds maximum file count ({max_count})"

    total_size = sum(f.get('size_bytes', 0) for f in files)
    if total_size > max_total_size:
        return f"Selection exceeds maximum total size ({max_total_size} bytes)"

    return None


def is_default_readme(path: str) -> bool:
    """Check if path is the root README.md."""
    return path in ('README.md', 'README.markdown')
