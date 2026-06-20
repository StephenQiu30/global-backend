"""Tests for TranslationProvider protocol and FakeTranslationProvider."""

import pytest
from app.services.translation_provider import TranslationProvider, FakeTranslationProvider


class TestTranslationProviderProtocol:
    """Tests for TranslationProvider protocol compliance."""

    def test_protocol_has_translate_markdown_method(self):
        """TranslationProvider protocol must define translate_markdown."""
        assert hasattr(TranslationProvider, 'translate_markdown')


class TestFakeTranslationProvider:
    """Tests for FakeTranslationProvider."""

    @pytest.mark.asyncio
    async def test_translate_returns_prefixed_content(self):
        provider = FakeTranslationProvider()
        result = await provider.translate_markdown("# Hello", "zh-CN")
        assert "[zh-CN]" in result
        assert "Hello" in result

    @pytest.mark.asyncio
    async def test_translate_different_languages(self):
        provider = FakeTranslationProvider()
        result_zh = await provider.translate_markdown("# Title", "zh-CN")
        result_ja = await provider.translate_markdown("# Title", "ja")
        assert "[zh-CN]" in result_zh
        assert "[ja]" in result_ja

    @pytest.mark.asyncio
    async def test_translate_preserves_original_content(self):
        provider = FakeTranslationProvider()
        source = "# My Document\n\nSome content here."
        result = await provider.translate_markdown(source, "zh-CN")
        assert "My Document" in result
        assert "Some content here." in result
