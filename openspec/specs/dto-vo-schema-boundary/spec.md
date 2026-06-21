## DTO 模块 (`app/dto/`)

### Requirement 1: DTO 包结构

系统 SHALL 提供 `app/dto/` 包，包含：
- `__init__.py`：包初始化
- `installation_dto.py`：安装相关请求 DTO
- `translation_task_dto.py`：翻译任务和公共预览请求 DTO

### Requirement 2: 安装验证 DTO

`app/dto/installation_dto.py` SHALL 定义：
- `VerifyInstallationDTO(BaseModel)`：字段 `installation_id: int`
- 名称以 `DTO` 结尾

### Requirement 3: 翻译任务 DTO

`app/dto/translation_task_dto.py` SHALL 定义：
- `CreateTranslationTaskDTO(BaseModel)`：
  - `installation_id: str`（min_length=1）
  - `repository: str`（min_length=1）
  - `base_branch: str`（min_length=1）
  - `files: List[str]`（min_length=1）
  - `language: str`（min_length=1）
- `CreatePublicPreviewDTO(BaseModel)`：
  - `repository: str`（min_length=1）
  - `files: List[str]`（min_length=1）
  - `language: str`（min_length=1）
- 名称以 `DTO` 结尾

## VO 模块 (`app/vo/`)

### Requirement 4: VO 包结构

系统 SHALL 提供 `app/vo/` 包，包含：
- `__init__.py`：包初始化
- `installation_vo.py`：安装相关响应 VO
- `translation_task_vo.py`：翻译任务和公共预览响应 VO

### Requirement 5: 安装验证 VO

`app/vo/installation_vo.py` SHALL 定义：
- `InstallationVO(BaseModel)`：
  - `installation_id: int`
  - `account_login: str`
  - `account_type: str`
  - `repository_selection: str`
- `RepositoryItemVO(BaseModel)`：
  - `full_name: str`
  - `default_branch: str`
  - `private: bool`
- `RepositoryListVO(BaseModel)`：
  - `repositories: list[RepositoryItemVO]`
- 名称以 `VO` 结尾

### Requirement 6: 翻译任务 VO

`app/vo/translation_task_vo.py` SHALL 定义：
- `FileMappingVO(BaseModel)`：
  - `source_path: str`
  - `target_path: str`
- `TranslationTaskVO(BaseModel)`：
  - `status: str`
  - `pr_url: str | None`
  - `pr_number: int | None`
  - `mappings: list[FileMappingVO] | None`
  - `error_code: str | None`
  - `error_message: str | None`
- `FilePreviewVO(BaseModel)`：
  - `source_path: str`
  - `target_path: str`
  - `translated_content: str`
- `PublicPreviewVO(BaseModel)`：
  - `previews: list[FilePreviewVO]`
- 名称以 `VO` 结尾

## 控制器集成

### Requirement 7: 控制器导入规范

控制器 SHALL 从 `app/dto/` 导入所有请求模型，从 `app/vo/` 导入所有响应模型。
控制器 SHALL NOT 内联定义 Pydantic 模型。
控制器 SHALL NOT 从 `app/domain/` 或 `app/services/` 导入模型用于响应序列化。

### Requirement 8: 安装控制器迁移

`app/api/installations.py` SHALL：
- 从 `app.dto.installation_dto` 导入 `VerifyInstallationDTO`
- 从 `app.vo.installation_vo` 导入 `InstallationVO`, `RepositoryItemVO`, `RepositoryListVO`
- 移除内联定义的 `VerifyRequest`, `InstallationResponse`, `RepositoryItem`, `RepositoryListResponse`

### Requirement 9: 翻译任务控制器迁移

`app/api/tasks.py` SHALL：
- 从 `app.dto.translation_task_dto` 导入 `CreateTranslationTaskDTO`
- 从 `app.vo.translation_task_vo` 导入 `TranslationTaskVO`
- 移除内联定义的 `TranslationTaskRequest`
- 将 `TaskResult` 转换为 `TranslationTaskVO` 返回

### Requirement 10: 公共预览控制器迁移

`app/api/public_preview.py` SHALL：
- 从 `app.dto.translation_task_dto` 导入 `CreatePublicPreviewDTO`
- 从 `app.vo.translation_task_vo` 导入 `PublicPreviewVO`
- 移除内联定义的 `PublicPreviewRequest`, `ErrorResponse`
- 将 `PublicPreviewResult` 转换为 `PublicPreviewVO` 返回

## 测试要求

### Requirement 11: DTO 测试

`tests/dto/test_translation_task_dto.py` SHALL 验证：
- `CreateTranslationTaskDTO` 字段校验（必填、min_length）
- `CreatePublicPreviewDTO` 字段校验

### Requirement 12: VO 测试

`tests/vo/test_translation_task_vo.py` SHALL 验证：
- `TranslationTaskVO` 序列化输出
- `PublicPreviewVO` 序列化输出
- VO 不包含 ORM Model 引用
