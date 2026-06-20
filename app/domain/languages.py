"""Domain models for supported languages."""

from pydantic import BaseModel


class Language(BaseModel):
    """Language model with code and display label."""

    code: str
    label: str


class InvalidLanguageError(Exception):
    """Raised when a language code is not supported."""

    pass


SUPPORTED_LANGUAGES: list[Language] = [
    Language(code="zh-CN", label="简体中文"),
    Language(code="zh-TW", label="繁体中文"),
    Language(code="en", label="English"),
    Language(code="ja", label="日本語"),
    Language(code="ko", label="한국어"),
    Language(code="fr", label="Français"),
    Language(code="de", label="Deutsch"),
    Language(code="es", label="Español"),
]


def validate_language_code(code: str) -> bool:
    """Validate if a language code is supported.

    Args:
        code: Language code to validate

    Returns:
        True if language is supported, False otherwise
    """
    return any(lang.code == code for lang in SUPPORTED_LANGUAGES)
