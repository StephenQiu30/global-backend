## DTO 模块 (`app/dto/`)

### Requirement 1: DTO 包结构

系统 SHALL 提供 `app/dto/` 包，包含：
- `__init__.py`：包初始化
- `installation.py`：安装相关请求 Request
- `repository.py`：仓库解析与 Markdown 发现请求 Request
- `translation_task.py`：翻译任务和公共预览请求 Request

入参类名以 `Request` 结尾，表示 API 请求参数 DTO。

### Requirement 2: 安装验证 Request

`app/dto/installation.py` SHALL 定义：
- `VerifyInstallationRequest(BaseModel)`：字段 `installation_id: int`
- `ListInstallationRepositoriesRequest(BaseModel)`：字段 `installation_id: int`
- 名称以 `Request` 结尾，字段含 `Field(description=...)`

### Requirement 3: 仓库相关 Request

`app/dto/repository.py` SHALL 定义：
- `ResolveRepositoryRequest(BaseModel)`：字段 `input: str`, `installation_id: int`
- `GetMarkdownFilesRequest(BaseModel)`：字段 `language: str`, `installation_id: str | None`
- 名称以 `Request` 结尾

### Requirement 4: 翻译任务 Request

`app/dto/translation_task.py` SHALL 定义：
- `CreateTranslationTaskRequest(BaseModel)`
- `CreatePublicPreviewRequest(BaseModel)`
- `GetTranslationTaskStatusRequest(BaseModel)`：字段 `task_id: str`
- `GetTranslationTaskFilePreviewsRequest(BaseModel)`：字段 `task_id: str`
- 名称以 `Request` 结尾

## VO 模块 (`app/vo/`)

### Requirement 5: VO 包结构

系统 SHALL 提供 `app/vo/` 包，出参类名以 `VO` 结尾。

### Requirement 6: 安装验证 VO

`app/vo/installation_vo.py` SHALL 定义 `InstallationVO`, `RepositoryItemVO`, `RepositoryListVO`。

### Requirement 7: 翻译任务 VO

`app/vo/translation_task_vo.py` SHALL 定义 `TranslationTaskCreateVO`, `TranslationTaskStatusVO`, `FilePreviewVO`, `PublicPreviewVO` 等响应 VO。

## 控制器集成

### Requirement 8: 控制器导入规范

控制器 SHALL 从 `app/dto/` 导入所有请求模型，从 `app/vo/` 导入所有响应模型。
GET 端点 SHALL 通过 `Depends()` 或 `Annotated[..., Query()]` 注入 Request 模型。

### Requirement 9: 安装控制器

`app/controller/installation_controller.py` SHALL 从 `app.dto.installation` 导入 Request 类。

### Requirement 10: 翻译任务控制器

`app/controller/translation_task_controller.py` SHALL 从 `app.dto.translation_task` 导入 Request 类。

### Requirement 11: 公共预览控制器

`app/controller/public_preview_controller.py` SHALL 从 `app.dto.translation_task` 导入 `CreatePublicPreviewRequest`。

## 测试要求

### Requirement 12: DTO 测试

`tests/dto/` SHALL 验证 Request 字段校验。

### Requirement 13: VO 测试

`tests/vo/` SHALL 验证 VO 序列化输出。
