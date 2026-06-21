## Context

global-backend 是全新项目，目前无任何源代码、依赖文件或项目结构。PRD 02 要求后端实现仓库地址解析和授权校验能力，这是翻译流程的入口门禁。

PRD 01 定义了 GitHub App 安装与授权的基础能力，本设计假设 PRD 01 的基础设施（config、github_app service）已存在或在本 change 中一并实现最小可用版本。

## Goals / Non-Goals

**Goals:**
- 解析用户输入的 GitHub 仓库地址为 `owner/repo` 格式
- 校验仓库是否在 GitHub App installation 的授权列表中
- 提供 `POST /api/repositories/resolve` API 端点
- 遵循 TDD 流程，测试先行

**Non-Goals:**
- SSH URL 支持
- GitHub 子路径 URL（如 `/owner/repo/tree/branch/path`）
- Gist URL 支持
- GitLab/Gitee 等非 GitHub 平台
- 公开仓库 fallback（未安装则拒绝）
- 猜测默认 installation

## Decisions

### 1. 使用 Pydantic 模型作为 RepositoryRef

**决策**: 使用 Pydantic `BaseModel` 定义 `RepositoryRef(owner, repo, full_name)`。

**理由**: 项目技术栈已确定为 FastAPI + Pydantic，使用 Pydantic 模型可直接用于 API 响应序列化，且提供类型验证。

### 2. 解析函数为纯逻辑

**决策**: `parse_repository_input(value: str) -> RepositoryRef` 是纯函数，无外部依赖。

**理由**: 纯逻辑易于测试，可复用于前端（TypeScript 重写），不依赖任何服务。

### 3. 授权校验通过 installation repository list

**决策**: 授权校验通过 GitHub API 查询 installation 的仓库列表，检查目标仓库是否在列表中。

**理由**: 符合 PRD 01 定义的权限模型，不引入额外的权限存储或缓存层。第一版保持简单。

### 4. 错误码使用结构化格式

**决策**: API 错误返回 `{ "error": "repository_not_installed" }` 格式。

**理由**: 前端可根据错误码展示不同提示，便于国际化和错误处理。

### 5. 项目结构分层

**决策**: 采用 `app/domain/`（纯逻辑）、`app/api/`（路由）、`app/services/`（外部服务）、`app/core/`（配置）分层。

**理由**: 职责分离，domain 层可独立测试，api 层处理 HTTP 协议，services 层封装外部依赖。

## Risks / Trade-offs

- **GitHub API 速率限制**: 每次 resolve 都调用 GitHub API 查询仓库列表 → 后续可添加缓存层
- **installation 仓库列表可能很大**: GitHub API 分页 → 当前实现只查询第一页，后续需处理分页
- **无本地授权存储**: 依赖 GitHub API 可用性 → 第一版可接受，后续可添加本地缓存

## Migration Plan

1. 创建 `pyproject.toml` 和项目基础结构
2. 实现 `app/core/config.py`（GitHub App 配置）
3. 实现 `app/domain/repository.py`（纯逻辑）
4. 实现 `app/services/github_app.py`（GitHub API 调用）
5. 实现 `app/api/repositories.py`（API 路由）
6. 实现 `app/main.py`（应用工厂）
7. 验证：`pytest tests/domain/test_repository.py tests/api/test_repository_resolve.py -v`

## Open Questions

- 无（所有设计决策已确定）
