# Specs: GitHub 分支、文件写入与 PR 创建

## S1: Branch Creation

- `create_branch(installation_id, full_name, base_branch, branch_name)` MUST create a branch from the default branch latest SHA.
- If the branch already exists, the method MUST return the existing branch safely.
- Branch name format: `translate/{language}/{task_id}`.

## S2: File Write

- `put_file(installation_id, full_name, branch, path, content, message)` MUST base64-encode content before sending to GitHub API.
- MUST support updating an existing target file by fetching its SHA first.
- MUST reject source paths; only accept target language suffix paths (e.g., `README.zh-CN.md`).
- Multiple files in one task MUST go into the same branch.

## S3: PR Creation

- `create_pull_request(installation_id, full_name, title, body, head, base)` MUST create a PR with head as translation branch and base as default branch.
- MUST return `url` and `number`.
- If an open PR already exists for the same branch, MUST return the existing PR.
- PR title format: `docs: add {language} translation for Markdown docs`.

## S4: PR Body

- `build_translation_pr_body(language, mappings, provider_name, task_id)` MUST return valid Markdown.
- Body MUST contain: auto-translation disclaimer, target language, file mappings, provider name, review reminder, task ID.

## S5: Task Runner PR Flow

- Task runner MUST complete translation of ALL selected files before calling `create_branch`.
- If any translation fails, NO branch, file write, or PR MUST be created.
- Multi-file translation MUST create exactly one branch and one PR.
- PR file list MUST only contain target translation files.

## S6: Error Handling

- GitHub API errors (rate limit, permission denied, not found) MUST be mapped to structured `AppError`.
- Failed writes MUST NOT leave a half-finished PR.
