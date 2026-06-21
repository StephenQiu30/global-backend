## Why

后端控制器（installation、repository、public_preview、translation_task、language）各自定义 `responses={...}` 和本地错误处理逻辑，使用 `HTTPException` 直接抛出不一致的错误响应体。服务层使用 `ValueError` 字符串作为业务错误契约，控制器需要解析异常字符串来决定 HTTP 状态码。

本 change 实现 `add-global-api-response-contract` 中定义的 SDD 合同，将所有控制器和服务迁移到统一的 `ApiResponseVO` 信封和 `AppException` 异常体系。

## What Changes

- 服务层：将 `ValueError` 替换为 `AppException(ErrorCode, ...)`，使业务错误类型安全
- 控制器层：使用 `success_response()` 包装成功响应，移除本地 `_ERROR_STATUS_MAP` 和字符串解析逻辑
- 删除 `AppError`（`app/core/errors.py`）和旧式错误 VO（`app/vo/error_vo.py`）
- 更新测试以验证统一信封响应格式

## Capabilities

### Modified Capabilities
- `global-api-response`: 实现控制器和服务层迁移

## Impact

- 所有现有 API 端点响应格式变更：外层增加 `code`, `message`, `data`, `trace_id` 字段
- HTTP 状态码语义保持不变
- 前端需适配新的响应信封格式（不在本 change 范围内）
