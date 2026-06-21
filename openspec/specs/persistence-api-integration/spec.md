## Database Infrastructure

### Requirement 1: SQLAlchemy Async Session

系统 SHALL 提供异步数据库会话管理：

- `app/models/base.py` 定义 `Base` (DeclarativeBase) 作为所有 ORM Model 的基类
- `app/db/session.py` 提供 `get_async_session()` 异步生成器用于 FastAPI 依赖注入
- `app/db/engine.py` 使用 `create_async_engine` 创建异步引擎
- 测试 SHALL 使用 `aiosqlite` 内存数据库，生产使用 `asyncpg`

### Requirement 2: Database URL Configuration

- `DATABASE_URL` 环境变量配置数据库连接（必填，无代码内默认值）
- 测试中使用 `sqlite+aiosqlite://`（内存数据库）

## ORM Models

### Requirement 3: InstallationAccountModel

```
表名: installation_accounts
字段:
  - id: Integer, PK, autoincrement
  - installation_id: Integer, unique, not null
  - account_login: String(255), not null
  - account_type: String(32), not null
  - repository_selection: String(32), not null
  - created_at: DateTime, server_default=func.now()
  - updated_at: DateTime, server_default=func.now(), onupdate=func.now()
```

### Requirement 4: TranslationTaskModel

```
表名: translation_tasks
字段:
  - id: Integer, PK, autoincrement
  - task_id: String(36), unique, not null (UUID string)
  - installation_id: String(64), not null
  - repository: String(255), not null
  - base_branch: String(255), not null
  - files: Text, not null (JSON array of file paths)
  - language: String(16), not null
  - status: String(16), not null, default="queued"
  - pr_url: String(512), nullable
  - pr_number: Integer, nullable
  - mappings: Text, nullable (JSON array of {source_path, target_path})
  - error_code: String(64), nullable
  - error_message: String(512), nullable
  - created_at: DateTime, server_default=func.now()
  - updated_at: DateTime, server_default=func.now(), onupdate=func.now()
索引:
  - ix_translation_tasks_task_id (task_id)
```

## Repositories

### Requirement 5: TranslationTaskRepository

- `create(...) -> TranslationTaskData`: 创建 QUEUED 状态任务
- `get_by_id(task_id) -> TranslationTaskData | None`: 按 task_id 查询
- `update_status(task_id, status, ...) -> TranslationTaskData | None`: 更新状态和结果
- `get_file_previews(task_id) -> list[dict]`: 从 `translation_tasks.mappings` JSON 读取文件映射

### Requirement 6: InstallationAccountRepository

- `upsert(installation_id, account_login, account_type) -> InstallationAccountModel`: 插入或更新

## DTO / VO

### Requirement 7: TranslationTaskCreateRequest

```python
class TranslationTaskCreateRequest(BaseModel):
    installation_id: str  # min_length=1
    repository: str       # min_length=1
    base_branch: str      # min_length=1
    files: list[str]      # min_length=1
    language: str         # min_length=1
```

### Requirement 8: TranslationTaskCreateVO

```python
class TranslationTaskCreateVO(BaseModel):
    task_id: str
    status: str  # "queued"
```

### Requirement 9: TranslationTaskStatusVO

```python
class TranslationTaskStatusVO(BaseModel):
    task_id: str
    status: str
    repository: str
    language: str
    pr_url: str | None
    pr_number: int | None
    file_mappings: list[dict] | None
    error_code: str | None
    error_message: str | None
    created_at: str
    updated_at: str
```

### Requirement 10: FilePreviewVO

```python
class FilePreviewVO(BaseModel):
    source_path: str
    target_path: str
    status: str
```

### Requirement 11: TaskNotFoundVO

```python
class TaskNotFoundVO(BaseModel):
    error: str = "task_not_found"
    message: str
```

## API Endpoints

### Requirement 12: POST /api/translation-tasks (修改)

- 请求体：CreateTranslationTaskRequest
- 成功响应 201：TranslationTaskCreateVO（包含 task_id 和 status="queued"）
- 验证失败：422
- 语言不支持：400
- 行为变更：创建持久化任务记录，入队到 RQ，返回 task_id

### Requirement 13: GET /api/translation-tasks/{task_id} (新增)

- 成功响应 200：TranslationTaskStatusVO
- 未找到：404 + TaskNotFoundVO

### Requirement 14: GET /api/translation-tasks/{task_id}/file-previews (新增)

- 成功响应 200：`list[FilePreviewVO]`
- 未找到：404 + TaskNotFoundVO

### Requirement 15: POST /api/github/installations/verify (修改)

- 请求/响应格式不变
- 内部行为变更：验证成功后调用 InstallationAccountRepository.upsert()

## Services

### Requirement 16: TranslationTaskService

- `create_task(...) -> TranslationTaskCreateVO`: 校验语言、创建持久化记录、入队
- `get_task_status(task_id) -> TranslationTaskStatusVO | None`: 查询持久化任务状态
- `get_file_previews(task_id) -> list[FilePreviewVO] | None`: 查询翻译文件预览

### Requirement 17: InstallationService

- `verify_and_persist(installation_id) -> InstallationResponse`: 验证并持久化安装信息

## Queue Adapter

### Requirement 18: Stub Queue Adapter

- `TranslationTaskQueue.enqueue(task_id) -> str`: 将 task_id 入队
- 测试使用内存实现，生产使用 RQ
- 不要求本 ticket 实现完整 RQ Worker
