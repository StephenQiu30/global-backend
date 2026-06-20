# Proposal: Markdown File Discovery

## Summary

Implement backend Markdown file scanning and selection restrictions for authorized GitHub repositories. The system will discover `.md` and `.markdown` files, default-select README, exclude generated translation variants, and enforce selection limits.

## Motivation

Users need to select Markdown files for translation. The backend must provide a reliable file discovery mechanism that:
- Scans authorized repositories using GitHub tree APIs
- Identifies eligible Markdown files
- Excludes generated/dependency directories
- Enforces file count and size limits
- Provides target path previews for translation

## Scope

### In Scope
- `.md` and `.markdown` file extensions
- Root `README.md` as default selection
- Language suffix variant exclusion (e.g., `README.zh-CN.md`)
- Directory exclusions: `.git`, `node_modules`, `dist`, `build`, `.next`
- Selection limits: max 10 files, max 200KB total
- Target path preview generation
- Size-based disabled reasons

### Out of Scope
- Translation execution
- PR creation
- Public repository scanning
- Frontend implementation

## Impact

- New domain module: `app/domain/markdown_files.py`
- New service module: `app/services/markdown_discovery.py`
- New API endpoint: `GET /api/repositories/{owner}/{repo}/markdown-files`
- New test files for domain, service, and API layers

## Non-Goals

- Scan `node_modules`, build outputs, or non-Markdown files
- Support arbitrary public repositories
- Implement translation logic

## Success Criteria

1. API returns only eligible Markdown files for authorized repos
2. Root README is marked as default
3. Translation variants are excluded from source file list
4. Selection limits are enforced at backend
5. All tests pass: `pytest tests/domain/test_markdown_files.py tests/services/test_markdown_discovery.py tests/api/test_markdown_files_api.py -v`
