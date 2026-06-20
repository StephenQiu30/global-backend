#!/usr/bin/env bash
set -euo pipefail

if ! command -v gh >/dev/null 2>&1; then
  echo "gh CLI is required. Install from https://cli.github.com/" >&2
  exit 1
fi

# Source of truth: .github/repository-metadata.yml
gh repo edit \
  --description "GitHub Markdown Translator 后端：通过 GitHub App 扫描仓库 Markdown、调用翻译模型生成语言后缀文件，并以 Pull Request 提交回 GitHub；支持公开仓库只读预览。" \
  --remove-topic ai-workflow \
  --remove-topic claude-agent \
  --remove-topic global \
  --remove-topic rag \
  --remove-topic sdd \
  --remove-topic symphony \
  --add-topic backend \
  --add-topic fastapi \
  --add-topic github-app \
  --add-topic markdown \
  --add-topic translation \
  --add-topic i18n \
  --add-topic python \
  --add-topic openspec \
  --add-topic tdd

echo "GitHub repository metadata synced from .github/repository-metadata.yml"
