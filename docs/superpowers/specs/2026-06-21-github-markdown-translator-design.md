# GitHub Markdown Translator Design

## Decision

Build the first version as a GitHub App backed by a Web application.

The user installs the GitHub App, selects or enters an authorized repository, chooses Markdown files and a target language, then the backend translates the files and submits the result as a Pull Request.

## Repositories

`global-frontend` owns the product UI:

1. GitHub App install entry.
2. Installation callback and authorized repository display.
3. Repository URL input.
4. Markdown file selection.
5. Language selection.
6. Task status and PR result pages.

`global-backend` owns the translation system:

1. GitHub App installation verification.
2. Repository authorization checks.
3. Markdown file scanning.
4. Translation task execution.
5. Markdown fidelity handling.
6. OpenAI translation provider.
7. GitHub branch, commit and PR creation.

## First Version Scope

The first version supports only repositories authorized through the GitHub App.

It does not support arbitrary public repository writes, fork-based PRs, issue comment commands, billing, or automatic PR merge.

## Output Rule

Translated files use same-directory language suffixes:

1. `README.md` -> `README.zh-CN.md`
2. `docs/guide.md` -> `docs/guide.zh-CN.md`

Source files are never overwritten.

## PRD Source

Detailed requirements are split by feature under:

`docs/prd/github-translator/`

Each feature has its own PRD so future implementation can be planned and validated independently.
