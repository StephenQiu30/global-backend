## Request 模块 (`app/requests/`)

### Requirement 1: Request 包结构

系统 SHALL 提供 `app/requests/` 包，包含：
- `__init__.py`
- `installation_requests.py`
- `repository_requests.py`
- `translation_task_requests.py`

### Requirement 2: 安装相关 Request

`app/requests/installation_requests.py` SHALL 定义：
- `VerifyInstallationRequest`：字段 `installation_id: int`
- `ListInstallationRepositoriesRequest`：字段 `installation_id: int`
- 名称以 `Request` 结尾，字段含 `Field(description=...)`

### Requirement 3: 仓库相关 Request

`app/requests/repository_requests.py` SHALL 定义：
- `ResolveRepositoryRequest`：字段 `input: str`, `installation_id: int`
- `GetMarkdownFilesRequest`：字段 `language: str`, `installation_id: str | None`
- 名称以 `Request` 结尾

### Requirement 4: 翻译任务相关 Request

`app/requests/translation_task_requests.py` SHALL 定义：
- `CreateTranslationTaskRequest`
- `CreatePublicPreviewRequest`
- `GetTranslationTaskStatusRequest`：字段 `task_id: str`
- `GetTranslationTaskFilePreviewsRequest`：字段 `task_id: str`
- 名称以 `Request` 结尾

## 控制器集成（变更）

### Requirement 7: 控制器导入规范

控制器 SHALL 从 `app/requests/` 导入所有请求模型，从 `app/vo/` 导入所有响应模型。
GET 端点 SHALL 通过 `Depends()` 或 `Annotated[..., Query()]` 注入 Request 模型。

## 测试要求（变更）

### Requirement 11: Request 测试

`tests/requests/` SHALL 验证 POST/GET Request 字段校验。
