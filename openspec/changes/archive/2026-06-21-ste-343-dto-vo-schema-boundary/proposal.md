## Why

PRD 11.4 要求拆分 DTO（入站请求）与 VO（出站响应）Schema 边界，使控制器不再内联定义 schema，ORM Model 不直接暴露为 API 输出。当前 FastAPI 路由在 `app/api/` 中内联定义 Pydantic 模型，违反分层原则。

## What Changes

- 新增 `app/dto/__init__.py`：DTO 包初始化
- 新增 `app/dto/installation_dto.py`：安装验证请求 DTO
- 新增 `app/dto/translation_task_dto.py`：翻译任务和公共预览请求 DTO
- 新增 `app/vo/__init__.py`：VO 包初始化
- 新增 `app/vo/installation_vo.py`：安装验证和仓库列表响应 VO
- 新增 `app/vo/translation_task_vo.py`：翻译任务和公共预览响应 VO
- 修改 `app/api/installations.py`：从 `app/dto/` 导入请求模型，从 `app/vo/` 导入响应模型
- 修改 `app/api/tasks.py`：从 `app/dto/` 导入请求模型，从 `app/vo/` 导入响应模型
- 修改 `app/api/public_preview.py`：从 `app/dto/` 导入请求模型，从 `app/vo/` 导入响应模型
- 新增 `tests/dto/test_translation_task_dto.py`：DTO 校验测试
- 新增 `tests/vo/test_translation_task_vo.py`：VO 序列化测试

## Capabilities

### New Capabilities
- `installation-dto`: 安装验证请求 DTO（VerifyInstallationDTO）
- `translation-task-dto`: 翻译任务请求 DTO（CreateTranslationTaskDTO）和公共预览请求 DTO（CreatePublicPreviewDTO）
- `installation-vo`: 安装验证响应 VO（InstallationVO）和仓库列表响应 VO（RepositoryItemVO, RepositoryListVO）
- `translation-task-vo`: 翻译任务响应 VO（TranslationTaskVO, FileMappingVO）和公共预览响应 VO（PublicPreviewVO, FilePreviewVO）

### Modified Capabilities
- `installation-api`: 控制器改为从 `app/dto/` 和 `app/vo/` 导入 schema
- `translation-task-api`: 控制器改为从 `app/dto/` 和 `app/vo/` 导入 schema
- `public-preview-api`: 控制器改为从 `app/dto/` 和 `app/vo/` 导入 schema

## Impact

- 控制器不再内联定义 Pydantic 模型
- 响应模型独立于领域模型，可独立演进
- DTO/VO 命名约定：DTO 以 `DTO` 结尾，VO 以 `VO` 结尾
- 领域模型（`app/domain/`）保持不变，继续作为业务逻辑核心
