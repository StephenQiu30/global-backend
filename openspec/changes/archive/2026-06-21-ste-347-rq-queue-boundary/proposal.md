## Why

翻译任务当前为同步执行，长时间运行会阻塞 API 请求。需要引入 Redis/RQ 作为后台任务队列边界，将翻译执行移至 worker 进程。此变更是 `add-pgsql-rq-persistence` 整体计划中队列层的最小实现。

## What Changes

- 新增 `pyproject.toml` 依赖：`rq`、`redis`
- 新增 `app/core/config.py` 配置：`redis_url`、`rq_queue_name`
- 新增 `app/queues/__init__.py`
- 新增 `app/queues/translation_task_queue.py`：`TranslationTaskQueue` 封装 RQ 入队
- 新增 `app/workers/__init__.py`
- 新增 `app/workers/translation_jobs.py`：worker 入口函数 `run_translation_task(task_id)`
- 新增 `tests/queues/__init__.py`
- 新增 `tests/queues/test_translation_task_queue.py`：使用 mock 验证入队行为
- 更新 `tests/test_config.py`：验证新配置项

## Capabilities

### New Capabilities
- `rq-queue-adapter`: TranslationTaskQueue.enqueue(task_id) 封装 RQ 入队
- `rq-worker-job`: run_translation_task(task_id) worker 入口函数
- `queue-config`: redis_url 和 rq_queue_name 环境变量配置

### Modified Capabilities
- 无（全新实现）

## Impact

- 新增 `rq` 和 `redis` 依赖
- 队列名称从配置读取，不硬编码
- 测试使用 mock 而非 live Redis（除非显式标记为集成测试）
- 不引入重试策略、定时任务、优先级队列或 dashboard
