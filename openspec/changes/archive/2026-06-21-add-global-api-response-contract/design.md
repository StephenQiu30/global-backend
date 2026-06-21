## Context

当前后端有五种控制器（installation、repository、translation_task、language、public_preview），各自定义 `responses={...}` 和错误处理逻辑。错误响应体形状有三种变体（`SimpleErrorVO`、`RetryableErrorVO`、`CodeMessageErrorVO`），错误码键名不统一（`error` vs `error_code`），成功响应没有外层信封。

`AppError` 异常类已定义在 `app/core/errors.py`，但仅被 `translation_task_controller.py` 的 `map_error_to_response` 函数引用，且该函数未被实际调用。

现有 `task-result-errors` spec 定义了 `AppError` 和安全错误映射的局部合同，本 change 将其提升为全局合同。

## Goals / Non-Goals

**Goals:**
- 定义统一的成功/错误响应信封结构
- 定义大写枚举响应码集合
- 明确 HTTP 状态码语义保持不变
- 明确控制器不应维护本地错误映射
- 为后续实现 change 提供明确的 SDD 合同

**Non-Goals:**
- 不实现生产代码（响应信封 Pydantic 模型、异常处理器、控制器迁移）
- 不强制所有错误返回 HTTP 200
- 不重构无关业务逻辑
- 不修改前端代码
- 不引入 middleware-only 响应包装（会破坏 FastAPI OpenAPI 准确性）

## Decisions

### 1. 响应信封使用四字段结构

**决策**: 成功和错误响应统一使用 `{"code": str, "message": str, "data": Any | null, "trace_id": str}` 信封。

**理由**: 四字段覆盖了响应码、人类可读消息、业务数据和分布式追踪需求。`data: null` 明确标识错误响应，避免歧义。

### 2. 响应码使用大写枚举

**决策**: 响应码为大写字符串枚举，如 `SUCCESS`、`VALIDATION_ERROR`、`GITHUB_API_ERROR`。

**理由**: 大写枚举在 JSON 中醒目、易于 grep、与 Python Enum 惯例一致。包含 ticket 描述中指定的全部 11 个码。

### 3. HTTP 状态码保持语义

**决策**: 错误响应的 HTTP 状态码保持 RESTful 语义（400、401、403、404、422、429、500、502、504），不强制所有错误返回 HTTP 200。

**理由**: 保持 HTTP 语义使 API 网关、监控工具和浏览器缓存正常工作。FastAPI 的 `responses={...}` 装饰器依赖真实状态码生成 OpenAPI 文档。

### 4. 控制器不维护本地错误映射

**决策**: 控制器 SHALL NOT 维护 `_ERROR_STATUS_MAP` 等本地映射或解析异常字符串。异常到响应的转换由集中异常处理器完成。

**理由**: 本地映射导致错误码重复定义、状态码不一致、新端点容易遗漏。集中处理确保全局一致。

### 5. 信封通过 Pydantic 模型实现

**决策**: 实现阶段使用 `ResponseEnvelope[T]` 泛型 Pydantic 模型，`code` 字段使用 `ResponseCode` 枚举。

**理由**: Pydantic 模型与 FastAPI 深度集成，支持 OpenAPI schema 生成、序列化验证和类型提示。泛型允许 `data` 字段类型安全。

### 6. 集中异常处理器注册到 FastAPI app

**决策**: 实现阶段在 `app/main.py` 中通过 `app.add_exception_handler()` 注册 `AppError` 和通用异常处理器。

**理由**: FastAPI 原生支持自定义异常处理器，注册后所有端点自动受益，无需控制器手动 catch。

## Risks / Trade-offs

- **信封增加响应体积**: 每个响应多出 `code`、`message`、`trace_id` 字段 → 体积增量可忽略
- **控制器迁移需要逐端点进行**: 现有 5 个控制器的 `responses={...}` 和错误处理需要逐步迁移 → 后续 change 分批执行
- **`trace_id` 依赖请求上下文**: 需要 middleware 或 context var 注入 trace_id → 实现时处理
- **FastAPI OpenAPI schema 需要适配**: 信封包装后 OpenAPI schema 会变化 → 实现阶段确保 `response_model` 正确

## File Structure

```
app/
  vo/
    response_envelope.py      # ResponseEnvelope[T] 泛型模型
  core/
    response_codes.py         # ResponseCode 枚举（大写响应码）
    exception_handlers.py     # 集中异常处理器
```

## Open Questions

- 无（所有设计决策已确定）
