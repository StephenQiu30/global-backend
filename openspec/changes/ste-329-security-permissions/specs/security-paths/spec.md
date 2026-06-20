# Spec: Security Paths

## Requirements

1. Paths containing `..` must be rejected with `ValueError`
2. Absolute paths starting with `/` must be rejected with `ValueError`
3. Files with extensions other than `.md` or `.markdown` must be rejected
4. Translated variant files (e.g., `README.zh-CN.md`) must be rejected from source selection
5. Valid Markdown paths must be returned normalized

## Test Cases

- `../README.md` -> rejected (path traversal)
- `/README.md` -> rejected (absolute path)
- `README.txt` -> rejected (not Markdown)
- `README.zh-CN.md` -> rejected (translated variant)
- `docs/README.md` -> accepted (valid relative Markdown)
- `README.markdown` -> accepted (valid extension)
