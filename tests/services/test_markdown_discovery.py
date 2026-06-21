"""Tests for Markdown file discovery service."""

import pytest

from app.services.markdown_discovery import (
    discover_markdown_files,
    MarkdownFileInfo,
)


class TestDiscoverMarkdownFiles:
    """Test Markdown file discovery from tree items."""

    def _make_tree_item(self, path: str, size: int = 1024, item_type: str = 'blob'):
        """Helper to create a tree item dict."""
        return {'path': path, 'size': size, 'type': item_type}

    def test_basic_discovery(self):
        """GIVEN a tree with README.md and docs/guide.md THEN both are discovered."""
        tree = [
            self._make_tree_item('README.md', 512),
            self._make_tree_item('docs/guide.md', 1024),
        ]
        result = discover_markdown_files(tree)

        assert len(result) == 2
        assert result[0].path == 'README.md'
        assert result[0].is_default_readme is True
        assert result[1].path == 'docs/guide.md'
        assert result[1].is_default_readme is False

    def test_excludes_translated_variants(self):
        """GIVEN README.zh-CN.md THEN it is excluded from results."""
        tree = [
            self._make_tree_item('README.md', 512),
            self._make_tree_item('README.zh-CN.md', 600),
        ]
        result = discover_markdown_files(tree)

        assert len(result) == 1
        assert result[0].path == 'README.md'

    def test_excludes_non_markdown_files(self):
        """GIVEN src/index.ts THEN it is excluded."""
        tree = [
            self._make_tree_item('README.md', 512),
            self._make_tree_item('src/index.ts', 2048),
        ]
        result = discover_markdown_files(tree)

        assert len(result) == 1
        assert result[0].path == 'README.md'

    def test_excludes_node_modules(self):
        """GIVEN node_modules/pkg/README.md THEN it is excluded."""
        tree = [
            self._make_tree_item('README.md', 512),
            self._make_tree_item('node_modules/pkg/README.md', 1024),
        ]
        result = discover_markdown_files(tree)

        assert len(result) == 1
        assert result[0].path == 'README.md'

    def test_excludes_git_directory(self):
        """GIVEN .git/config.md THEN it is excluded."""
        tree = [
            self._make_tree_item('README.md', 512),
            self._make_tree_item('.git/config.md', 256),
        ]
        result = discover_markdown_files(tree)

        assert len(result) == 1
        assert result[0].path == 'README.md'

    def test_excludes_build_outputs(self):
        """GIVEN dist/README.md, build/README.md, .next/server/page.md THEN all excluded."""
        tree = [
            self._make_tree_item('README.md', 512),
            self._make_tree_item('dist/README.md', 1024),
            self._make_tree_item('build/README.md', 1024),
            self._make_tree_item('.next/server/page.md', 2048),
        ]
        result = discover_markdown_files(tree)

        assert len(result) == 1
        assert result[0].path == 'README.md'

    def test_sorts_readme_first(self):
        """GIVEN docs/a.md, README.md, docs/b.md THEN README is first."""
        tree = [
            self._make_tree_item('docs/a.md', 512),
            self._make_tree_item('README.md', 1024),
            self._make_tree_item('docs/b.md', 768),
        ]
        result = discover_markdown_files(tree)

        assert result[0].path == 'README.md'
        assert result[1].path == 'docs/a.md'
        assert result[2].path == 'docs/b.md'

    def test_sorts_alphabetically(self):
        """GIVEN docs/b.md, docs/a.md, docs/c.md THEN sorted alphabetically."""
        tree = [
            self._make_tree_item('docs/b.md', 512),
            self._make_tree_item('docs/a.md', 512),
            self._make_tree_item('docs/c.md', 512),
        ]
        result = discover_markdown_files(tree)

        assert result[0].path == 'docs/a.md'
        assert result[1].path == 'docs/b.md'
        assert result[2].path == 'docs/c.md'

    def test_marks_default_readme(self):
        """GIVEN README.md THEN is_default_readme is True."""
        tree = [self._make_tree_item('README.md', 512)]
        result = discover_markdown_files(tree)

        assert result[0].is_default_readme is True

    def test_no_default_readme(self):
        """GIVEN only docs/guide.md THEN no file is marked as default."""
        tree = [self._make_tree_item('docs/guide.md', 512)]
        result = discover_markdown_files(tree)

        assert result[0].is_default_readme is False

    def test_generates_target_path_preview(self):
        """GIVEN README.md and language zh-CN THEN target is README.zh-CN.md."""
        tree = [self._make_tree_item('README.md', 512)]
        result = discover_markdown_files(tree, language='zh-CN')

        assert result[0].target_path_preview == 'README.zh-CN.md'

    def test_custom_language_target_path(self):
        """GIVEN docs/guide.md and language ja THEN target is docs/guide.ja.md."""
        tree = [self._make_tree_item('docs/guide.md', 512)]
        result = discover_markdown_files(tree, language='ja')

        assert result[0].target_path_preview == 'docs/guide.ja.md'

    def test_marks_oversized_file_with_disabled_reason(self):
        """GIVEN a file of 300KB with 200KB limit THEN disabled_reason is set."""
        tree = [self._make_tree_item('large.md', 300 * 1024)]
        result = discover_markdown_files(tree, max_total_size=200 * 1024)

        assert result[0].disabled_reason is not None
        assert 'exceeds maximum' in result[0].disabled_reason.lower()

    def test_normal_size_file_no_disabled_reason(self):
        """GIVEN a file of 100KB with 200KB limit THEN disabled_reason is None."""
        tree = [self._make_tree_item('normal.md', 100 * 1024)]
        result = discover_markdown_files(tree, max_total_size=200 * 1024)

        assert result[0].disabled_reason is None

    def test_skips_tree_entries(self):
        """GIVEN a tree entry (type: tree) THEN it is skipped."""
        tree = [
            self._make_tree_item('docs', 0, 'tree'),
            self._make_tree_item('README.md', 512),
        ]
        result = discover_markdown_files(tree)

        assert len(result) == 1
        assert result[0].path == 'README.md'

    def test_target_exists_when_preview_path_in_tree(self):
        """GIVEN target translation path exists in tree THEN target_exists is True."""
        tree = [
            self._make_tree_item("README.md", 512),
            self._make_tree_item("README.zh-CN.md", 600),
        ]
        result = discover_markdown_files(tree, language="zh-CN")

        assert len(result) == 1
        assert result[0].target_path_preview == "README.zh-CN.md"
        assert result[0].target_exists is True

    def test_full_scenario(self):
        """GIVEN a realistic tree THEN correct files are discovered and sorted."""
        tree = [
            self._make_tree_item('README.md', 2048),
            self._make_tree_item('README.zh-CN.md', 2500),
            self._make_tree_item('README.en.md', 2200),
            self._make_tree_item('docs/api/reference.md', 4096),
            self._make_tree_item('docs/guide.md', 1024),
            self._make_tree_item('src/index.ts', 512),
            self._make_tree_item('node_modules/pkg/README.md', 8192),
            self._make_tree_item('.git/config.md', 256),
            self._make_tree_item('dist/README.md', 1024),
            self._make_tree_item('build/README.md', 1024),
            self._make_tree_item('.next/server/page.md', 2048),
        ]
        result = discover_markdown_files(tree)

        assert len(result) == 3
        assert result[0].path == 'README.md'
        assert result[0].is_default_readme is True
        assert result[1].path == 'docs/api/reference.md'
        assert result[2].path == 'docs/guide.md'

    def test_markdown_extension_supported(self):
        """GIVEN README.markdown THEN it is discovered."""
        tree = [self._make_tree_item('README.markdown', 512)]
        result = discover_markdown_files(tree)

        assert len(result) == 1
        assert result[0].path == 'README.markdown'
        assert result[0].is_default_readme is True
