## Tasks

- [x] 1. 添加 rq 和 redis 依赖到 pyproject.toml
- [x] 2. 添加 redis_url 和 rq_queue_name 到 Settings
- [x] 3. 编写 config 测试（红灯）
- [x] 4. 实现 config 变更（绿灯）
- [x] 5. 创建 app/queues/ 和 app/workers/ 目录结构
- [x] 6. 编写 TranslationTaskQueue 测试（红灯）
- [x] 7. 实现 TranslationTaskQueue（绿灯）
- [x] 8. 编写 worker job 测试（红灯）
- [x] 9. 实现 worker job（绿灯）
- [x] 10. 运行完整测试套件验证
- [x] 11. 更新 OpenSpec 任务状态

## Commit Plan

- [x] `test:` config 测试（redis_url, rq_queue_name）
- [x] `impl:` config 实现
- [x] `test:` TranslationTaskQueue 入队测试
- [x] `impl:` TranslationTaskQueue 实现
- [x] `test:` worker job 测试
- [x] `impl:` worker job 实现
- [x] `chore:` 依赖添加（pyproject.toml）
