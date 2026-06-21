## Why

PRD 05 定义翻译任务创建、同步执行、状态和结果字段。后端需要接收翻译任务请求，读取选中文件，调用翻译 Provider，并返回结构化任务结果。这是翻译流程的核心执行层。

## What Changes

- 新增 `app/domain/task.py`：Task 和 TaskResult 领域模型，定义状态枚举和输入输出契约
- 新增 `app/services/translation_provider.py`：TranslationProvider 协议（接口），定义翻译能力抽象
- 新增 `app/services/task_runner.py`：TaskRunner 执行器，编排翻译任务流程
- 新增 `app/api/tasks.py`：`POST /api/translation-tasks` API 端点

## Capabilities

### New Capabilities
- `task-domain`: 翻译任务领域模型，包含 Task、TaskResult、TaskStatus 枚举
- `translation-provider`: 翻译能力抽象协议，支持 Fake 和 OpenAI 实现
- `task-runner`: 任务执行器，编排文件读取、翻译、结果组装
- `translation-task-api`: `POST /api/translation-tasks` 同步任务创建端点

### Modified Capabilities
- 无（全新实现）

## Impact

- 新增 API 端点：`POST /api/translation-tasks`
- 依赖翻译 Provider 抽象（本 change 只定义协议和 Fake 实现）
- 依赖 GitHub 文件读取能力（通过 github_client 参数注入）
- 任务状态：queued → running → succeeded/failed
- 失败结果包含安全的 error code 和 error message（不泄露内部信息）
