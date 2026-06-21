## Why

PRD 11.3 要求为翻译任务、安装账户和翻译文件提供持久化存储。当前所有数据模型均为 Pydantic 内存模型，无法跨进程或重启保留状态。需要 SQLAlchemy ORM Models 和 Alembic 迁移来创建 PgSQL 表结构。

## What Changes

- 新增 `app/db/base.py`：SQLAlchemy DeclarativeBase 和共享列定义
- 新增 `app/db/session.py`：async session 工厂和引擎配置
- 新增 `app/models/installation_account_model.py`：InstallationAccountModel
- 新增 `app/models/translation_task_model.py`：TranslationTaskModel
- 新增 `app/models/translation_file_model.py`：TranslationFileModel
- 新增 `alembic.ini` + `alembic/env.py`：Alembic 配置
- 新增 `alembic/versions/*_add_translation_persistence.py`：初始迁移
- 新增 `tests/db/test_models.py`：模型映射和约束测试
- 更新 `pyproject.toml`：添加 sqlalchemy、alembic、asyncpg 依赖

## Capabilities

### New Capabilities
- `db-base`: SQLAlchemy 2.x DeclarativeBase 和 session 工厂
- `installation-account-model`: 安装账户持久化模型
- `translation-task-model`: 翻译任务持久化模型（含状态、结果字段）
- `translation-file-model`: 翻译文件持久化模型（源/目标路径映射）
- `alembic-migration`: Alembic 配置和初始迁移脚本

### Modified Capabilities
- 无（全新实现）

## Impact

- 新增数据库表：`installation_accounts`、`translation_tasks`、`translation_files`
- 依赖 SQLAlchemy 2.x、Alembic、asyncpg
- 仅持久化层，不涉及 Repository 方法、API 端点或 RQ workers
- ORM Models 仅导入 SQLAlchemy，不导入 domain DTO/VO/controller 模块
