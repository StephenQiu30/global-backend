## Goals

- 隔离数据库访问，防止 SQLAlchemy session 泄漏到控制器或应用服务
- 提供可测试的持久化层，支持单元测试和集成测试
- 返回 domain/VO 友好数据，不暴露 ORM 实现细节

## Non-Goals

- 不实现动态查询 DSL
- 不实现分页框架
- 不实现跨实体的通用 Repository 抽象（直到证明有重复代码）
- 不修改 API 路由或 Worker 执行逻辑

## Contracts

### InstallationAccountRepository

```python
class InstallationAccountRepository:
    def __init__(self, session: AsyncSession): ...

    async def upsert(
        self,
        installation_id: int,
        account_login: str,
        account_type: str,
        repository_selection: str,
    ) -> InstallationAccountData: ...
```

### TranslationTaskRepository

```python
class TranslationTaskRepository:
    def __init__(self, session: AsyncSession): ...

    async def create(
        self,
        installation_id: str,
        repository: str,
        base_branch: str,
        files: list[str],
        language: str,
    ) -> TranslationTaskData: ...

    async def update_status(
        self,
        task_id: str,
        status: TaskStatus,
        *,
        pr_url: str | None = None,
        pr_number: int | None = None,
        mappings: list[FileMapping] | None = None,
        error_code: str | None = None,
        error_message: str | None = None,
    ) -> TranslationTaskData | None: ...

    async def get_by_id(self, task_id: str) -> TranslationTaskData | None: ...

    async def get_file_previews(self, task_id: str) -> list[FileMapping]: ...
```

## State Flow

```
TranslationTask:
  queued → running → succeeded
                   → failed
```

## Failure Paths

- 数据库连接失败：抛出异常，由调用方处理
- 任务不存在：返回 None
- 更新冲突：乐观锁或最后写入胜出（当前实现使用简单更新）

## Permission Boundary

- Repository 层不处理权限，由上层服务负责
- Repository 只接受已验证的数据

## Verification

- 自动化测试：`pytest tests/repositories/test_translation_task_repository.py -v`
- 手动检查：事务/session 使用是否清晰

## Migration/Rollback

- 新增表：`installation_accounts`、`translation_tasks`、`translated_files`
- 无数据迁移（全新实现）
- 回滚：删除表和 Repository 文件
