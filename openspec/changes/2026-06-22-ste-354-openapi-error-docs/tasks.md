## 1. SDD 文档产出（本 change）

- [x] 1.1 完成 `openspec/changes/2026-06-22-ste-354-openapi-error-docs/proposal.md`
- [x] 1.2 完成 `openspec/changes/2026-06-22-ste-354-openapi-error-docs/specs/openapi-error-docs/spec.md`
- [x] 1.3 完成 `openspec/changes/2026-06-22-ste-354-openapi-error-docs/design.md`
- [x] 1.4 完成 `openspec/changes/2026-06-22-ste-354-openapi-error-docs/tasks.md`

## 2. 实现

- [x] 2.1 `test:` 为 `app/core/openapi.py` 编写红灯测试（`tests/core/test_openapi.py`）
- [x] 2.2 `impl:` 实现 `app/core/openapi.py`：`common_error_responses` 辅助函数
- [x] 2.3 `test:` 更新 `tests/controller/test_openapi_docs.py`：验证所有端点都有错误响应文档
- [x] 2.4 `impl:` 更新所有控制器的路由装饰器，使用 `common_error_responses` 添加 `responses`
- [x] 2.5 `chore:` 删除 `app/core/errors.py`（未使用的 `AppError` 类）
- [x] 2.6 `docs:` 更新 `docs/design/backend-engineering-architecture-review.md`，记录全局响应合同和 OpenAPI 辅助函数

## 3. 验证

- [x] 3.1 `pytest tests/core/test_openapi.py -v` 通过（10/10）
- [x] 3.2 `pytest tests/controller/test_openapi_docs.py -v` 通过（18/18）
- [x] 3.3 `pytest tests/ -v` 全量通过（547/547）
- [x] 3.4 `bash scripts/validate-repository.sh` 通过
