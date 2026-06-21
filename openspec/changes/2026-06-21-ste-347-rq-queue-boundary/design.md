## Architecture Decisions

### 1. 使用 rq 而非 Celery

**决策：** 使用 `rq`（Redis Queue）作为任务队列。

**理由：**
- rq 更轻量，适合当前规模
- 无 broker 配置复杂度
- 与 Redis 直接集成
- Celery 的多 broker、多 backend、任务编排功能当前不需要

### 2. 队列适配器模式

**决策：** `TranslationTaskQueue` 封装 `rq.Queue`，而非直接在 service 中使用 `rq.Queue`。

**理由：**
- 隔离 RQ 依赖，便于测试
- 统一队列名称管理
- 后续可扩展为 Protocol 接口
- 与项目 Protocol-based DI 模式一致

### 3. Worker 函数而非 Worker 类

**决策：** 使用顶层函数 `run_translation_task(task_id)` 作为 RQ job。

**理由：**
- RQ 原生支持函数作为 job
- 避免不必要的类封装
- 函数签名清晰，易于测试
- 后续可直接委托给 application service

### 4. 桩实现策略

**决策：** worker 函数当前为桩实现，仅打印日志。

**理由：**
- application service 层（Task 6）尚未实现
- 队列边界可以独立验证
- 桩实现确保 RQ 调用链路完整
- 后续对接时只需替换函数体

### 5. 配置分离

**决策：** `redis_url` 和 `rq_queue_name` 作为独立配置项。

**理由：**
- 队列名称可能因环境不同（dev/staging/prod）
- Redis URL 需要独立配置
- 遵循现有 pydantic-settings 模式
- 默认值适合本地开发

## Dependency Flow

```
app/queues/translation_task_queue.py
  -> rq.Queue
  -> app/core/config.py (queue_name)

app/workers/translation_jobs.py
  -> (future) app/application/translation_task_service.py

tests/queues/test_translation_task_queue.py
  -> unittest.mock.patch("rq.Queue.enqueue")
  -> app.queues.translation_task_queue
```

## Test Mock Strategy

使用 `unittest.mock.patch` 而非 `fakeredis`：

- `fakeredis` 引入额外测试依赖
- RQ 的 `Queue.enqueue` 是纯 Python 调用，可直接 mock
- mock 更明确地表达"测试入队调用，不测试 Redis 行为"
- 集成测试可选使用真实 Redis
