## Why

`app/requests/` 与项目分层语义不一致：入参应放在 `app/dto/`，类名保留 `XxxRequest` 表达接口请求契约。

## What Changes

- `app/requests/` 迁回 `app/dto/`，模块文件按领域重命名
- 更新 controller / test import 路径
- OpenSpec 基线 spec 同步为 `app/dto/` + `XxxRequest`

## Impact

- 无 HTTP 契约变更，仅 Python 包路径调整
