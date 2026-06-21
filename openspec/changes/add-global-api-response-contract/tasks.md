## 1. SDD 文档产出（本 change）

- [ ] 1.1 完成 `openspec/changes/add-global-api-response-contract/proposal.md`
- [ ] 1.2 完成 `openspec/changes/add-global-api-response-contract/specs/global-api-response/spec.md`
- [ ] 1.3 完成 `openspec/changes/add-global-api-response-contract/design.md`
- [ ] 1.4 完成 `openspec/changes/add-global-api-response-contract/tasks.md`
- [ ] 1.5 验证所有文档符合 OpenSpec config 规则：`bash scripts/validate-repository.sh`

## 2. 后续实现 change（不在本 change 范围，仅列出任务边界）

以下任务将在后续独立 change 中实现，本 change 只定义合同：

- [ ] 2.1 实现 `app/core/response_codes.py`：`ResponseCode` 枚举（11 个大写响应码）
- [ ] 2.2 实现 `app/vo/response_envelope.py`：`ResponseEnvelope[T]` 泛型 Pydantic 模型
- [ ] 2.3 实现 `app/core/exception_handlers.py`：集中异常处理器（`AppError` → 信封响应）
- [ ] 2.4 在 `app/main.py` 注册异常处理器
- [ ] 2.5 定义 `ResponseCode` → HTTP 状态码映射表
- [ ] 2.6 迁移 `app/controller/installation_controller.py`：移除本地错误映射，使用信封
- [ ] 2.7 迁移 `app/controller/repository_controller.py`：移除本地错误映射，使用信封
- [ ] 2.8 迁移 `app/controller/translation_task_controller.py`：移除 `map_error_to_response` 和 `_ERROR_STATUS_MAP`，使用信封
- [ ] 2.9 迁移 `app/controller/public_preview_controller.py`：移除本地错误映射，使用信封
- [ ] 2.10 迁移 `app/controller/language_controller.py`：使用信封
- [ ] 2.11 删除 `app/vo/error_vo.py` 中的 `SimpleErrorVO`、`MessageErrorVO`、`RetryableErrorVO`、`CodeMessageErrorVO`
- [ ] 2.12 删除 `app/vo/translation_task_vo.py` 中的 `TaskNotFoundVO`
- [ ] 2.13 更新所有控制器的 `responses={...}` 装饰器，使用新的错误信封 schema

## 3. 验证

- [ ] 3.1 运行 `bash scripts/validate-repository.sh` 确认仓库结构完整
- [ ] 3.2 人工 review spec 文档，对照现有控制器确认合同覆盖所有错误场景
- [ ] 3.3 确认 Agent Review 通过后归档本 change
