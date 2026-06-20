"""Translation provider protocol, fake implementation, and OpenAI provider with Markdown fidelity."""

from typing import Protocol, runtime_checkable

from app.services.markdown_fidelity import protect_markdown, restore_markdown

try:
    import openai
except ImportError:
    openai = None  # Allow import without openai installed (tests mock it)


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


# Required prompt constraints from PRD 06
_FIDELITY_CONSTRAINTS = """\
CRITICAL Markdown fidelity rules - you MUST follow ALL of these:
1. Preserve Markdown structure exactly as given.
2. Do NOT translate content inside code blocks or inline code.
3. Do NOT modify any URLs, links, or image paths.
4. Do NOT delete, modify, or reorder any placeholder tokens like __MD_PROTECT_*__.
5. Do NOT change heading levels (# ## ### etc.).
6. Maintain list formatting (bullets, numbering) and table structure.
7. Return ONLY the translated Markdown - no explanations, no code fences around your output.
"""


class OpenAITranslationProvider:
    """Translates Markdown text using OpenAI with fidelity protection.

    Integrates the protect/restore cycle: protects non-translatable spans
    before API call, restores them after.
    """

    def __init__(self, api_key: str, model: str = "gpt-4o-mini") -> None:
        self.api_key = api_key
        self.model = model

    def _build_prompt(self, source: str, target_language: str) -> str:
        """Build the translation prompt with fidelity constraints."""
        return (
            f"Translate the following Markdown text to {target_language}.\n\n"
            f"{_FIDELITY_CONSTRAINTS}\n"
            f"Markdown to translate:\n\n{source}"
        )

    async def translate_markdown(self, source: str, target_language: str) -> str:
        """Translate Markdown with fidelity protection.

        Args:
            source: Raw Markdown text to translate.
            target_language: Target language code (e.g., 'zh-CN').

        Returns:
            Translated Markdown with protected spans restored.
        """
        if openai is None:
            raise RuntimeError("openai package is required for translation")

        # Step 1: Protect non-translatable spans
        protected = protect_markdown(source)

        # Step 2: Build prompt with constraints
        prompt = self._build_prompt(protected.text, target_language)

        # Step 3: Call OpenAI API
        response = await openai.AsyncChatCompletion.acreate(
            model=self.model,
            messages=[
                {"role": "system", "content": "You are a Markdown translator."},
                {"role": "user", "content": prompt},
            ],
            temperature=0.3,
        )
        translated_text = response.choices[0].message.content

        # Step 4: Restore placeholders
        result = restore_markdown(translated_text, protected.placeholders)

        return result
