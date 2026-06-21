## Goals

- 将入站请求 DTO 和出站响应 VO 从控制器中抽离，实现 Schema 边界显式化
- 控制器只负责路由和编排，不拥有 schema 定义
- ORM Model 永远不暴露为 API 输出

## Non-Goals

- 不为未涉及的端点创建 DTO/VO（如 languages、repositories）
- 不引入数据库 ORM 层（本 change 无 SQLAlchemy）
- 不修改领域模型或服务层

## Contracts

### DTO 契约
- DTO 只定义入站请求结构和校验规则
- DTO 命名约定：`{Action}{Entity}DTO`
- DTO 位于 `app/dto/` 包

### VO 契约
- VO 只定义出站响应结构
- VO 命名约定：`{Entity}VO` 或 `{Entity}{Detail}VO`
- VO 位于 `app/vo/` 包
- VO 可以引用其他 VO（如 `RepositoryListVO` 引用 `RepositoryItemVO`）

### 控制器契约
- 控制器从 `app/dto/` 导入请求模型
- 控制器从 `app/vo/` 导入响应模型
- 控制器负责将领域/服务模型转换为 VO

## State Flow

```
请求 → DTO 校验 → 控制器 → 服务/领域逻辑 → 领域/服务模型 → VO 转换 → 响应
```

## Failure Paths

- DTO 校验失败：FastAPI 自动返回 422
- 业务逻辑失败：控制器捕获异常，映射为安全的错误响应

## Rollback Impact

- 回滚只需恢复 `app/api/` 中的内联模型定义
- DTO/VO 模块可安全删除
- 不影响领域模型和服务层
