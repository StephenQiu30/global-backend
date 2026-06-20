# global-backend

GitHub Markdown Translator 的后端服务。通过 GitHub App 读取已授权仓库的 Markdown 文件，调用翻译模型生成同目录语言后缀文件（例如 `README.md` → `README.zh-CN.md`），并以 Pull Request 提交回 GitHub；同时支持公开仓库的只读翻译预览。

配套前端仓库：[global-frontend](https://github.com/StephenQiu30/global-frontend)（Next.js）。

## 功能概览

| 能力 | 说明 |
| --- | --- |
| GitHub App 安装校验 | 验证 installation，列出已授权仓库 |
| 仓库解析与授权 | 解析 GitHub URL / `owner/repo`，校验是否已安装 App |
| Markdown 文件发现 | 扫描仓库 Markdown，默认选中根目录 `README.md`，支持多选与选择上限 |
| 目标语言 | 支持 `zh-CN`、`zh-TW`、`en`、`ja`、`ko`、`fr`、`de`、`es` |
| 翻译任务 | 读取源文件、Markdown 保真翻译、创建分支、写入文件、创建 PR |
| 任务结果 | 结构化成功/失败响应，错误码可映射 HTTP 状态 |
| 公开仓库预览 | 对公开仓库生成只读翻译预览，不创建 PR |
| 安全与限额 | 授权校验、路径安全、单任务最多 10 文件 / 200KB |

## 技术栈

- Python 3.12+
- [FastAPI](https://fastapi.tiangolo.com/) + Uvicorn
- GitHub App REST API（JWT + installation token）
- OpenAI Chat Completions（第一版翻译 Provider）
- pytest + respx（测试）

## API 概览

| 方法 | 路径 | 说明 |
| --- | --- | --- |
| `POST` | `/api/github/installations/verify` | 校验 GitHub App installation |
| `GET` | `/api/github/installations/{id}/repositories` | 列出 installation 已授权仓库 |
| `POST` | `/api/repositories/resolve` | 解析并校验仓库授权 |
| `GET` | `/api/repositories/{owner}/{repo}/markdown-files` | 发现可翻译 Markdown 文件 |
| `GET` | `/api/languages` | 返回支持的目标语言列表 |
| `POST` | `/api/translation-tasks` | 创建并执行翻译任务（同步） |
| `POST` | `/api/public-preview` | 公开仓库只读翻译预览 |

本地启动后可在 `/docs` 查看 OpenAPI 文档。

## 快速开始

### 1. 安装依赖

```bash
python -m venv .venv
source .venv/bin/activate
pip install -e ".[dev]"
```

### 2. 配置环境变量

复制 `.env.example` 为 `.env`，至少填写 GitHub App 相关变量：

```bash
cp .env.example .env
```

| 变量 | 说明 |
| --- | --- |
| `GITHUB_APP_ID` | GitHub App ID |
| `GITHUB_PRIVATE_KEY` | GitHub App 私钥（PEM，可用 `\n` 转义单行） |
| `GITHUB_WEBHOOK_SECRET` | Webhook 密钥（如暂未接 webhook 可留空） |
| `OPENAI_API_KEY` | OpenAI API Key（启用真实翻译时需要） |

Symphony / Linear 相关变量见 `.env.example` 注释，仅 Agent 工作流需要。

### 3. 启动服务

```bash
uvicorn app.main:app --reload --port 8000
```

### 4. 运行测试

```bash
pytest tests/ -v
```

## 项目结构

```text
app/
  api/           # FastAPI 路由（installations、repositories、tasks、languages、public_preview）
  core/          # 配置与错误类型
  domain/        # 领域模型（repository、languages、markdown_files、task）
  services/      # GitHub App、翻译、Markdown 保真、任务执行
docs/
  prd/           # 产品需求（GitHub Markdown Translator）
  plans/         # 实现计划
openspec/        # SDD 规范层与变更提案
tests/           # 单元与 API 测试
```

## 文档入口

- 产品总览：[docs/prd/github-translator/00-product-overview.md](docs/prd/github-translator/00-product-overview.md)
- PRD 索引：[docs/prd/github-translator/README.md](docs/prd/github-translator/README.md)
- 实现计划：[docs/plans/github-translator/README.md](docs/plans/github-translator/README.md)
- 本地开发与运维：[docs/operations/local-development.md](docs/operations/local-development.md)

## 仓库治理与 Agent 协作

本仓库同时承载 Symphony / Linear Agent 协作规范，用于 ticket 驱动的 SDD、TDD 与 OpenSpec 流程：

| 入口 | 用途 |
| --- | --- |
| [CLAUDE.md](CLAUDE.md) | Claude Agent 全局协作规范 |
| [CLAUDE.local.md](CLAUDE.local.md) | 本项目路径、命令与局部约定 |
| [WORKFLOW.md](WORKFLOW.md) | Linear ticket 调度与 Workpad 契约 |
| [openspec/](openspec/) | 长期规格与变更提案 |
| [.claude/agents/](.claude/agents/) | Explorer / PM / Builder / Tester / Reporter |
| [.claude/skills/](.claude/skills/) | OpenSpec、验证、Git 收口等技能 |

仓库结构校验：

```bash
scripts/validate-repository.sh
```

规范骨架来源：[StephenQiu30/stephen-cladue](https://github.com/StephenQiu30/stephen-cladue)。同步模板更新时只导入共享治理规则，避免覆盖项目特有文档。
