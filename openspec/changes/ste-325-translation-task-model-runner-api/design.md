## Context

PRD 05 要求实现翻译任务的核心执行层。这是翻译流程的中心组件，连接任务输入（API）、文件读取（GitHub）和翻译能力（Provider）。

当前项目已有：
- `app/domain/markdown_files.py`（PRD 03）：Markdown 文件分类和路径规则
- `app/domain/repository.py`（PRD 02）：仓库地址解析
- `app/services/markdown_discovery.py`（PRD 03）：文件发现服务
- `app/core/config.py`：应用配置
- `app/main.py`：FastAPI 应用工厂

本 change 不依赖 PRD 01-04 的授权和文件校验已完成实现；通过依赖注入（github_client、translation_provider）解耦外部依赖。

## Goals / Non-Goals

**Goals:**
- 定义 Task/TaskResult 领域模型和 TaskStatus 枚举
- 定义 TranslationProvider 协议（接口）
- 实现 TaskRunner 同步执行器
- 实现 `POST /api/translation-tasks` API 端点
- 遵循 TDD 流程

**Non-Goals:**
- 队列 worker 或异步任务
- 重试系统
- 计费额度检查
- 前端状态页
- 公开仓库预览或 issue 评论命令
- 实际的 GitHub API 调用（通过注入解耦）
- 实际的 OpenAI 翻译调用（只定义协议）

## Decisions

### 1. 领域模型使用 Pydantic BaseModel

**决策**: Task、TaskResult、FileMapping 使用 Pydantic BaseModel。

**理由**: 与项目既有模式一致（RepositoryRef），可直接用于 API 响应序列化，提供类型验证。

### 2. TranslationProvider 使用 Protocol

**决策**: 使用 Python `typing.Protocol` 定义 TranslationProvider。

**理由**: 结构化子类型，允许 Fake 实现无需继承。符合 Python 最佳实践。

### 3. TaskRunner 通过构造函数注入依赖

**决策**: `TaskRunner(translation_provider, github_client)` 通过构造函数注入。

**理由**: 便于测试（传入 Fake），符合依赖反转原则。

### 4. 同步执行模式

**决策**: 首版采用同步执行，API 等待任务完成后返回结果。

**理由**: 简化实现，满足 PRD 05 首版要求。后续可改为异步 + 状态查询。

### 5. 错误码为安全字符串

**决策**: 失败时返回 `error_code`（枚举值）和 `error_message`（安全描述），不泄露内部信息。

**理由**: 前端可根据 error_code 展示不同提示，安全描述不暴露实现细节。

## Risks / Trade-offs

- **同步执行阻塞**: 大文件或多文件任务可能导致 API 响应慢 → 首版可接受，后续改异步
- **无实际 GitHub/Provider 实现**: 依赖注入解耦，测试用 Fake → 后续 PRD 实现具体 Provider
- **无任务持久化**: 任务结果只在内存中 → 首版可接受

## Migration Plan

1. 创建 `app/domain/task.py`（领域模型）
2. 创建 `app/services/translation_provider.py`（协议）
3. 创建 `app/services/task_runner.py`（执行器）
4. 创建 `app/api/tasks.py`（API 端点）
5. 注册路由到 `app/main.py`
6. 验证：`pytest tests/domain/test_task.py tests/services/test_task_runner.py tests/api/test_translation_tasks.py -v`
