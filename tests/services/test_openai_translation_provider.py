"""Tests for OpenAI translation provider with Markdown fidelity.

Covers: prompt constraints, protect/restore integration.
Source: PRD 06, OpenSpec REQ-4.
"""

from unittest.mock import AsyncMock, MagicMock, patch

import pytest

from app.services.translation_provider import OpenAITranslationProvider


class TestPromptConstraints:
    """Test that provider prompt includes required Markdown fidelity constraints."""

    def setup_method(self):
        self.provider = OpenAITranslationProvider(api_key="test-key")

    def test_prompt_includes_preserve_markdown(self):
        prompt = self.provider._build_prompt("Hello", "zh-CN")
        assert "preserve" in prompt.lower() or "Preserve" in prompt

    def test_prompt_includes_do_not_modify_urls(self):
        prompt = self.provider._build_prompt("Hello", "zh-CN")
        assert "URL" in prompt or "url" in prompt.lower()

    def test_prompt_includes_return_only_markdown(self):
        prompt = self.provider._build_prompt("Hello", "zh-CN")
        assert "Markdown" in prompt or "markdown" in prompt.lower()

    def test_prompt_includes_do_not_translate_code(self):
        prompt = self.provider._build_prompt("Hello", "zh-CN")
        assert "code" in prompt.lower()

    def test_prompt_includes_do_not_delete_placeholders(self):
        prompt = self.provider._build_prompt("Hello", "zh-CN")
        assert "placeholder" in prompt.lower()

    def test_prompt_includes_heading_level_constraint(self):
        prompt = self.provider._build_prompt("Hello", "zh-CN")
        assert "heading" in prompt.lower()

    def test_prompt_includes_list_table_constraint(self):
        prompt = self.provider._build_prompt("Hello", "zh-CN")
        assert "list" in prompt.lower() or "table" in prompt.lower()


class TestProtectRestoreIntegration:
    """Test that provider integrates protect_markdown and restore_markdown."""

    def setup_method(self):
        self.provider = OpenAITranslationProvider(api_key="test-key")

    @pytest.mark.asyncio
    @patch("app.services.translation_provider.openai")
    async def test_translate_protects_code_blocks(self, mock_openai):
        """Code blocks should be protected before sending to API."""
        mock_response = MagicMock()
        mock_response.choices = [MagicMock()]
        mock_response.choices[0].message.content = "翻译后的文本"
        mock_openai.AsyncChatCompletion.acreate = AsyncMock(return_value=mock_response)

        source = "Text\n```\ncode\n```\nMore"
        result = await self.provider.translate_markdown(source, "zh-CN")

        # The API should have been called with protected text
        call_args = mock_openai.AsyncChatCompletion.acreate.call_args
        messages = call_args[1]["messages"] if "messages" in call_args[1] else call_args[0][0]
        user_message = [m for m in messages if m["role"] == "user"][0]["content"]
        assert "```" not in user_message or "code" not in user_message

    @pytest.mark.asyncio
    @patch("app.services.translation_provider.openai")
    @patch("app.services.translation_provider.protect_markdown")
    @patch("app.services.translation_provider.restore_markdown")
    async def test_translate_restores_placeholders(self, mock_restore, mock_protect, mock_openai):
        """Placeholders should be restored after API response."""
        from app.services.markdown_fidelity import ProtectedMarkdown

        # Mock protect to return known placeholder
        mock_protect.return_value = ProtectedMarkdown(
            text="Text __MD_PROTECT_test123__ here",
            placeholders={"__MD_PROTECT_test123__": "`code`"},
        )

        # Mock restore to simulate real behavior
        mock_restore.side_effect = lambda text, ph: text.replace(
            "__MD_PROTECT_test123__", "`code`"
        )

        mock_response = MagicMock()
        mock_response.choices = [MagicMock()]
        mock_response.choices[0].message.content = "翻译 __MD_PROTECT_test123__ 文本"
        mock_openai.AsyncChatCompletion.acreate = AsyncMock(return_value=mock_response)

        source = "Text `code` here"
        result = await self.provider.translate_markdown(source, "zh-CN")

        # The code should be restored
        assert "`code`" in result

    @pytest.mark.asyncio
    @patch("app.services.translation_provider.openai")
    async def test_translate_preserves_urls(self, mock_openai):
        """URLs should be preserved through the translate cycle."""
        mock_response = MagicMock()
        mock_response.choices = [MagicMock()]
        mock_response.choices[0].message.content = "访问 [链接](https://example.com) 站点"
        mock_openai.AsyncChatCompletion.acreate = AsyncMock(return_value=mock_response)

        source = "Visit [link](https://example.com) site"
        result = await self.provider.translate_markdown(source, "zh-CN")

        assert "https://example.com" in result


class TestProviderInitialization:
    """Test provider initialization."""

    def test_init_with_api_key(self):
        provider = OpenAITranslationProvider(api_key="sk-test")
        assert provider.api_key == "sk-test"

    def test_init_with_custom_model(self):
        provider = OpenAITranslationProvider(api_key="sk-test", model="gpt-4")
        assert provider.model == "gpt-4"

    def test_default_model(self):
        provider = OpenAITranslationProvider(api_key="sk-test")
        assert provider.model is not None
