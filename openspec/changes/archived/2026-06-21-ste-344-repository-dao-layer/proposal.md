## Why

PRD 11.5 要求集中数据库访问，防止原始 SQLAlchemy session 泄漏到控制器或应用服务中。当前实现没有持久化层，任务执行结果和安装账户元数据无法持久化存储。需要添加 Repository/DAO 层来隔离数据库访问，使持久化逻辑可测试且与 HTTP 路由解耦。

## What Changes

- 新增 `app/repositories/installation_account_repository.py`：InstallationAccountRepository，用于 upsert 验证过的安装账户元数据
- 新增 `app/repositories/translation_task_repository.py`：TranslationTaskRepository，用于创建任务、更新状态、读取任务结果和文件预览
- 新增 `tests/repositories/test_translation_task_repository.py`：TranslationTaskRepository 的自动化测试

## Capabilities

### New Capabilities
- `installation-account-repository`: 安装账户元数据的 upsert 和查询
- `translation-task-repository`: 翻译任务的创建、状态更新、结果读取、文件预览元数据读取
- `failed-task-persistence`: 失败任务的安全错误信息持久化（仅存储 error_code 和 error_message）

### Modified Capabilities
- 无（全新实现）

## Impact

- 新增 Repository 层，隔离数据库访问
- 不涉及 API 路由变更
- 不涉及 Worker 执行逻辑
- 不涉及通用基础 Repository 抽象
- Repository 返回 domain/VO 友好数据，不返回原始 ORM Model
