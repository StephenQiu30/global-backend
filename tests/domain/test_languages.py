"""Tests for language domain models."""

import pytest
from app.domain.languages import (
    Language,
    SUPPORTED_LANGUAGES,
    validate_language_code,
    InvalidLanguageError,
)


class TestLanguage:
    """Tests for Language model."""

    def test_create_language(self):
        lang = Language(code="zh-CN", label="简体中文")
        assert lang.code == "zh-CN"
        assert lang.label == "简体中文"

    def test_language_from_dict(self):
        data = {"code": "en", "label": "English"}
        lang = Language(**data)
        assert lang.code == "en"
        assert lang.label == "English"


class TestSupportedLanguages:
    """Tests for SUPPORTED_LANGUAGES constant."""

    def test_contains_zh_cn(self):
        codes = [lang.code for lang in SUPPORTED_LANGUAGES]
        assert "zh-CN" in codes

    def test_contains_zh_tw(self):
        codes = [lang.code for lang in SUPPORTED_LANGUAGES]
        assert "zh-TW" in codes

    def test_contains_en(self):
        codes = [lang.code for lang in SUPPORTED_LANGUAGES]
        assert "en" in codes

    def test_contains_ja(self):
        codes = [lang.code for lang in SUPPORTED_LANGUAGES]
        assert "ja" in codes

    def test_contains_ko(self):
        codes = [lang.code for lang in SUPPORTED_LANGUAGES]
        assert "ko" in codes

    def test_contains_fr(self):
        codes = [lang.code for lang in SUPPORTED_LANGUAGES]
        assert "fr" in codes

    def test_contains_de(self):
        codes = [lang.code for lang in SUPPORTED_LANGUAGES]
        assert "de" in codes

    def test_contains_es(self):
        codes = [lang.code for lang in SUPPORTED_LANGUAGES]
        assert "es" in codes

    def test_exactly_eight_languages(self):
        assert len(SUPPORTED_LANGUAGES) == 8


class TestValidateLanguageCode:
    """Tests for validate_language_code function."""

    def test_valid_zh_cn(self):
        assert validate_language_code("zh-CN") is True

    def test_valid_zh_tw(self):
        assert validate_language_code("zh-TW") is True

    def test_valid_en(self):
        assert validate_language_code("en") is True

    def test_valid_ja(self):
        assert validate_language_code("ja") is True

    def test_valid_ko(self):
        assert validate_language_code("ko") is True

    def test_valid_fr(self):
        assert validate_language_code("fr") is True

    def test_valid_de(self):
        assert validate_language_code("de") is True

    def test_valid_es(self):
        assert validate_language_code("es") is True

    def test_invalid_empty_string(self):
        assert validate_language_code("") is False

    def test_invalid_unknown_code(self):
        assert validate_language_code("xx") is False

    def test_invalid_similar_code(self):
        assert validate_language_code("zh") is False

    def test_invalid_uppercase(self):
        assert validate_language_code("ZH-CN") is False


class TestInvalidLanguageError:
    """Tests for InvalidLanguageError exception."""

    def test_error_is_exception(self):
        assert issubclass(InvalidLanguageError, Exception)

    def test_error_with_message(self):
        error = InvalidLanguageError("unsupported language: xx")
        assert str(error) == "unsupported language: xx"

    def test_error_can_be_raised(self):
        with pytest.raises(InvalidLanguageError):
            raise InvalidLanguageError("test error")
