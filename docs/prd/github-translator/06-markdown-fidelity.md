# PRD 06: Markdown 保真翻译

## 1. 目标

翻译 Markdown 文档时尽量保持原始结构、代码、链接、图片、表格和 frontmatter 不被破坏，只翻译自然语言内容。

## 2. 用户故事

作为仓库维护者，我希望翻译后的 Markdown 文件仍然可以正常渲染，代码块、链接和图片地址保持正确，这样我不需要大量手工修复格式。

## 3. 必须保护的内容

1. fenced code blocks。
2. inline code。
3. Markdown links 的 URL。
4. Markdown images 的 URL。
5. HTML 注释。
6. YAML frontmatter 的 key。
7. 表格结构。
8. Badge URL。
9. 相对路径链接。

## 4. 可翻译内容

1. 标题文本。
2. 普通段落。
3. 列表项自然语言。
4. 表格单元格自然语言。
5. link label 文本。
6. image alt 文本。
7. blockquote 自然语言。

## 5. 处理策略

第一版采用“保护占位符 + 分块翻译”：

1. 解析 Markdown。
2. 将不可翻译片段替换为占位符。
3. 将可翻译文本分块。
4. 调用翻译 Provider。
5. 恢复占位符。
6. 重新拼装 Markdown。
7. 做基本格式检查。

## 6. Provider Prompt 要求

翻译 Prompt 必须要求模型：

1. 保留 Markdown 结构。
2. 不翻译代码。
3. 不修改 URL。
4. 不添加额外解释。
5. 不删除占位符。
6. 不改变标题层级。
7. 保持列表和表格格式。

## 7. 文件命名

同目录语言后缀：

1. `README.md` -> `README.zh-CN.md`
2. `docs/guide.md` -> `docs/guide.zh-CN.md`
3. `docs/api.markdown` -> `docs/api.zh-CN.markdown`

## 8. 质量限制

第一版不承诺完美术语一致性，但必须避免结构损坏。

不做：

1. 术语表。
2. 翻译记忆。
3. 人工校对工作流。
4. 多模型质量比较。

## 9. 验收标准

1. 代码块内容不被翻译。
2. URL 不被修改。
3. 图片引用不被破坏。
4. Markdown 标题层级保持一致。
5. 输出文件可被 Markdown 渲染器正常解析。
