# PRD 03: Markdown 文件扫描与选择

## 1. 目标

系统自动扫描已授权仓库中的 Markdown 文件，默认选中根目录 `README.md`，并允许用户选择多个 Markdown 文件进行翻译。

## 2. 用户故事

作为用户，我希望系统能自动列出仓库里的 Markdown 文件，并默认帮我选中 README，这样我可以快速翻译项目入口文档，也可以按需补充其他文档。

## 3. 文件范围

第一版支持扩展名：

1. `.md`
2. `.markdown`

第一版排除：

1. 已生成的语言后缀文件，例如 `README.zh-CN.md`。
2. `node_modules`。
3. `.git`。
4. 构建输出目录，例如 `dist`、`build`、`.next`。
5. 超过大小限制的文件。

## 4. 扫描规则

1. 优先扫描默认分支。
2. 默认分支从 GitHub API 获取。
3. 扫描结果按路径排序。
4. 根目录 `README.md` 排在第一位。
5. 如果存在多个 README 变体，优先 `README.md`，其次 `README.markdown`。

## 5. 选择规则

第一版默认：

1. 自动选中根目录 `README.md`。
2. 用户可以取消选择。
3. 用户可以选择其他 Markdown 文件。
4. 单次最多选择 10 个文件。
5. 总原文大小限制建议为 200KB。

## 6. 前端展示

文件选择页展示：

1. 文件路径。
2. 文件大小。
3. 是否已存在目标语言文件。
4. 是否默认选中。
5. 禁用原因，例如文件过大。

操作能力：

1. 搜索文件路径。
2. 全选当前可选文件。
3. 清空选择。
4. 查看选择数量和总大小。

## 7. 后端接口需求

建议接口：

1. `POST /api/repositories/resolve`
2. `GET /api/repositories/{owner}/{repo}/markdown-files`

扫描接口返回：

1. `path`
2. `size_bytes`
3. `is_default_readme`
4. `is_translated_variant`
5. `disabled_reason`
6. `target_path_preview`

## 8. 错误场景

1. 仓库没有 Markdown 文件。
2. README 不存在。
3. GitHub contents/tree API 失败。
4. 文件太多导致扫描超时。
5. installation 权限不足。

## 9. 验收标准

1. 系统能列出仓库 `.md` 和 `.markdown` 文件。
2. 根目录 `README.md` 默认选中。
3. 已翻译语言后缀文件不会被默认选中。
4. 用户最多选择 10 个文件。
5. 前端能显示总大小和不可选原因。
