# PRD 01: GitHub App 安装与授权

## 1. 目标

让用户通过 Web 应用完成 GitHub App 安装，授权指定账号和仓库，使系统具备读取 Markdown 文件、创建分支、写文件、创建 Pull Request 的权限。

## 2. 用户故事

作为项目维护者，我希望在网页中点击安装 GitHub App，选择需要翻译文档的仓库，并在安装完成后看到授权结果，这样我就能安全地让系统为仓库提交翻译 PR。

## 3. 入口

前端首页必须提供明确入口：

1. 安装 GitHub App。
2. 查看安装状态。
3. 查看已授权仓库。
4. 查看权限说明。

第一版不要求完整用户账号系统。GitHub App installation 是主要权限边界。

## 4. 安装流程

1. 用户点击 `安装 GitHub App`。
2. 前端跳转到 GitHub App 安装 URL。
3. 用户在 GitHub 上选择个人账号或组织。
4. 用户选择全部仓库或指定仓库。
5. GitHub 安装完成后回跳到前端 callback URL。
6. 前端读取 `installation_id`。
7. 前端调用后端校验安装。
8. 后端调用 GitHub API 获取 installation 信息。
9. 后端返回安装账号、仓库列表和权限状态。
10. 前端展示安装成功页面。

## 5. 权限需求

GitHub App 第一版需要的权限：

1. `Contents: Read and write`，读取 Markdown 文件并写入翻译文件。
2. `Pull requests: Read and write`，创建 PR。
3. `Metadata: Read-only`，读取仓库基础信息。
4. `Issues: Read-only` 可选，第一版 Web 流程不依赖 issue 评论。

不需要的权限：

1. 不需要管理 Actions。
2. 不需要删除仓库内容。
3. 不需要管理 secrets。
4. 不需要管理成员权限。

## 6. 前端展示要求

安装成功页展示：

1. GitHub 账号或组织名。
2. 安装 ID。
3. 已授权仓库数量。
4. 已授权仓库列表。
5. 下一步按钮：`开始翻译仓库文档`。

安装失败页展示：

1. 失败原因。
2. 重试按钮。
3. 返回首页按钮。

## 7. 后端接口需求

建议接口：

1. `GET /api/github/app/install-url`：返回安装 URL。
2. `POST /api/github/installations/verify`：校验 installation。
3. `GET /api/github/installations/{installation_id}/repositories`：列出授权仓库。

## 8. 错误场景

1. 用户取消安装：前端提示未完成安装。
2. `installation_id` 缺失：前端提示回调参数无效。
3. GitHub API 调用失败：后端返回可读错误。
4. App 权限不足：提示需要重新安装或更新权限。
5. installation 不属于当前 App：后端拒绝。

## 9. 验收标准

1. 用户能从首页跳转到 GitHub App 安装页面。
2. 安装完成后能回到前端 callback 页面。
3. 后端能校验 installation 并返回仓库列表。
4. 前端能展示已授权仓库。
5. 安装失败时有明确错误提示。
