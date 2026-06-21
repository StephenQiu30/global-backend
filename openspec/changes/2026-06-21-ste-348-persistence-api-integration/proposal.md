## Why

STE-348 是持久化工程计划（PRD 11）中的集成任务（Task 9）。当前 `POST /api/translation-tasks` 仅同步执行并返回内存结果，无任务持久化、状态轮询或文件预览能力。Ticket 要求将 controller 层接入 application service、repository 和 queue adapter，实现任务提交返回 ID、状态查询和文件预览端点。

前置任务（Tasks 2-8：config、ORM models、DTO/VO、repositories、application services、controllers、queue）在当前代码库中不存在。本 change 需要实现最小可行的持久化基础设施以满足 Task 9 的验收标准。

## What Changes

- 新增 `app/db/` 模块：SQLAlchemy async engine、AsyncSession factory、DeclarativeBase
- 新增 `app/models/`：InstallationAccountModel、TranslationTaskModel、TranslationFileModel
- 新增 `app/repositories/`：InstallationAccountRepository、TranslationTaskRepository
- 新增 `app/dto/`：TranslationTaskCreateDTO
- 新增 `app/vo/`：TranslationTaskStatusVO、TranslationTaskCreateVO、FilePreviewVO
- 新增 `app/services/translation_task_service.py`：任务创建、状态查询、文件预览编排
- 新增 `app/services/installation_service.py`：安装验证持久化
- 更新 `app/api/tasks.py`：新增 GET 端点，POST 改为异步队列提交
- 更新 `app/api/installations.py`：接入安装验证持久化
- 更新 `app/main.py`：注入数据库 session 和 service 依赖
- 新增 `tests/db/test_models.py`、`tests/repositories/`、`tests/api/test_persistence_api.py`

## Capabilities

### New Capabilities

- `task-persistence`: 翻译任务持久化到 PostgreSQL
- `task-status-polling`: GET 端点查询持久化任务状态
- `file-preview-api`: GET 端点查询翻译文件预览元数据
- `installation-persistence`: 安装验证元数据持久化
- `db-session-infra`: SQLAlchemy async session 基础设施

### Modified Capabilities

- `translation-task-api`: POST 端点从同步执行改为返回任务 ID + queued 状态

## Impact

- `POST /api/translation-tasks` 响应格式变更：从 `TaskResult` 改为 `{ task_id, status }`
- 新增 `GET /api/translation-tasks/{task_id}` 和 `GET /api/translation-tasks/{task_id}/file-previews` 端点
- `POST /api/github/installations/verify` 响应不变，但内部增加持久化逻辑
- 需要 `DATABASE_URL` 环境变量（SQLite 用于测试，PostgreSQL 用于生产）
- 现有 `tests/api/test_translation_tasks.py` 需要适配新的 POST 响应格式
