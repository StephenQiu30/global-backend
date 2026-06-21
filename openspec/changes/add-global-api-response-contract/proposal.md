## Why

后端控制器目前逐端点定义 `responses={...}`，错误响应体形状不一致：`SimpleErrorVO` 使用 `{"error": "..."}`、`RetryableErrorVO` 使用 `{"error": "...", "message": "...", "retryable": ...}`、`CodeMessageErrorVO` 使用 `{"error_code": "...", "message": "..."}`。错误码键名在 `error` 和 `error_code` 之间不统一，成功响应没有外层信封，控制器各自维护本地错误映射或解析异常字符串。

本 change 定义全局 API 响应信封和异常处理合同，为后续控制器迁移和前端集成提供统一规范。

## What Changes

- 定义全局成功响应信封：`{"code": "SUCCESS", "message": "OK", "data": ..., "trace_id": "..."}`
- 定义全局错误响应信封：`{"code": "GITHUB_API_ERROR", "message": "...", "data": null, "trace_id": "..."}`
- 定义大写枚举响应码：`SUCCESS`、`VALIDATION_ERROR`、`INTERNAL_ERROR`、`GITHUB_API_ERROR`、`TASK_NOT_FOUND`、`INSTALLATION_NOT_FOUND`、`REPOSITORY_NOT_FOUND`、`REPOSITORY_NOT_INSTALLED`、`GITHUB_RATE_LIMITED`、`TRANSLATION_ERROR`、`UNSUPPORTED_LANGUAGE`
- 明确 HTTP 状态码保持语义，错误不强制返回 HTTP 200
- 明确控制器不应维护本地错误映射或解析异常字符串

## Capabilities

### New Capabilities
- `global-api-response`: 全局 API 响应信封、枚举响应码和集中异常处理合同

### Modified Capabilities
- 无（纯 SDD 合同定义，不修改现有能力实现）

## Impact

- 本 change 只产出 SDD 文档，不修改生产代码
- 后续 change 将基于此合同实现 `app/vo/response_envelope.py`、`app/core/response_codes.py`、`app/core/exception_handlers.py`
- 控制器迁移将在后续 change 中逐步完成
- 前端需适配新的响应信封格式（不在本 change 范围内）
