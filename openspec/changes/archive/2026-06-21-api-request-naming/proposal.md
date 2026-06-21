## Why

入站 API 模型当前使用 `XxxDTO` 命名且部分 GET 端点参数分散在 path/query 中，不利于 OpenAPI 文档生成与统一契约表达。

## What Changes

- `app/dto/` 迁移为 `app/requests/`，类名统一为 `XxxRequest`
- 补齐 GET 端点 path/query 参数 Request 封装
- 控制器改为从 `app/requests/` 导入请求模型
- 响应 `app/vo/` 保持不变
- 测试目录 `tests/dto/` 迁移为 `tests/requests/`

## Capabilities

### Modified Capabilities

- `dto-vo-schema-boundary`: 请求层从 DTO 改为 Request 命名与目录约定

## Impact

- HTTP JSON 字段名不变，对外 API 契约兼容
- OpenAPI schema 名称变为 `XxxRequest`，便于文档与代码生成
