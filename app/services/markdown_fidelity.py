"""Markdown fidelity protection service.

Protects non-translatable Markdown spans with placeholders before translation,
then restores them after translation to preserve structure.

Source: PRD 06, OpenSpec REQ-1 through REQ-6.
"""

import re
import uuid
from dataclasses import dataclass, field

PLACEHOLDER_PREFIX = "__MD_PROTECT_"
PLACEHOLDER_SUFFIX = "__"

# Combined regex with named groups for single-pass matching.
# Order matters: longer/more specific patterns first.
_COMBINED = re.compile(
    r"(?P<fenced_code_backtick>```[\s\S]*?```)"
    r"|(?P<fenced_code_tilde>~~~[\s\S]*?~~~)"
    r"|(?P<html_comment><!--[\s\S]*?-->)"
    r"|(?P<inline_code>`[^`\n]+`)"
    r"|(?P<image_url>!\[(?P<image_url_alt>[^\]]*)\]\((?P<image_url_url>[^)]+)\))"
    r"|(?P<link_url>\[(?P<link_url_label>[^\]]*)\]\((?P<link_url_url>[^)]+)\))",
    re.MULTILINE,
)


def _make_placeholder() -> str:
    """Generate a unique placeholder token."""
    return f"{PLACEHOLDER_PREFIX}{uuid.uuid4().hex[:8]}{PLACEHOLDER_SUFFIX}"


@dataclass
class ProtectedMarkdown:
    """Result of protecting Markdown text.

    Attributes:
        text: Markdown text with placeholders replacing protected spans.
        placeholders: Mapping from placeholder token to original content.
    """

    text: str
    placeholders: dict[str, str] = field(default_factory=dict)


def protect_markdown(source: str) -> ProtectedMarkdown:
    """Replace non-translatable Markdown spans with unique placeholders.

    Protects: fenced code, inline code, URLs, image URLs, HTML comments.
    Link labels and image alt text remain translatable.

    Uses single-pass matching to avoid double-processing of nested patterns.

    Args:
        source: Raw Markdown text.

    Returns:
        ProtectedMarkdown with placeholders in place of protected spans.
    """
    placeholders: dict[str, str] = {}

    def _replace(match: re.Match) -> str:
        if match.group("fenced_code_backtick") is not None:
            placeholder = _make_placeholder()
            placeholders[placeholder] = match.group("fenced_code_backtick")
            return placeholder
        if match.group("fenced_code_tilde") is not None:
            placeholder = _make_placeholder()
            placeholders[placeholder] = match.group("fenced_code_tilde")
            return placeholder
        if match.group("html_comment") is not None:
            placeholder = _make_placeholder()
            placeholders[placeholder] = match.group("html_comment")
            return placeholder
        if match.group("inline_code") is not None:
            placeholder = _make_placeholder()
            placeholders[placeholder] = match.group("inline_code")
            return placeholder
        if match.group("image_url") is not None:
            # Protect only URL, keep alt text translatable
            alt = match.group("image_url_alt")  # group 6
            url = match.group("image_url_url")  # group 7
            placeholder = _make_placeholder()
            placeholders[placeholder] = url
            return f"![{alt}]({placeholder})"
        if match.group("link_url") is not None:
            # Protect only URL, keep label translatable
            label = match.group("link_url_label")  # group 8
            url = match.group("link_url_url")  # group 9
            placeholder = _make_placeholder()
            placeholders[placeholder] = url
            return f"[{label}]({placeholder})"
        return match.group(0)  # fallback, should not happen

    result = _COMBINED.sub(_replace, source)
    return ProtectedMarkdown(text=result, placeholders=placeholders)


def restore_markdown(translated: str, placeholders: dict[str, str]) -> str:
    """Restore placeholder tokens with their original content.

    Args:
        translated: Text containing placeholder tokens.
        placeholders: Mapping from placeholder token to original content.

    Returns:
        Markdown with all placeholders replaced by original content.
    """
    result = translated
    for placeholder, original in placeholders.items():
        result = result.replace(placeholder, original)
    return result
