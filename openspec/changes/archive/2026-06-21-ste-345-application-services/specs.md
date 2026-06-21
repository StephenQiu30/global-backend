## InstallationService (`app/application/installation_service.py`)

### Requirement 1: InstallationService 接口

系统 SHALL 提供 `InstallationService` 类，包含以下方法：
- `verify_installation(installation_id: int) -> InstallationResponse`
- `list_repositories(installation_id: int) -> RepositoryListResponse`

### Requirement 2: verify_installation 行为

`verify_installation` SHALL：
1. 调用 `GitHubAppClient.get_installation()` 获取安装信息
2. 构造并返回 `InstallationResponse` DTO
3. 将 `ValueError` 映射为 `InstallationNotFoundError`
4. 将 `RuntimeError` 映射为 `GitHubApiError`

### Requirement 3: list_repositories 行为

`list_repositories` SHALL：
1. 调用 `GitHubAppClient.get_installation_repos()` 获取仓库列表
2. 构造并返回 `RepositoryListResponse` DTO
3. 将 `ValueError` 映射为 `InstallationNotFoundError`
4. 将 `RuntimeError` 映射为 `GitHubApiError`

### Requirement 4: 错误类型定义

系统 SHALL 定义以下 Application Service 层错误：
- `InstallationNotFoundError`：安装不存在
- `GitHubApiError`：GitHub API 调用失败

## TranslationTaskService (`app/application/translation_task_service.py`)

### Requirement 5: TranslationTaskService 接口

系统 SHALL 提供 `TranslationTaskService` 类，包含以下方法：
- `create_task(request: TranslationTaskRequest) -> TaskResult`

### Requirement 6: create_task 行为

`create_task` SHALL：
1. 校验 `language` 是否为支持的语言代码
2. 构造 `Task` domain 对象
3. 委托 `TaskRunner.run()` 执行任务
4. 返回 `TaskResult`
5. 语言校验失败时抛出 `UnsupportedLanguageError`

### Requirement 7: 语言校验

TranslationTaskService SHALL 使用 `domain.languages.validate_language_code()` 进行语言校验。

### Requirement 8: DTO 定义

系统 SHALL 定义以下 DTO：
- `TranslationTaskRequest`：包含 `installation_id`, `repository`, `base_branch`, `files`, `language`
- `InstallationResponse`：包含 `installation_id`, `account_login`, `account_type`, `repository_selection`
- `RepositoryItem`：包含 `full_name`, `default_branch`, `private`
- `RepositoryListResponse`：包含 `repositories: list[RepositoryItem]`

## Controller 层约束

### Requirement 9: Controller 薄化

重构后的 Controller SHALL：
1. 仅负责 HTTP 请求解析和响应序列化
2. 不包含业务校验逻辑（如语言校验）
3. 不直接调用 domain 或 infrastructure 层
4. 通过 Application Service 执行业务操作

### Requirement 10: 错误映射

Controller SHALL：
1. 捕获 Application Service 层的领域错误
2. 映射为对应的 HTTP 状态码
3. 不泄露内部错误细节

## 测试约束

### Requirement 11: Service 测试独立性

Application Service 测试 SHALL：
1. 不依赖 FastAPI TestClient
2. 不依赖 HTTP 请求/响应对象
3. 仅测试 Service 层的业务编排逻辑
4. 使用 mock 或 fake 替代外部依赖（GitHub API、TranslationProvider）
