## Why

PRD 11.6 要求将业务编排逻辑从 HTTP 控制器中分离出来，形成可测试的 Application Services 层。当前 `app/api/tasks.py` 和 `app/api/installations.py` 直接包含业务逻辑（如语言校验、Task 构造、GitHub 客户端初始化），不符合 Spring Boot 风格的 thin controller 原则。

## What Changes

- 新增 `app/application/__init__.py`：Application Service 层入口
- 新增 `app/application/installation_service.py`：InstallationService，封装 GitHub 安装验证逻辑
- 新增 `app/application/translation_task_service.py`：TranslationTaskService，封装翻译任务创建和执行逻辑
- 重构 `app/api/tasks.py`：移除业务逻辑，仅保留 HTTP 请求/响应映射
- 重构 `app/api/installations.py`：移除业务逻辑，仅保留 HTTP 请求/响应映射
- 新增 `tests/application/__init__.py`
- 新增 `tests/application/test_installation_service.py`
- 新增 `tests/application/test_translation_task_service.py`

## Capabilities

### New Capabilities
- `installation-service`: GitHub 安装验证和账户元数据处理
- `translation-task-service`: 翻译任务创建、语言校验和执行委托

### Modified Capabilities
- `translation-task-api`: 移除业务编排，委托给 TranslationTaskService
- `installation-api`: 移除业务编排，委托给 InstallationService

## Impact

- 新增 `app/application/` 目录，包含 Application Service 层
- 重构 API 控制器为 thin HTTP 适配器
- Service 测试可独立运行，不依赖 HTTP TestClient
- 不改变外部 API 行为或响应格式
