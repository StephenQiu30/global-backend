# GitHub Markdown Translator PRD 索引

本目录记录 GitHub Markdown Translator 的详细需求分析。每个功能点单独维护一个 PRD，便于后续拆分任务、验收和测试。

## PRD 列表

1. [PRD 00: 产品总览](00-product-overview.md)
2. [PRD 01: GitHub App 安装与授权](01-github-app-installation.md)
3. [PRD 02: 仓库地址解析与授权校验](02-repository-url-and-authorization.md)
4. [PRD 03: Markdown 文件扫描与选择](03-markdown-file-discovery.md)
5. [PRD 04: 目标语言选择](04-language-selection.md)
6. [PRD 05: 翻译任务创建与执行](05-translation-task.md)
7. [PRD 06: Markdown 保真翻译](06-markdown-fidelity.md)
8. [PRD 07: GitHub 分支、提交与 PR 创建](07-pr-submission.md)
9. [PRD 08: 任务状态与结果展示](08-task-status-and-results.md)
10. [PRD 09: 安全、权限与滥用防护](09-security-and-permissions.md)
11. [PRD 10: 公开仓库 URL 预览翻译后续能力](10-public-repository-preview-future.md)

## 第一版范围摘要

第一版只支持已安装 GitHub App 的仓库。用户通过 Web 页面输入或选择仓库，系统扫描 Markdown 文件，用户选择目标语言后，系统翻译文件并通过 Pull Request 提交到 GitHub。

技术选型：

1. 前端：Next.js + React + TypeScript + Tailwind CSS。
2. 后端：FastAPI + GitHub App API + OpenAI Translation Provider。

核心输出规则：

1. 不覆盖原始 Markdown 文件。
2. 使用同目录语言后缀，例如 `README.md` -> `README.zh-CN.md`。
3. 所有变更通过 PR 审核。
