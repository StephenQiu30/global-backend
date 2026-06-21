## Queue Adapter

### TranslationTaskQueue

- 位置：`app/queues/translation_task_queue.py`
- 职责：封装 RQ 队列入队操作
- 方法：`enqueue(task_id: str) -> rq.job.Job`
  - 接收 task_id 字符串
  - 将 `run_translation_task` 函数入队，参数为 `task_id`
  - 使用配置中的队列名称
  - 返回 RQ Job 对象
- 构造函数：接收 `queue_name` 参数（从 config 传入）
- 内部创建 `rq.Queue` 实例

## Worker Job

### run_translation_task

- 位置：`app/workers/translation_jobs.py`
- 职责：RQ worker 入口函数
- 签名：`def run_translation_task(task_id: str) -> None`
- 行为：
  - 接收 task_id
  - 委托给 application service 执行翻译
  - 当前阶段为桩实现（打印日志），待 application service 层完成后对接
- 设计约束：
  - 不包含重试逻辑
  - 不包含状态更新逻辑（由 application service 负责）
  - 不包含错误分类逻辑（由 task_runner 负责）

## Configuration

### Settings 扩展

- `redis_url: str = "redis://localhost:6379/0"`
  - Redis 连接地址
  - 环境变量：`REDIS_URL`
- `rq_queue_name: str = "translation"`
  - RQ 队列名称
  - 环境变量：`RQ_QUEUE_NAME`

## Test Strategy

### Unit Tests（不依赖 live Redis）

- 使用 `unittest.mock.patch` 模拟 `rq.Queue.enqueue`
- 验证 enqueue 被调用且参数正确
- 验证队列名称来自 config
- 测试文件：`tests/queues/test_translation_task_queue.py`

### Integration Tests（可选，需 live Redis）

- 标记 `@pytest.mark.integration`
- 验证实际入队到 Redis
- 不在默认测试套件中运行

## Non-Goals

- 不实现重试策略
- 不实现优先级队列
- 不实现定时任务
- 不实现 RQ dashboard
- 不实现 worker 部署自动化
- 不实现任务状态回调
