## Architecture

### Layer Boundary

```
┌─────────────────────────────────────────────────┐
│                  API Layer                       │
│  app/api/tasks.py, app/api/installations.py     │
│  - HTTP 请求解析/响应序列化                        │
│  - 错误映射 (domain error → HTTP status)          │
└──────────────────────┬──────────────────────────┘
                       │
                       ▼
┌─────────────────────────────────────────────────┐
│            Application Service Layer             │
│  app/application/installation_service.py        │
│  app/application/translation_task_service.py    │
│  - 业务编排和协调                                  │
│  - DTO 定义和转换                                  │
│  - 领域错误定义                                    │
└──────────────────────┬──────────────────────────┘
                       │
                       ▼
┌─────────────────────────────────────────────────┐
│                  Domain Layer                    │
│  app/domain/task.py, app/domain/languages.py    │
│  - 领域模型和值对象                                │
│  - 业务规则校验                                    │
└──────────────────────┬──────────────────────────┘
                       │
                       ▼
┌─────────────────────────────────────────────────┐
│            Infrastructure Layer                  │
│  app/services/github_app.py                     │
│  app/services/task_runner.py                    │
│  app/services/translation_provider.py           │
│  - 外部系统集成                                    │
└─────────────────────────────────────────────────┘
```

### Dependency Direction

- API → Application Service → Domain + Infrastructure
- Application Service 不依赖 HTTP 层
- Domain 不依赖 Infrastructure

## Key Decisions

### 1. Service 层职责边界

**Decision**: Application Service 负责业务编排，Domain 负责业务规则。

**Rationale**:
- InstallationService: 调用 GitHubAppClient，处理错误映射，返回 DTO
- TranslationTaskService: 校验语言，构造 Task，委托 TaskRunner

### 2. DTO 位置

**Decision**: DTO 定义在 `app/application/` 模块中。

**Rationale**:
- DTO 是 Application Service 的公共接口
- 避免 domain 依赖 HTTP 层的 Pydantic 模型
- 便于 Service 测试独立于 HTTP

### 3. 错误处理策略

**Decision**: Application Service 定义领域错误，Controller 负责 HTTP 映射。

**Rationale**:
- Service 层抛出语义化错误（如 `InstallationNotFoundError`）
- Controller 捕获并映射为 HTTP 状态码
- 保持 Service 层不依赖 HTTP 概念

### 4. 依赖注入方式

**Decision**: 使用 FastAPI 的 `Depends` 进行依赖注入。

**Rationale**:
- 项目已使用 FastAPI
- 无需引入额外 DI 框架
- 符合 ticket 的非目标约束

## File Structure

```
app/
├── application/
│   ├── __init__.py
│   ├── installation_service.py      # InstallationService
│   └── translation_task_service.py  # TranslationTaskService
├── api/
│   ├── installations.py             # 重构：thin controller
│   └── tasks.py                     # 重构：thin controller
└── ...

tests/
├── application/
│   ├── __init__.py
│   ├── test_installation_service.py
│   └── test_translation_task_service.py
└── ...
```
