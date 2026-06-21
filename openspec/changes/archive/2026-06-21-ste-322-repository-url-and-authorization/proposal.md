## Why

PRD 02 规定首版只支持 GitHub App 已授权仓库。后端需要解析用户输入的 GitHub 仓库地址，并在进入翻译流程前强制校验仓库是否已通过 GitHub App 授权。这是翻译流程的入口门禁，防止未授权仓库进入扫描和翻译环节。

## What Changes

- 新增 `app/domain/repository.py`：实现 `RepositoryRef` 模型和 `parse_repository_input()` 纯逻辑函数
- 新增 `app/api/repositories.py`：实现 `POST /api/repositories/resolve` 授权校验接口
- 新增 `app/services/github_app.py`：GitHub App 服务层，提供 installation 授权校验能力
- 新增 `app/core/config.py`：应用配置，包含 GitHub App 凭据
- 新增 `app/main.py`：FastAPI 应用工厂
- 新增 `pyproject.toml`：项目依赖和配置

## Capabilities

### New Capabilities
- `repository-parsing`: 仓库地址解析能力，支持 `https://github.com/owner/repo`、`github.com/owner/repo`、`owner/repo` 三种格式
- `repository-authorization`: 仓库授权校验能力，检查仓库是否在 GitHub App installation 的授权列表中

### Modified Capabilities
- 无（全新实现）

## Impact

- 新增 API 端点：`POST /api/repositories/resolve`
- 依赖 GitHub App installation API 进行授权校验
- 需要 GitHub App 配置（`GITHUB_APP_ID`、`GITHUB_PRIVATE_KEY`、`GITHUB_APP_SLUG`）
- 影响前端仓库选择流程（后续 PRD 02 Task 3/4）
