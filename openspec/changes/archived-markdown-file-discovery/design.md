# Design: Markdown File Discovery

## Architecture

The implementation follows a layered architecture:

1. **Domain Layer** (`app/domain/markdown_files.py`): Pure business rules for file classification
2. **Service Layer** (`app/services/markdown_discovery.py`): GitHub API integration and file discovery
3. **API Layer** (`app/api/repositories.py`): HTTP endpoint with authorization checks

## Domain Layer Design

### Core Functions

```python
def is_supported_markdown_path(path: str) -> bool:
    """Check if path has .md or .markdown extension."""

def is_translated_variant(path: str) -> bool:
    """Check if path matches language suffix pattern (e.g., README.zh-CN.md)."""

def is_safe_path(path: str) -> bool:
    """Reject directory traversal and absolute paths."""

def target_translation_path(source_path: str, language: str) -> str:
    """Generate target path with language suffix."""

def validate_selection(files: list, max_count: int = 10, max_size: int = 200 * 1024) -> None:
    """Validate selection against count and size limits."""
```

### Pattern Matching

Translated variant detection uses regex pattern:
```
^(.+)\.([a-z]{2}(?:-[A-Z]{2})?)\.md$
```

Examples:
- `README.zh-CN.md` -> matches (base: `README`, lang: `zh-CN`)
- `guide.en.md` -> matches (base: `guide`, lang: `en`)
- `README.md` -> no match

## Service Layer Design

### Discovery Flow

1. Fetch repository tree from GitHub API
2. Filter excluded directories (`.git`, `node_modules`, `dist`, `build`, `.next`)
3. Filter supported extensions (`.md`, `.markdown`)
4. Exclude translated variants
5. Sort: root README first, then alphabetical by path
6. Mark default README
7. Apply size limits and mark disabled files

### GitHub Tree API Integration

Use `GET /repos/{owner}/{repo}/git/trees/{branch}?recursive=1` to get full tree.

Response processing:
- Filter `tree` array for `type: "blob"`
- Check each path against exclusion rules
- Apply extension and variant filters

### Result Structure

```python
@dataclass
class MarkdownFileInfo:
    path: str
    size_bytes: int
    is_default_readme: bool
    is_translated_variant: bool
    disabled_reason: Optional[str]
    target_path_preview: str
    target_exists: bool
```

## API Layer Design

### Endpoint

```
GET /api/repositories/{owner}/{repo}/markdown-files
```

### Query Parameters

- `language` (optional, default: `zh-CN`): Target language for path previews

### Request Flow

1. Extract `installation_id` from request context
2. Verify repository authorization
3. Call discovery service
4. Return file list with metadata

### Error Responses

- `404 repository_not_installed`: Repository not authorized
- `500 github_api_error`: GitHub API failure

## State Flow

```
Request -> Authorization Check -> GitHub Tree Fetch -> Filter & Sort -> Response
```

## Failure Paths

1. **GitHub API failure**: Return 500 with error message
2. **No Markdown files**: Return empty list (not an error)
3. **No README**: Return list without default selection
4. **Oversized files**: Include with `disabled_reason`, don't drop

## Rollback Impact

- No database changes
- No external state modifications
- Pure read-only operation
