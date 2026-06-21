## Context

STE-348 是 PRD 11 持久化工程计划的集成任务（Task 9）。前置 Tasks 2-8（config、ORM models、DTO/VO、repositories、services、controllers、queue）在代码库中不存在。本设计需要构建最小可行的持久化基础设施以满足 Task 9 验收标准。

当前代码库状态：
- `POST /api/translation-tasks` 同步执行，返回 TaskResult（内存中）
- 无数据库、无 ORM、无 repository、无 DTO/VO 分离
- 无 GET 端点查询任务状态或文件预览

## Goals / Non-Goals

**Goals:**
- 实现 SQLAlchemy async session 基础设施（app/db/）
- 实现三个 ORM Model（InstallationAccount, TranslationTask, TranslationFile）
- 实现两个 Repository（InstallationAccountRepository, TranslationTaskRepository）
- 实现 DTO/VO 分离
- 实现 Application Service 层
- 更新 controller 层接入持久化
- 新增 GET 端点
- 通过 TDD 验证所有行为

**Non-Goals:**
- 不实现完整 RQ/Redis 队列（使用 stub adapter）
- 不实现 Alembic 迁移（仅 ORM 模型定义）
- 不实现 `app/controller/` 目录迁移（继续使用 `app/api/`）
- 不实现 Worker 执行逻辑
- 不修改 `app/services/task_runner.py`（保留现有同步执行能力）

## Decisions

### 1. 继续使用 app/api/ 而非迁移至 app/controller/

**决策**: 在现有 `app/api/tasks.py` 中新增端点，不创建 `app/controller/` 目录。

**理由**: STE-348 的范围是集成持久化，不是架构迁移。迁移到 controller 目录是 Task 7 的范围，不应在本 ticket 中完成。

### 2. 使用 SQLite aiosqlite 用于测试

**决策**: 测试使用 `aiosqlite` 内存数据库，不需要外部 PostgreSQL。

**理由**: 降低测试环境依赖，确保 CI 可以无外部服务运行。ORM Model 使用 JSON（非 JSONB）以兼容 SQLite。

### 3. Stub Queue Adapter

**决策**: 实现内存队列 stub，`enqueue()` 直接记录 task_id。

**理由**: 完整 RQ 集成是 Task 8 的范围。本 ticket 只需要证明 task_id 能被传递到队列层。

### 4. POST 响应格式变更

**决策**: `POST /api/translation-tasks` 从返回 `TaskResult` 改为返回 `{ task_id, status }`。

**理由**: 异步模式下任务尚未执行完成，不能返回结果。调用方需要通过 task_id 轮询状态。

### 5. UUID 作为 task_id

**决策**: 使用 `uuid4().hex` 生成 32 字符 task_id。

**理由**: 与 ORM Model 的主键生成策略一致，避免依赖数据库自增 ID。

### 6. JSON columns 而非 JSONB

**决策**: `source_files` 和 `file_mappings` 使用 JSON 类型。

**理由**: SQLite 不支持 JSONB，使用 JSON 确保测试兼容性。

## Risks / Trade-offs

- **POST 行为变更**: 现有 `tests/api/test_translation_tasks.py` 需要适配新的响应格式
- **无 Alembic 迁移**: ORM Model 定义了表结构但未生成迁移脚本（STE-342 覆盖）
- **Stub queue**: 入队操作不执行实际翻译，仅记录 task_id
- **依赖方向**: Application Service 直接使用 Repository（符合 OpenSpec 契约）
