# Proposal: Markdown 保真翻译保护层

## Status

- [x] Proposed
- [ ] Accepted
- [ ] Implemented
- [ ] Verified
- [ ] Archived

## Summary

实现 Markdown 翻译时的结构保护机制，确保代码块、URL、图片、frontmatter、表格等不可翻译片段在翻译过程中不被破坏。

## Motivation

PRD 06 要求翻译 Markdown 文档时保持原始结构完整。翻译模型可能会意外修改代码、链接或格式，导致输出文件无法正常渲染。

## Scope

### In scope

- fenced code blocks 保护
- inline code 保护
- Markdown links URL 保护
- Markdown images URL 保护
- HTML 注释保护
- YAML frontmatter key 保护
- table separator 行保护
- badge URL 保护
- relative link 保护

### Out of scope

- 术语表
- 翻译记忆
- 多模型质量比较
- 人工校对流

### Non-goals

- 不承诺完美术语一致性
- 不让模型修改链接或代码

## Approach

采用"占位符替换 + 分块翻译 + 恢复"策略：

1. 解析 Markdown，将不可翻译片段替换为唯一占位符
2. 将可翻译文本分块发送给翻译 Provider
3. 翻译完成后恢复占位符
4. 做基本格式检查

Provider prompt 必须包含明确的 Markdown 保护约束。

## Risks

- 占位符可能与用户文本冲突（使用 UUID 前缀规避）
- 正则表达式可能无法覆盖所有 Markdown 语法变体
- 模型可能忽略 prompt 约束（通过后处理检查缓解）

## Normative files affected

- `docs/prd/github-translator/06-markdown-fidelity.md` (source)
- `docs/plans/github-translator/06-markdown-fidelity-plan.md` (source)
