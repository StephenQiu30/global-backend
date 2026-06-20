# Design: Markdown 保真翻译保护层

## Architecture

```
┌─────────────────┐     ┌──────────────┐     ┌─────────────────┐
│  Source Markdown │────▶│   protect    │────▶│  Safe Text +    │
│                  │     │  _markdown() │     │  Placeholders   │
└─────────────────┘     └──────────────┘     └────────┬────────┘
                                                       │
                                                       ▼
┌─────────────────┐     ┌──────────────┐     ┌─────────────────┐
│  Final Markdown │◀────│   restore    │◀────│  Translated     │
│                  │     │  _markdown() │     │  Text           │
└─────────────────┘     └──────────────┘     └─────────────────┘
```

## Data Structures

### ProtectedMarkdown

```python
@dataclass
class ProtectedMarkdown:
    text: str                              # Text with placeholders
    placeholders: dict[str, str]           # placeholder_id -> original_content
```

## Key Functions

### protect_markdown(source: str) -> ProtectedMarkdown

1. Extract and protect YAML frontmatter keys
2. Extract and protect fenced code blocks
3. Extract and protect inline code
4. Extract and protect image URLs
5. Extract and protect link URLs
6. Extract and protect HTML comments
7. Extract and protect table separators
8. Extract and protect badge URLs
9. Return ProtectedMarkdown with text and placeholder map

### restore_markdown(translated: str, placeholders: dict[str, str]) -> str

1. Replace all placeholder tokens with original content
2. Return restored Markdown

## Regex Patterns

| Structure | Pattern |
|-----------|---------|
| Fenced code | ````[\s\S]*?```` or ~~~[\s\S]*?~~~ |
| Inline code | `` `[^`]+` `` |
| Link URL | `\[([^\]]*)\]\(([^)]+)\)` |
| Image URL | `!\[([^\]]*)\]\(([^)]+)\)` |
| HTML comment | `<!--[\s\S]*?-->` |
| Frontmatter | `\A---\n([\s\S]*?)\n---` |
| Table separator | `\|[\s\-:]+\|` |
| Badge URL | `https?://img\.shields\.io[^\s)]+` |

## Provider Integration

OpenAITranslationProvider wraps the protect/restore cycle:

1. Call `protect_markdown(source)`
2. Build prompt with fidelity constraints + protected text
3. Call OpenAI API
4. Call `restore_markdown(response, placeholders)`
5. Return final Markdown

## Error Handling

- Placeholder collision: raise ValueError with details
- Restore failure (missing placeholder): log warning, return partial restore
- API failure: propagate original exception

## Rollback

No database changes. Revert code changes to return to previous state.
