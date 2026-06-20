"""Pure function to build PR body for translation Pull Requests."""


def build_translation_pr_body(
    language: str,
    mappings: list[dict[str, str]],
    provider_name: str,
    task_id: str,
) -> str:
    """Build a Markdown PR body for a translation PR.

    Args:
        language: Target language code (e.g., "zh-CN").
        mappings: List of {"source": ..., "target": ...} file mappings.
        provider_name: Name of the translation provider.
        task_id: Translation task identifier.

    Returns:
        Valid Markdown string for the PR body.
    """
    lines = [
        f"# 自动翻译: {language}",
        "",
        "此 PR 由自动翻译工具生成，需要人工审核。",
        "",
        "## 翻译信息",
        "",
        f"- **目标语言**: {language}",
        f"- **翻译引擎**: {provider_name}",
        f"- **任务 ID**: {task_id}",
        "",
        "## 文件映射",
        "",
    ]

    if mappings:
        lines.append("| 源文件 | 目标文件 |")
        lines.append("|--------|----------|")
        for m in mappings:
            lines.append(f"| {m['source']} | {m['target']} |")
        lines.append("")

    lines.extend([
        "## 审核建议",
        "",
        "请人工审核翻译质量，特别是：",
        "- 术语准确性",
        "- 格式完整性",
        "- 链接和代码块是否正确保留",
        "",
        "---",
        "*此翻译由自动翻译工具生成，请在合并前仔细审核。*",
    ])

    return "\n".join(lines)
