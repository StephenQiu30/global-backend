# PRD 07: GitHub 分支、提交与 PR 创建

## 1. 目标

翻译完成后，系统通过 GitHub App 在目标仓库创建翻译分支，写入翻译文件，并创建 Pull Request 供维护者审核。

## 2. 用户故事

作为维护者，我希望系统不要直接修改主分支，而是创建 PR，这样我可以审核翻译内容、触发 CI，并决定是否合并。

## 3. GitHub 操作顺序

1. 获取默认分支。
2. 获取默认分支最新 commit SHA。
3. 创建翻译分支。
4. 写入一个或多个翻译文件。
5. 创建 commit。
6. 创建 PR。
7. 返回 PR URL。

## 4. 文件写入规则

1. 只写目标语言后缀文件。
2. 不覆盖源文件。
3. 目标文件存在时允许更新。
4. 多文件翻译必须进入同一个分支和 PR。
5. 失败时不创建半成品 PR。

## 5. PR 内容

PR 标题示例：

`docs: add zh-CN translation for Markdown docs`

PR 描述包含：

1. 自动翻译声明。
2. 目标语言。
3. 源文件与目标文件映射。
4. 翻译 Provider。
5. 需要人工审核提醒。
6. 任务 ID。

## 6. 已存在 PR 策略

第一版策略：

1. 如果同一任务创建过 PR，返回已有 PR。
2. 如果目标分支已存在且 PR open，则更新分支。
3. 如果分支冲突，生成新的 task ID 分支。

## 7. 错误场景

1. GitHub App 没有 contents write 权限。
2. GitHub App 没有 pull requests write 权限。
3. 默认分支不存在。
4. 创建分支失败。
5. 写文件失败。
6. 创建 PR 失败。
7. GitHub API rate limit。

## 8. 验收标准

1. 成功任务必须创建 PR。
2. PR base 是仓库默认分支。
3. PR head 是系统创建的翻译分支。
4. PR 文件列表只包含目标翻译文件。
5. 前端能展示 PR URL。
