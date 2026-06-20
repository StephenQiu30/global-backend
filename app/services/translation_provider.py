"""OpenAI translation provider with Markdown fidelity integration.

Wraps the protect/restore cycle and enforces Markdown structure constraints
in the translation prompt.

Source: PRD 06, OpenSpec REQ-4, REQ-5.
"""

from app.services.markdown_fidelity import protect_markdown, restore_markdown

try:
    import openai
except ImportError:
    openai = None  # Allow import without openai installed (tests mock it)

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

    def translate(self, source: str, target_language: str) -> str:
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
        response = openai.ChatCompletion.create(
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
