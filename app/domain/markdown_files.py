"""Domain validators for Markdown file paths."""

import re

_MARKDOWN_EXTENSIONS = {".md", ".markdown"}
_TRANSLATED_VARIANT_PATTERN = re.compile(r"\.[a-z]{2}(-[A-Z]{2})?\.md$")


def validate_markdown_path(path: str) -> str:
    """Validate a Markdown file path for safety.

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

    if _TRANSLATED_VARIANT_PATTERN.search(path):
        raise ValueError("translated_variant: translated files cannot be source")

    return path
