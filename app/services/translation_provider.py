"""Translation provider protocol and fake implementation."""

from typing import Protocol, runtime_checkable


@runtime_checkable
class TranslationProvider(Protocol):
    """Protocol for translation providers."""

    async def translate_markdown(self, source_content: str, target_language: str) -> str:
        """Translate markdown content to target language.

        Args:
            source_content: Source markdown content
            target_language: Target language code

        Returns:
            Translated markdown content
        """
        ...


class FakeTranslationProvider:
    """Fake translation provider for testing."""

    async def translate_markdown(self, source_content: str, target_language: str) -> str:
        """Return content with language prefix for testing.

        Args:
            source_content: Source markdown content
            target_language: Target language code

        Returns:
            Content prefixed with language tag
        """
        return f"[{target_language}] {source_content}"
