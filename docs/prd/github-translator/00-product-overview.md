# PRD 00: GitHub Markdown Translator 产品总览

## 1. 背景

开源项目和团队项目通常以 Markdown 文档作为入口，例如 `README.md`、`docs/*.md`、贡献指南、安装说明和 API 文档。当前用户如果想把 GitHub 仓库文档翻译为其他语言，往往需要手动复制内容、调用翻译工具、维护 Markdown 格式，再手动提交到仓库。这一过程重复、容易破坏格式，也缺少 Pull Request 审核闭环。

本产品目标是提供一个 GitHub App 驱动的 Markdown 翻译工具。用户在 Web 页面中输入或选择已授权的 GitHub 仓库，系统自动解析 Markdown 文件，用户选择目标语言后，系统生成同目录语言后缀文件，并通过 Pull Request 提交回 GitHub。

## 2. 产品定位

产品名称暂定为 `GitHub Markdown Translator`。

第一版定位为：

1. 面向已安装 GitHub App 的仓库。
2. 通过 Web 页面完成仓库选择、文件选择、语言选择和翻译提交。
3. 通过 GitHub App 权限读取仓库文件、创建分支、写入翻译文件、创建 PR。
4. 保护原始 Markdown 结构，不覆盖原文文件。
5. 所有变更必须进入 PR 审核，不直接合并默认分支。

## 3. 技术选型

采用方案 A：`Next.js + FastAPI`。

`global-frontend`：

1. Next.js。
2. React。
3. TypeScript。
4. Tailwind CSS。
5. 负责安装入口、仓库输入、Markdown 文件选择、语言选择、任务状态和结果展示。

`global-backend`：

1. Python FastAPI。
2. GitHub App Webhook 与 GitHub REST API 集成。
3. OpenAI API 作为第一版翻译 Provider。
4. Markdown 分块、保护与重组。
5. 翻译任务执行、PR 创建和状态记录。

## 4. 第一版用户旅程

1. 用户访问 Web 应用。
2. 用户点击安装或登录 GitHub App。
3. GitHub 跳转到 App 安装页面，用户选择账号和仓库。
4. 安装完成后回到 Web 应用。
5. 用户输入 GitHub 仓库地址，或从已授权仓库列表中选择仓库。
6. 系统校验该仓库是否已授权给 GitHub App。
7. 系统扫描仓库 Markdown 文件。
8. 系统默认选中根目录 `README.md`，用户可多选其他 Markdown 文件。
9. 用户选择目标语言。
10. 用户提交翻译任务。
11. 系统读取文件、解析 Markdown、调用翻译模型、生成目标文件。
12. 系统创建翻译分支并提交文件。
13. 系统创建 PR。
14. 前端展示任务结果、PR 链接和翻译文件列表。

## 5. 第一版范围

必须实现：

1. GitHub App 安装入口和安装回调。
2. 已授权仓库校验。
3. GitHub 仓库 URL 解析。
4. Markdown 文件扫描。
5. 默认 README 选择与多文件选择。
6. 目标语言选择。
7. 翻译任务创建。
8. Markdown 保真翻译。
9. 同目录语言后缀输出。
10. GitHub 分支、提交和 PR 创建。
11. 任务状态展示。
12. 明确错误提示。

暂不实现：

1. 任意公开仓库的无授权提交。
2. fork 后提交 PR。
3. 自动合并 PR。
4. GitHub issue 评论命令触发。
5. 团队计费、额度、订阅。
6. 多翻译 Provider UI 切换。
7. 全仓库无限制翻译。

## 6. 后续方向

1. 任意公开仓库 URL 的只读解析和翻译预览。
2. fork + PR 模式。
3. GitHub issue 评论命令，例如 `/translate zh-CN README.md`。
4. 多 Provider：DeepL、Gemini、Claude。
5. 翻译记忆和术语表。
6. 仓库级配置文件，例如 `.github-translator.yml`。
7. 批量语言翻译。

## 7. 总体验收标准

1. 用户可以完成 GitHub App 安装并回到 Web 应用。
2. 用户可以输入已授权仓库地址并通过校验。
3. 系统可以展示仓库 Markdown 文件列表。
4. 用户可以选择目标语言并创建翻译任务。
5. 系统可以生成 `README.zh-CN.md` 这类同目录语言后缀文件。
6. 系统可以创建 GitHub PR。
7. PR 中包含所有翻译文件。
8. 前端可以展示任务成功或失败状态。
9. 失败时用户能看到具体原因。
10. 原始 Markdown 文件不会被覆盖。
