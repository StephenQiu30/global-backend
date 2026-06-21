# Proposal: 公开仓库只读翻译预览

## Status

- [x] Proposed
- [x] Accepted
- [x] Implemented
- [x] Verified
- [x] Archived

## Summary

为二期公开仓库添加只读翻译预览能力：公开仓库读客户端 + 翻译预览 API。只读，不执行任何 GitHub 写操作。

## Motivation

PRD 10 定义二期能力：用户输入公开仓库 URL，系统读取 Markdown 并生成翻译预览。提交回 GitHub 时引导安装 GitHub App。当前首版闭环仅支持已安装 GitHub App 的仓库，公开仓库预览能降低用户门槛。

## Scope

### In scope

- 公开仓库 Markdown 文件列表读取（无认证）
- 公开仓库 Markdown 内容读取（无认证）
- 翻译预览 API（`POST /api/public-preview`）
- 预览响应不含 PR URL
- GitHub write method 未调用的服务级测试

### Out of scope

- fork PR
- OAuth 用户授权
- 写入公开仓库
- 绕过 GitHub App 安装
- 前端预览页面（global-frontend）

### Non-goals

- public preview 绝不能写 GitHub

## Approach

1. 新增 `PublicRepositoryClient`：使用 httpx 无认证访问 GitHub API，复用 `app/domain/repository.py` 的 `parse_repository_input()` 和 `app/domain/markdown_files.py` 的文件过滤函数。
2. 新增 `POST /api/public-preview` 端点：接收 repository、files、language，返回翻译预览和目标文件名。
3. 复用现有 `TranslationProvider` 协议和 `FakeTranslationProvider` 进行测试。
4. 服务测试验证未调用任何 GitHub write method。

## Risks

- GitHub 未认证 API 有 rate limit（60 req/hr），需后续增加缓存策略（本 ticket 不实现缓存层）
- 公开仓库可能不存在或不可访问，需明确错误处理

## Normative files affected

- `docs/prd/github-translator/10-public-repository-preview-future.md` (source)
- `docs/plans/github-translator/10-public-repository-preview-future-plan.md` (source)
