## Task Domain (`app/domain/task.py`)

### Requirement 1: TaskStatus 枚举

系统 SHALL 定义 `TaskStatus` 枚举，包含以下状态：
- `queued`: 任务已创建，等待执行
- `running`: 任务正在执行
- `succeeded`: 任务成功完成
- `failed`: 任务执行失败

### Requirement 2: Task 输入模型

系统 SHALL 定义 `Task` 模型，包含以下字段：
- `task_id: str` — 唯一任务标识符
- `installation_id: str` — GitHub App installation ID
- `repository: str` — 仓库全名（owner/repo）
- `base_branch: str` — 基础分支名
- `files: list[str]` — 待翻译文件路径列表
- `language: str` — 目标语言代码
- `status: TaskStatus` — 当前状态（默认 queued）

### Requirement 3: TaskResult 输出模型

系统 SHALL 定义 `TaskResult` 模型，成功时包含：
- `status: TaskStatus` — 最终状态（succeeded 或 failed）
- `pr_url: str | None` — PR 链接（成功时有值）
- `pr_number: int | None` — PR 编号（成功时有值）
- `mappings: list[FileMapping] | None` — 文件映射（成功时有值）
- `error_code: str | None` — 错误码（失败时有值）
- `error_message: str | None` — 安全错误信息（失败时有值）

### Requirement 4: FileMapping 模型

系统 SHALL 定义 `FileMapping` 模型：
- `source_path: str` — 源文件路径
- `target_path: str` — 翻译后文件路径

### Requirement 5: 输入校验

`POST /api/translation-tasks` SHALL 校验：
- `installation_id` 非空
- `repository` 非空
- `base_branch` 非空
- `files` 非空列表
- `language` 非空

校验失败时返回 422 状态码。

## TranslationProvider (`app/services/translation_provider.py`)

### Requirement 6: TranslationProvider 协议

系统 SHALL 定义 `TranslationProvider` 协议，包含：
- `async def translate_markdown(self, source_content: str, target_language: str) -> str`

### Requirement 7: FakeTranslationProvider

测试 SHALL 提供 `FakeTranslationProvider`，返回可预测的翻译结果。

## TaskRunner (`app/services/task_runner.py`)

### Requirement 8: TaskRunner 执行流程

`TaskRunner` SHALL 执行以下流程：
1. 设置任务状态为 `running`
2. 逐个读取文件内容（通过 github_client）
3. 调用 TranslationProvider 翻译每个文件
4. 组装 TaskResult（成功或失败）

### Requirement 9: 失败处理

TaskRunner 遇到错误时 SHALL：
- 设置任务状态为 `failed`
- 返回安全的 error_code 和 error_message
- 不泄露内部堆栈或敏感信息

错误码包括：
- `file_read_error`: 文件读取失败
- `translation_error`: 翻译失败
- `unknown_error`: 未知错误

## Translation Task Controller (`app/controller/translation_task_controller.py`)

### Requirement 10: POST /api/translation-tasks

系统 SHALL 提供 `POST /api/translation-tasks` 端点：
- 接收 JSON body：`{ installation_id, repository, base_branch, files, language }`
- 同步执行任务并返回结果
- 成功返回 200 + TaskResult JSON
- 校验失败返回 422

### Requirement 11: 成功响应格式

成功响应 SHALL 包含：
```json
{
  "status": "succeeded",
  "pr_url": "https://github.com/owner/repo/pull/123",
  "pr_number": 123,
  "mappings": [
    { "source_path": "README.md", "target_path": "README.zh-CN.md" }
  ]
}
```

### Requirement 12: 失败响应格式

失败响应 SHALL 包含：
```json
{
  "status": "failed",
  "error_code": "translation_error",
  "error_message": "Translation provider returned an error"
}
```
