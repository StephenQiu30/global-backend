## InstallationService (`app/services/installation_service.py`)

### Requirement 1: InstallationService 接口

系统 SHALL 提供 `InstallationService` 类，包含以下方法：
- `verify_and_persist(installation_id, account_login, account_type) -> dict`

### Requirement 2: verify_and_persist 行为

`verify_and_persist` SHALL：
1. 通过 `InstallationAccountRepository.upsert()` 持久化安装账户元数据
2. 返回包含 `installation_id`, `account_login`, `account_type` 的字典

## TranslationTaskService (`app/services/translation_task_service.py`)

### Requirement 3: TranslationTaskService 接口

系统 SHALL 提供 `TranslationTaskService` 类，包含以下方法：
- `create_task(...) -> TranslationTaskCreateVO`
- `get_task_status(task_id) -> TranslationTaskStatusVO | None`
- `get_file_previews(task_id) -> list[FilePreviewVO] | None`

### Requirement 4: create_task 行为

`create_task` SHALL：
1. 校验 `language` 是否为支持的语言代码
2. 通过 `TranslationTaskRepository` 创建任务记录
3. 通过 `TranslationTaskQueue` 入队异步执行
4. 返回 `TranslationTaskCreateVO`
5. 语言校验失败时抛出 `ValueError`

### Requirement 5: 语言校验

TranslationTaskService SHALL 使用 `domain.languages.validate_language_code()` 进行语言校验。

## Controller 层约束

### Requirement 6: Controller 薄化

Controller SHALL：
1. 仅负责 HTTP 请求解析和响应序列化
2. 从 `app/dto/` 导入 `XxxRequest`，从 `app/vo/` 导入 `XxxVO`
3. 通过 Service 层执行业务操作
4. 所有 HTTP 端点定义在 `app/controller/`，不得在 `app/api/` 重复定义

### Requirement 7: 错误映射

Controller SHALL：
1. 捕获 Service 层错误并映射为 HTTP 状态码
2. 不泄露内部错误细节

## 测试约束

### Requirement 8: Service 测试独立性

Service 测试 SHALL：
1. 不依赖 FastAPI TestClient（API 集成测试放在 `tests/api/`）
2. 使用 mock 或 fake 替代外部依赖
