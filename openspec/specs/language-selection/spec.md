## Language Domain (`app/domain/languages.py`)

### Requirement 1: 支持的语言列表

系统 SHALL 定义 `SUPPORTED_LANGUAGES` 常量，包含以下语言：
- `zh-CN` (简体中文)
- `zh-TW` (繁体中文)
- `en` (English)
- `ja` (日本語)
- `ko` (한국어)
- `fr` (Français)
- `de` (Deutsch)
- `es` (Español)

### Requirement 2: Language 模型

系统 SHALL 定义 `Language` 模型：
- `code: str` — 语言代码（如 "zh-CN"）
- `label: str` — 语言显示名称（如 "简体中文"）

### Requirement 3: 语言校验函数

系统 SHALL 提供 `validate_language_code(code: str) -> bool` 函数：
- 接受支持的语言代码时返回 `True`
- 接受未知语言代码时返回 `False`

### Requirement 4: 语言校验异常

系统 SHALL 提供 `InvalidLanguageError` 异常类：
- 当语言代码不支持时抛出
- 包含安全的错误信息

## Languages API (`app/api/languages.py`)

### Requirement 5: GET /api/languages

系统 SHALL 提供 `GET /api/languages` 端点：
- 返回支持的语言列表
- 响应格式：`[{"code": "zh-CN", "label": "简体中文"}, ...]`
- 状态码：200

## Translation Task Integration (`app/api/tasks.py`)

### Requirement 6: 任务创建语言校验

`POST /api/translation-tasks` SHALL 在创建任务前校验语言代码：
- 调用 `validate_language_code` 校验 `language` 字段
- 语言代码不支持时返回 400 状态码
- 错误响应格式：`{"error": "unsupported_language", "message": "..."}`
