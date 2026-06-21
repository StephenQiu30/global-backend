## Architecture

语言领域采用简单的数据驱动设计，语言列表作为常量存储在领域层，校验函数作为纯函数实现。

### 语言数据结构

```python
# app/domain/languages.py
SUPPORTED_LANGUAGES: list[Language] = [
    Language(code="zh-CN", label="简体中文"),
    Language(code="zh-TW", label="繁体中文"),
    Language(code="en", label="English"),
    Language(code="ja", label="日本語"),
    Language(code="ko", label="한국어"),
    Language(code="fr", label="Français"),
    Language(code="de", label="Deutsch"),
    Language(code="es", label="Español"),
]
```

### 校验函数设计

```python
def validate_language_code(code: str) -> bool:
    """校验语言代码是否支持。"""
    return any(lang.code == code for lang in SUPPORTED_LANGUAGES)
```

### API 设计

- `GET /api/languages`：直接返回 `SUPPORTED_LANGUAGES` 列表
- 语言校验在任务创建端点前置执行，复用 `validate_language_code`

## Data Flow

1. 前端调用 `GET /api/languages` 获取语言列表
2. 用户选择目标语言
3. 前端调用 `POST /api/translation-tasks` 提交任务
4. 后端校验语言代码，拒绝不支持的语言
5. 校验通过后执行翻译任务

## Error Handling

- 不支持的语言代码返回 400 状态码
- 错误响应包含安全的错误码和消息
- 不泄露内部实现细节
