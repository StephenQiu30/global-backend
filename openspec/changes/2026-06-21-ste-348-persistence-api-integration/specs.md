## Database Infrastructure

### Requirement 1: SQLAlchemy Async Session

系统 SHALL 提供异步数据库会话管理：

- `app/db/base.py` 定义 `Base` (DeclarativeBase) 作为所有 ORM Model 的基类
- `app/db/session.py` 提供 `get_async_session()` 异步生成器用于 FastAPI 依赖注入
- `app/db/engine.py` 使用 `create_async_engine` 创建异步引擎
- 测试 SHALL 使用 `aiosqlite` 内存数据库，生产使用 `asyncpg`

### Requirement 2: Database URL Configuration

- `DATABASE_URL` 环境变量配置数据库连接
- 默认值：`sqlite+aiosqlite:///./test.db`（开发友好）
- 测试中使用 `sqlite+aiosqlite://`（内存数据库）

## ORM Models

### Requirement 3: InstallationAccountModel

```
表名: installation_accounts
字段:
  - id: String(32), PK, default=hex(uuid4())
  - installation_id: Integer, unique, not null
  - account_login: String(255), not null
  - account_type: String(50), not null
  - created_at: DateTime, server_default=func.now()
  - updated_at: DateTime, server_default=func.now(), onupdate=func.now()
```

### Requirement 4: TranslationTaskModel

```
表名: translation_tasks
字段:
  - id: String(32), PK, default=hex(uuid4())
  - task_id: String(36), unique, not null (UUID string)
  - installation_id: String(50), not null
  - repository: String(255), not null
  - base_branch: String(255), not null
  - source_files: JSON, not null (list of file paths)
  - language: String(10), not null
  - status: String(20), not null, default="queued"
  - pr_url: String(500), nullable
  - pr_number: Integer, nullable
  - file_mappings: JSON, nullable (list of {source_path, target_path})
  - error_code: String(50), nullable
  - error_message: String(500), nullable
  - created_at: DateTime, server_default=func.now()
  - updated_at: DateTime, server_default=func.now(), onupdate=func.now()
索引:
  - ix_translation_tasks_task_id (task_id)
  - ix_translation_tasks_installation_id (installation_id)
  - ix_translation_tasks_created_at (created_at)
```

### Requirement 5: TranslationFileModel

```
表名: translation_files
字段:
  - id: String(32), PK, default=hex(uuid4())
  - task_id: String(36), not null (逻辑引用 translation_tasks.task_id)
  - source_path: String(500), not null
  - target_path: String(500), not null
  - status: String(20), not null, default="pending"
  - created_at: DateTime, server_default=func.now()
索引:
  - ix_translation_files_task_id (task_id)
```

## Repositories

### Requirement 6: TranslationTaskRepository

- `create_task(data) -> TranslationTaskModel`: 创建 QUEUED 状态任务
- `get_by_task_id(task_id) -> TranslationTaskModel | None`: 按 task_id 查询
- `update_status(task_id, status, result_data) -> None`: 更新状态和结果
- `get_file_previews(task_id) -> list[TranslationFileModel]`: 查询翻译文件预览

### Requirement 7: InstallationAccountRepository

- `upsert(installation_id, account_login, account_type) -> InstallationAccountModel`: 插入或更新

## DTO / VO

### Requirement 8: TranslationTaskCreateDTO

```python
class TranslationTaskCreateDTO(BaseModel):
    installation_id: str  # min_length=1
    repository: str       # min_length=1
    base_branch: str      # min_length=1
    files: list[str]      # min_length=1
    language: str         # min_length=1
```

### Requirement 9: TranslationTaskCreateVO

```python
class TranslationTaskCreateVO(BaseModel):
    task_id: str
    status: str  # "queued"
```

### Requirement 10: TranslationTaskStatusVO

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

### Requirement 11: FilePreviewVO

```python
class FilePreviewVO(BaseModel):
    source_path: str
    target_path: str
    status: str
```

### Requirement 12: TaskNotFoundVO

```python
class TaskNotFoundVO(BaseModel):
    error: str = "task_not_found"
    message: str
```

## API Endpoints

### Requirement 13: POST /api/translation-tasks (修改)

- 请求体：TranslationTaskCreateDTO
- 成功响应 201：TranslationTaskCreateVO（包含 task_id 和 status="queued"）
- 验证失败：422
- 语言不支持：400
- 行为变更：创建持久化任务记录，入队到 RQ，返回 task_id

### Requirement 14: GET /api/translation-tasks/{task_id} (新增)

- 成功响应 200：TranslationTaskStatusVO
- 未找到：404 + TaskNotFoundVO

### Requirement 15: GET /api/translation-tasks/{task_id}/file-previews (新增)

- 成功响应 200：`list[FilePreviewVO]`
- 未找到：404 + TaskNotFoundVO

### Requirement 16: POST /api/github/installations/verify (修改)

- 请求/响应格式不变
- 内部行为变更：验证成功后调用 InstallationAccountRepository.upsert()

## Application Services

### Requirement 17: TranslationTaskService

- `create_task(dto) -> TranslationTaskCreateVO`: 校验语言、创建持久化记录、入队
- `get_task_status(task_id) -> TranslationTaskStatusVO`: 查询持久化任务状态
- `get_file_previews(task_id) -> list[FilePreviewVO]`: 查询翻译文件预览

### Requirement 18: InstallationService

- `verify_and_persist(installation_id) -> InstallationResponse`: 验证并持久化安装信息

## Queue Adapter

### Requirement 19: Stub Queue Adapter

- `TranslationTaskQueue.enqueue(task_id) -> str`: 将 task_id 入队
- 测试使用内存实现，生产使用 RQ
- 不要求本 ticket 实现完整 RQ Worker
