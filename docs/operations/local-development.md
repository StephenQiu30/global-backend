---
layer: Operations
doc_no: "001"
audience: Dev
feature_area: github-markdown-translator
purpose: 记录 global-backend 本地开发、测试与 GitHub 仓库元数据同步方式
canonical_path: docs/operations/local-development.md
status: accepted
version: "1.0"
owner: global-backend
inputs:
  - README.md
  - .env.example
outputs:
  - 本地启动与验证命令
  - GitHub About 信息同步流程
triggers:
  - 新成员 onboarding
  - 更新仓库描述或 topics
  - 调整本地运行方式
downstream: []
---

# 本地开发与仓库元数据

## 环境要求

- Python 3.12+
- GitHub App（已创建并安装到测试仓库）
- OpenAI API Key（启用真实翻译时）

## 本地启动

```bash
python -m venv .venv
source .venv/bin/activate
pip install -e ".[dev]"
cp .env.example .env
# 编辑 .env，填写 GITHUB_APP_ID、GITHUB_PRIVATE_KEY 等
uvicorn app.main:app --reload --port 8000
```

服务启动后：

- API 根路径：`http://127.0.0.1:8000`
- OpenAPI 文档：`http://127.0.0.1:8000/docs`

## 常用验证命令

```bash
# 全量测试
pytest tests/ -v

# 仓库结构与治理文件检查
scripts/validate-repository.sh

# 同步 GitHub 仓库 About 信息（描述与 topics）
scripts/sync-github-metadata.sh
```

## GitHub 仓库元数据

仓库描述与 topics 的源文件为 [`.github/repository-metadata.yml`](../../.github/repository-metadata.yml)。

修改该文件后执行 `scripts/sync-github-metadata.sh`，将 description 和 topics 推送到 GitHub。需要已登录 `gh` CLI 且对仓库有 admin 权限。

## 相关文档

- [README.md](../../README.md)
- [GitHub Markdown Translator PRD 索引](../prd/github-translator/README.md)
