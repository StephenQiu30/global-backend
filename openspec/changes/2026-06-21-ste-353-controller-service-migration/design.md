## Context

基于 `add-global-api-response-contract` 已归档的 SDD 合同，本 change 实现控制器和服务层的迁移。

现有基础设施已就绪：
- `ApiResponseVO[T]` 泛型信封模型（`app/core/response.py`）
- `ErrorCode` 大写枚举（11 个响应码）
- `AppException` 结构化异常（`app/core/exceptions.py`）
- `success_response()` / `error_response()` 辅助函数
- 全局异常处理器（已注册到 FastAPI app）

需要迁移的组件：
- 5 个控制器（installation、repository、public_preview、translation_task、language）
- 4 个服务文件中的 `ValueError`（github_app、public_repository、translation_task_service、markdown_discovery）
- 旧式错误 VO 和 `AppError` 异常类

## Goals / Non-Goals

**Goals:**
- 所有控制器返回 `ApiResponseVO[...]` 信封
- 服务层使用 `AppException` 替代 `ValueError` 作为跨层业务错误
- 移除控制器中的 `_ERROR_STATUS_MAP` 和字符串解析逻辑
- 保持 HTTP 状态码语义不变
- 更新测试验证信封格式

**Non-Goals:**
- 不引入新端点或业务能力
- 不修改数据库模型或迁移
- 不修改前端代码
- 不重构无关业务逻辑

## Decisions

### 1. 服务层使用 AppException 替代 ValueError

**决策**: 服务层抛出 `AppException(ErrorCode, message, http_status)` 替代 `ValueError`。

**理由**: `AppException` 携带类型安全的 `ErrorCode` 枚举和 HTTP 状态码，控制器无需解析异常字符串。全局异常处理器自动将其转换为 `ApiResponseVO` 错误信封。

### 2. 控制器使用 success_response() 包装成功响应

**决策**: 控制器的成功返回使用 `success_response(data)` 包装，返回 `ApiResponseVO` 信封。

**理由**: 统一成功响应格式，包含 `code`, `message`, `data`, `trace_id` 字段。

### 3. 移除 AppError 和旧式错误 VO

**决策**: 删除 `app/core/errors.py` 中的 `AppError` 类和 `app/vo/error_vo.py` 中的旧式错误模型。

**理由**: `AppError` 被 `AppException` 完全替代，旧式错误 VO 不再使用。

### 4. 保留 ErrorCode → HTTP 状态码映射

**决策**: 保留 `app/core/response.py` 中的 `ERROR_CODE_HTTP_STATUS` 映射表，供全局异常处理器使用。

**理由**: 全局异常处理器需要根据 `ErrorCode` 确定 HTTP 状态码。

## Risks / Trade-offs

- **测试需要更新**: 现有测试验证旧响应格式，需要更新为信封格式 → 预期工作量
- **前端需要适配**: 响应格式变更需要前端调整 → 不在本 change 范围
- **`AppError` 删除可能影响其他模块**: 需要检查是否有其他地方使用 → 已确认仅 `github_app.py` 和 `translation_task_controller.py` 使用

## File Structure

```text
app/
  core/
    errors.py              # 删除 AppError
    response.py            # 保留（已有 ApiResponseVO, ErrorCode）
    exceptions.py          # 保留（已有 AppException, 全局处理器）
  vo/
    error_vo.py            # 删除旧式错误模型
  controller/
    installation_controller.py      # 迁移
    repository_controller.py        # 迁移
    public_preview_controller.py    # 迁移
    translation_task_controller.py  # 迁移
    language_controller.py          # 迁移
  services/
    github_app.py                  # 迁移 ValueError → AppException
    public_repository.py           # 迁移 ValueError → AppException
    translation_task_service.py    # 迁移 ValueError → AppException
    markdown_discovery.py          # 迁移 ValueError → AppException
tests/
  api/                            # 更新测试
  controller/                     # 更新测试
```
