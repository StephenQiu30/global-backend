# CLAUDE.local.md

本文件用于记录放在具体项目中的局部规范性配置，与 `CLAUDE.md` 中的全局协作规则进行区分。

## 使用边界

1. `CLAUDE.md` 存放长期稳定的 Claude 全局规则、角色协作原则和交付格式。
2. `CLAUDE.local.md` 存放当前项目特有的规范、路径、命令、环境约束和临时协作约定。
3. 当局部规范与全局规则冲突时，应优先确认项目上下文，并以更具体、更贴近当前项目的规则为准。

## 当前项目规范

1. 本项目是 `global-backend`，GitHub Markdown Translator 的后端实现（FastAPI + GitHub App + OpenAI 翻译）。
2. 后端实现、接口、数据模型、权限和运行命令记录在本文件或 `docs/` 的对应分类中。
3. 本项目内的角色配置放在 `.claude/agents/` 目录。
4. 本项目内的可复用流程放在 `.claude/skills/` 目录。
5. 长期后端行为和协作边界优先沉淀到 `openspec/`，任务执行时先更新 OpenSpec artifacts，再进入实现和验证。
6. `docs/` 目录保留分类结构和 README 骨架，正文文档按任务需要归档。

## 常用命令

```bash
# 安装与启动
pip install -e ".[dev]"
python -m app

# Docker 一体化启动
docker compose up --build

# 测试与校验
pytest tests/ -v
scripts/validate-repository.sh

# 同步 GitHub 仓库 About 信息
scripts/sync-github-metadata.sh
```

## 关键路径

- 应用进程入口：`app/runner.py`（通过 `python -m app` 启动）
- FastAPI 应用工厂：`app/main.py`
- 配置：`app/core/config.py`、`.env`
- PRD：`docs/prd/github-translator/`
- 本地开发说明：`docs/operations/local-development.md`
- 仓库 About 元数据：`.github/repository-metadata.yml`
