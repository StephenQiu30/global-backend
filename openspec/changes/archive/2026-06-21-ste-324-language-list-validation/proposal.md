## Why

PRD 04 定义首版语言列表和文件后缀规则。后端需要提供受控语言列表，并在翻译任务提交前校验目标语言代码，拒绝不支持的语言。

## What Changes

- 新增 `app/domain/languages.py`：语言领域模型和校验函数
- 新增 `app/api/languages.py`：`GET /api/languages` API 端点
- 修改 `app/api/tasks.py`：在翻译任务创建时集成语言校验
- 新增 `tests/domain/test_languages.py`：语言领域测试
- 新增 `tests/api/test_languages_api.py`：语言 API 测试

## Capabilities

### New Capabilities
- `language-domain`: 语言领域模型，定义支持的语言列表和校验函数
- `languages-api`: `GET /api/languages` 端点，返回支持的语言列表

### Modified Capabilities
- `translation-task-api`: 在任务创建时集成语言校验，拒绝不支持的语言代码

## Impact

- 新增 API 端点：`GET /api/languages`
- 翻译任务创建时新增语言校验前置条件
- 语言列表变更需要显式更新 PRD/Plan
- 支持的语言：`zh-CN`、`zh-TW`、`en`、`ja`、`ko`、`fr`、`de`、`es`
