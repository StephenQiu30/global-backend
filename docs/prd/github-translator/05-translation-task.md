# PRD 05: 翻译任务创建与执行

## 1. 目标

用户选择仓库、文件和目标语言后，系统创建翻译任务，执行文件读取、Markdown 解析、AI 翻译、文件写入和 PR 创建。

## 2. 用户故事

作为用户，我希望点击一次提交后，系统能自动完成翻译并给我一个 PR 链接，这样我可以在 GitHub 中审核翻译结果。

## 3. 任务输入

任务创建需要：

1. installation ID。
2. owner。
3. repo。
4. base branch。
5. 文件路径列表。
6. 目标语言。
7. 当前用户或安装上下文。

## 4. 执行步骤

1. 校验仓库授权。
2. 校验文件列表。
3. 校验目标语言。
4. 读取源文件内容。
5. 解析 Markdown。
6. 调用翻译 Provider。
7. 生成目标文件内容。
8. 创建或复用翻译分支。
9. 写入目标文件。
10. 创建或更新 PR。
11. 保存任务结果。
12. 返回 PR 链接。

## 5. 分支命名

建议格式：

`translate/{language}/{timestamp-or-task-id}`

示例：

`translate/zh-CN/20260621-readme`

分支名必须：

1. ASCII 安全。
2. 不包含空格。
3. 不包含用户输入的原始路径片段，或必须做 slug 化。

## 6. PR 规则

PR 标题：

`docs: add {language} translation for Markdown docs`

PR 描述必须包含：

1. 源仓库。
2. 目标语言。
3. 翻译文件列表。
4. 源文件列表。
5. 是否更新已有翻译。
6. 自动生成声明。
7. 人工审核建议。

## 7. 同步与异步

第一版建议采用同步任务加超时：

1. 单次任务文件数和总大小有限。
2. 用户提交后进入任务处理中页面。
3. 后端执行完成后返回结果。
4. 超时则返回失败。

后续可升级为队列：

1. Redis/RQ 或 Celery。
2. 任务状态持久化。
3. 失败重试。
4. Webhook 或轮询更新。

## 8. 状态

第一版任务状态：

1. `queued`
2. `running`
3. `succeeded`
4. `failed`

状态字段：

1. task ID。
2. repository。
3. language。
4. selected files。
5. created PR URL。
6. error code。
7. error message。

## 9. 验收标准

1. 用户提交任务后能看到处理中状态。
2. 任务成功后能看到 PR 链接。
3. 任务失败后能看到具体失败原因。
4. PR 包含所有选中文件的翻译结果。
5. 原始文件不会被覆盖。
