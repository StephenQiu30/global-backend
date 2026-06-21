## Why

当前 global-backend 使用内存存储和同步执行模式，无法支持任务持久化、异步队列处理和企业级分层架构。PRD 11 要求引入 PostgreSQL 持久化、SQLAlchemy ORM、Redis/RQ 异步队列，以及 controller-based API 分层架构（DTO/VO/ORM Model/Repository/Application Service/Queue/Worker）。这些架构决策影响长期后端可维护性，必须在实现前通过 SDD 契约锁定。

## What Changes

- 定义 PostgreSQL 为唯一关系型数据库，SQLAlchemy 2.x + Alembic 为 ORM/迁移工具链
- 定义 Redis/RQ 为唯一队列方案，RQ Worker 为任务执行器
- 定义 `app/controller/` 为 API 层，替代当前 `app/api/` 直接路由模式
- 定义 DTO（Data Transfer Object）用于 controller 入参，VO（Value Object）用于 controller 出参
- 定义 ORM Model 为 SQLAlchemy 模型层，映射数据库表结构
- 定义 Repository/DAO 层封装数据库查询，Application Service 编排业务逻辑
- 定义 Queue 层封装 RQ 任务入队，Worker 层执行异步任务
- 定义 Swagger/OpenAPI 由 controller 定义自动生成，暴露于 `/docs` 和 `/openapi.json`
- 定义 ORM Model 禁止直接作为 controller 响应返回

## Capabilities

### New Capabilities

- `persistence-pgsql`: PostgreSQL 数据库作为唯一关系型存储
- `orm-sqlalchemy`: SQLAlchemy 2.x ORM + Alembic 迁移工具链
- `queue-rq`: Redis/RQ 异步队列方案
- `controller-api`: 基于 controller 的 API 分层架构
- `dto-vo-separation`: DTO 入参 / VO 出参分离
- `repository-dao`: Repository/DAO 数据访问层
- `application-service`: Application Service 业务编排层
- `queue-worker`: Queue 入队 + Worker 异步执行

### Modified Capabilities

- 无（全新架构契约定义，不修改已有 spec）

## Impact

- 不产生生产代码变更（纯 SDD 契约定义）
- 后续实现 ticket 将基于本 change 的契约创建实际模块
- 架构决策影响所有后续持久化、队列和 API 相关 ticket
- 当前 `app/api/` 模块将在后续 ticket 中迁移至 `app/controller/` 模式
