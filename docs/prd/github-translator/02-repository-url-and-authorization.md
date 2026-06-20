# PRD 02: 仓库地址解析与授权校验

## 1. 目标

用户输入 GitHub 仓库地址后，系统自动解析 owner/repo，并校验该仓库是否已授权给 GitHub App。第一版只允许对已授权仓库创建翻译任务。

## 2. 用户故事

作为用户，我希望只需要粘贴 GitHub 仓库地址，系统就能识别仓库并告诉我是否可以翻译，这样我不需要理解 GitHub App installation 的技术细节。

## 3. 支持的输入格式

第一版支持：

1. `https://github.com/owner/repo`
2. `https://github.com/owner/repo/`
3. `github.com/owner/repo`
4. `owner/repo`

第一版不支持：

1. Git SSH 地址。
2. 子路径 URL，例如 `/tree/main/docs`。
3. Gist。
4. GitLab、Gitee 等非 GitHub 地址。

## 4. 解析规则

1. 去除 URL 前后空格。
2. 去除末尾 `/`。
3. 从 URL 中提取 owner 和 repo。
4. repo 名保留大小写，但比较时按 GitHub 返回结果为准。
5. 非法输入必须返回明确错误。

## 5. 授权校验

后端校验逻辑：

1. 根据当前 installation 列出授权仓库。
2. 匹配输入的 owner/repo。
3. 如果匹配成功，返回仓库元信息。
4. 如果未授权，返回 `repository_not_installed`。
5. 如果仓库不存在，返回 `repository_not_found`。

第一版不做公开仓库 fallback。未授权仓库只能提示安装 GitHub App。

## 6. 前端交互

仓库输入页包含：

1. 仓库地址输入框。
2. 已授权仓库下拉选择。
3. 校验按钮或自动校验。
4. 校验状态。
5. 错误提示。

成功状态展示：

1. 仓库全名。
2. 默认分支。
3. 仓库可见性。
4. 是否已授权。
5. 下一步：扫描 Markdown。

## 7. 错误场景

1. 地址为空。
2. 地址不是 GitHub 仓库。
3. owner/repo 格式错误。
4. 仓库不存在。
5. 仓库未授权。
6. GitHub API 超时。
7. installation token 获取失败。

## 8. 验收标准

1. 输入 `https://github.com/owner/repo` 能解析出 owner/repo。
2. 输入 `owner/repo` 能解析出 owner/repo。
3. 未授权仓库不能进入翻译流程。
4. 已授权仓库能进入 Markdown 扫描流程。
5. 所有错误都有清晰文案和下一步建议。
