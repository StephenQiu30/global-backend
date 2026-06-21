# Specs: Markdown 保真翻译保护层

## Requirements

### REQ-1: Protected Spans Identification

The system SHALL identify and protect the following Markdown structures:

1. Fenced code blocks (``` and ~~~)
2. Inline code (`backtick`)
3. Markdown link URLs `[text](url)`
4. Markdown image URLs `![alt](url)`
5. HTML comments `<!-- ... -->`
6. YAML frontmatter keys (lines before first `---` closing)
7. Markdown table separator rows (`|---|---|`)
8. Badge URLs (shields.io, img.shields.io patterns)
9. Relative links (paths starting with `./` or `../`)

### REQ-2: Placeholder Generation

The system SHALL generate unique placeholders using UUID-based tokens with a recognizable prefix (e.g., `__MD_PROTECT_<uuid>__`) to avoid collision with user content.

### REQ-3: Round-trip Fidelity

Protected spans MUST survive the protect-translate-restore cycle without modification:

```
original_protected_span == restore(protect(original_text))
```

### REQ-4: Provider Prompt Constraints

The translation provider prompt MUST include:

1. "Preserve Markdown structure"
2. "Do not modify URLs"
3. "Do not translate code"
4. "Return only Markdown"
5. "Do not delete placeholders"
6. "Do not change heading levels"
7. "Maintain list and table formatting"

### REQ-5: Translatable Content

The system SHALL translate:

1. Heading text
2. Paragraph text
3. List item natural language
4. Table cell natural language
5. Link label text
6. Image alt text
7. Blockquote natural language

### REQ-6: Structure Validation

After restore, the system SHOULD perform lightweight validation:

1. Heading levels preserved
2. Code block delimiters intact
3. Table structure maintained

## Scenarios

### Success: Code block preserved

Given a Markdown document with a fenced code block,
When the document is protected and restored,
Then the code block content is identical to the original.

### Success: URL preserved

Given a Markdown document with links and images,
When the document is protected and restored,
Then all URLs are unchanged.

### Success: Frontmatter preserved

Given a Markdown document with YAML frontmatter,
When the document is protected and restored,
Then frontmatter keys are unchanged.

### Failure: Placeholder collision

Given a document containing text matching the placeholder pattern,
When protection is applied,
Then the system MUST use a different placeholder prefix or detect the collision.

## Validation Evidence

- Automated: `pytest tests/services/test_markdown_fidelity*.py tests/services/test_openai_translation_provider.py -v`
- Manual: Complex Markdown fixture with all protected structures
