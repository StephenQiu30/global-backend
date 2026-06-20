# Proposal: GitHub 分支、文件写入与 PR 创建

## Summary

实现翻译任务完成后的 GitHub 写操作：创建翻译分支、写入翻译文件、创建 Pull Request。

## Normative files to change

- `app/services/github_app.py` (new) — GitHub 分支/文件/PR API
- `app/services/pr_description.py` (new) — PR body 纯函数
- `app/services/task_runner.py` (new) — PR flow 串联
- `tests/services/test_github_branch_creation.py` (new)
- `tests/services/test_github_file_write.py` (new)
- `tests/services/test_github_pr_creation.py` (new)
- `tests/services/test_pr_description.py` (new)
- `tests/services/test_task_runner_pr_flow.py` (new)

## Non-goals

- PR 自动合并
- CI 状态轮询
- Review comment 处理
- 不写源文件，不直接 push 默认分支

## Scope

- `create_branch`: 从默认分支 SHA 创建翻译分支
- `put_file`: 写入翻译文件（base64 编码），支持更新已有文件
- `create_pull_request`: 创建或复用 PR
- `build_translation_pr_body`: 纯函数生成 PR 描述
- Task runner PR flow: 确保翻译全部完成后才执行 GitHub 写操作，翻译失败不创建半成品 PR
