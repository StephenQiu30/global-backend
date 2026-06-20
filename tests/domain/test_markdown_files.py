"""Tests for Markdown file domain rules."""

import pytest

from app.domain.markdown_files import (
    is_supported_markdown_path,
    is_translated_variant,
    is_safe_path,
    is_in_excluded_directory,
    target_translation_path,
    validate_selection,
    is_default_readme,
    MAX_FILE_COUNT,
    MAX_TOTAL_SIZE,
)


class TestIsSupportedMarkdownPath:
    """Test extension support detection."""

    def test_md_extension(self):
        """GIVEN a file path docs/guide.md THEN it is supported."""
        assert is_supported_markdown_path('docs/guide.md') is True

    def test_markdown_extension(self):
        """GIVEN a file path README.markdown THEN it is supported."""
        assert is_supported_markdown_path('README.markdown') is True

    def test_uppercase_extension(self):
        """GIVEN a file path README.MD THEN it is supported (case insensitive)."""
        assert is_supported_markdown_path('README.MD') is True

    def test_unsupported_extension(self):
        """GIVEN a file path src/index.ts THEN it is NOT supported."""
        assert is_supported_markdown_path('src/index.ts') is False

    def test_no_extension(self):
        """GIVEN a file path Makefile THEN it is NOT supported."""
        assert is_supported_markdown_path('Makefile') is False

    def test_nested_md_file(self):
        """GIVEN a file path docs/api/reference.md THEN it is supported."""
        assert is_supported_markdown_path('docs/api/reference.md') is True


class TestIsTranslatedVariant:
    """Test translated variant detection."""

    def test_chinese_variant(self):
        """GIVEN README.zh-CN.md THEN it is a translated variant."""
        assert is_translated_variant('README.zh-CN.md') is True

    def test_english_variant(self):
        """GIVEN docs/guide.en.md THEN it is a translated variant."""
        assert is_translated_variant('docs/guide.en.md') is True

    def test_japanese_variant(self):
        """GIVEN README.ja.md THEN it is a translated variant."""
        assert is_translated_variant('README.ja.md') is True

    def test_not_a_variant(self):
        """GIVEN README.md THEN it is NOT a translated variant."""
        assert is_translated_variant('README.md') is False

    def test_regular_file(self):
        """GIVEN docs/guide.md THEN it is NOT a translated variant."""
        assert is_translated_variant('docs/guide.md') is False

    def test_complex_language_code(self):
        """GIVEN README.pt-BR.md THEN it is a translated variant."""
        assert is_translated_variant('README.pt-BR.md') is True


class TestIsSafePath:
    """Test path safety validation."""

    def test_relative_path(self):
        """GIVEN docs/guide.md THEN it is safe."""
        assert is_safe_path('docs/guide.md') is True

    def test_directory_traversal(self):
        """GIVEN ../../../etc/passwd.md THEN it is NOT safe."""
        assert is_safe_path('../../../etc/passwd.md') is False

    def test_absolute_path(self):
        """GIVEN /etc/passwd.md THEN it is NOT safe."""
        assert is_safe_path('/etc/passwd.md') is False

    def test_traversal_in_middle(self):
        """GIVEN docs/../../../etc/passwd.md THEN it is NOT safe."""
        assert is_safe_path('docs/../../../etc/passwd.md') is False

    def test_simple_filename(self):
        """GIVEN README.md THEN it is safe."""
        assert is_safe_path('README.md') is True


class TestIsInExcludedDirectory:
    """Test excluded directory detection."""

    def test_node_modules(self):
        """GIVEN node_modules/pkg/README.md THEN it is excluded."""
        assert is_in_excluded_directory('node_modules/pkg/README.md') is True

    def test_git_directory(self):
        """GIVEN .git/config.md THEN it is excluded."""
        assert is_in_excluded_directory('.git/config.md') is True

    def test_dist_directory(self):
        """GIVEN dist/README.md THEN it is excluded."""
        assert is_in_excluded_directory('dist/README.md') is True

    def test_build_directory(self):
        """GIVEN build/README.md THEN it is excluded."""
        assert is_in_excluded_directory('build/README.md') is True

    def test_next_directory(self):
        """GIVEN .next/server/page.md THEN it is excluded."""
        assert is_in_excluded_directory('.next/server/page.md') is True

    def test_normal_directory(self):
        """GIVEN docs/guide.md THEN it is NOT excluded."""
        assert is_in_excluded_directory('docs/guide.md') is False

    def test_similar_name_not_excluded(self):
        """GIVEN my_node_modules/README.md THEN it is NOT excluded."""
        assert is_in_excluded_directory('my_node_modules/README.md') is False


class TestTargetTranslationPath:
    """Test target path generation."""

    def test_root_readme(self):
        """GIVEN README.md and zh-CN THEN target is README.zh-CN.md."""
        assert target_translation_path('README.md', 'zh-CN') == 'README.zh-CN.md'

    def test_nested_file(self):
        """GIVEN docs/guide.md and ja THEN target is docs/guide.ja.md."""
        assert target_translation_path('docs/guide.md', 'ja') == 'docs/guide.ja.md'

    def test_markdown_extension(self):
        """GIVEN README.markdown and zh-CN THEN target is README.zh-CN.markdown."""
        assert target_translation_path('README.markdown', 'zh-CN') == 'README.zh-CN.markdown'

    def test_deeply_nested(self):
        """GIVEN docs/api/reference.md and en THEN target is docs/api/reference.en.md."""
        assert target_translation_path('docs/api/reference.md', 'en') == 'docs/api/reference.en.md'


class TestValidateSelection:
    """Test selection limit validation."""

    def test_within_limits(self):
        """GIVEN 5 files totaling 100KB THEN validation passes."""
        files = [{'size_bytes': 20 * 1024} for _ in range(5)]
        assert validate_selection(files) is None

    def test_exceeds_file_count(self):
        """GIVEN 11 files THEN validation fails with count error."""
        files = [{'size_bytes': 1024} for _ in range(11)]
        result = validate_selection(files)
        assert result is not None
        assert 'file count' in result.lower()

    def test_exceeds_total_size(self):
        """GIVEN 5 files totaling 250KB THEN validation fails with size error."""
        files = [{'size_bytes': 50 * 1024} for _ in range(5)]
        result = validate_selection(files)
        assert result is not None
        assert 'total size' in result.lower()

    def test_custom_limits(self):
        """GIVEN custom limits of 3 files and 50KB THEN validation respects them."""
        files = [{'size_bytes': 20 * 1024} for _ in range(4)]
        result = validate_selection(files, max_count=3)
        assert result is not None
        assert 'file count' in result.lower()

    def test_empty_selection(self):
        """GIVEN empty list THEN validation passes."""
        assert validate_selection([]) is None


class TestIsDefaultReadme:
    """Test default README detection."""

    def test_root_readme_md(self):
        """GIVEN README.md THEN it is default readme."""
        assert is_default_readme('README.md') is True

    def test_root_readme_markdown(self):
        """GIVEN README.markdown THEN it is default readme."""
        assert is_default_readme('README.markdown') is True

    def test_nested_readme(self):
        """GIVEN docs/README.md THEN it is NOT default readme."""
        assert is_default_readme('docs/README.md') is False

    def test_translated_variant(self):
        """GIVEN README.zh-CN.md THEN it is NOT default readme."""
        assert is_default_readme('README.zh-CN.md') is False
