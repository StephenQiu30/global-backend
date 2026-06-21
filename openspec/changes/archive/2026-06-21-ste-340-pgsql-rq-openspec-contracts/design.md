## Context

当前 global-backend（GitHub Markdown Translator 后端）使用内存存储和同步执行模式：

- `app/api/`：直接在路由中处理请求，无分层
- `app/domain/`：Pydantic 领域模型，无持久化
- `app/services/`：业务逻辑直接调用，无队列
- 无数据库、无 ORM、无迁移、无异步队列

PRD 11 要求引入 PostgreSQL 持久化、SQLAlchemy ORM、Redis/RQ 异步队列和企业级分层架构。这些决策影响长期后端可维护性，必须在实现前通过 SDD 契约锁定。

## Goals / Non-Goals

**Goals:**
- 定义 PostgreSQL 为唯一关系型数据库
- 定义 SQLAlchemy 2.x + Alembic 为 ORM/迁移工具链
- 定义 Redis/RQ 为唯一队列方案
- 定义 controller/domain/dto/vo/models/repositories/db/queues/workers 分层结构
- 定义 DTO/VO 分离和 ORM Model 禁止直接返回的契约
- 定义 Swagger/OpenAPI 自动生成规范
- 定义模块依赖方向约束

**Non-Goals:**
- 不实现生产代码（纯 SDD 契约定义）
- 不安装依赖或运行数据库迁移
- 不定义具体数据库表结构（留给后续 ticket）
- 不实现自定义 MyBatis 类 ORM
- 不实现工作流引擎
- 不实现通用 Repository 框架（每个聚合根独立定义）
- 不实现多队列策略（单一 default 队列）

## Decisions

### 1. PostgreSQL 作为唯一数据库

**决策**: 使用 PostgreSQL 作为唯一关系型数据库。

**理由**: PostgreSQL 是 Python/FastAPI 生态中最成熟的开源关系型数据库，支持 JSONB、全文索引、异步驱动（asyncpg），与 SQLAlchemy 2.x 集成最佳。

**替代方案**: SQLite（不适合生产）、MySQL（生态略弱于 PgSQL）、MongoDB（不适合关系型翻译任务数据）。

### 2. SQLAlchemy 2.x + Alembic

**决策**: 使用 SQLAlchemy 2.x 作为 ORM，Alembic 管理 schema 迁移。

**理由**: SQLAlchemy 是 Python 生态最成熟的 ORM，2.x 版本支持 async/await，与 FastAPI 原生集成。Alembic 是 SQLAlchemy 官方迁移工具，支持自动生成和回滚。

**替代方案**: Tortoise ORM（生态较小）、Peewee（不支持 async）、raw SQL（维护成本高）。

### 3. Redis/RQ 作为队列方案

**决策**: 使用 Redis 作为消息代理，RQ（Redis Queue）作为任务队列框架。

**理由**: RQ 是轻量级 Python 队列，API 简洁，部署简单（只需 Redis），适合中小型项目。比 Celery 更轻量，比 Dramatiq 社区更大。

**替代方案**: Celery（过重）、Dramatiq（生态较小）、ARQ（async 但文档不足）。

### 4. Controller 分层替代直接路由

**决策**: 使用 `app/controller/` 替代 `app/api/` 的直接路由模式。

**理由**: Controller 分层将 HTTP 协议细节（路由、参数校验、响应序列化）与业务逻辑解耦。每个 controller 只负责接收 DTO、调用 Application Service、返回 VO，职责清晰。

**替代方案**: 保持 `app/api/` 模式（随项目增长会变得臃塞）、使用 CQRS（过度设计）。

### 5. DTO/VO 分离

**决策**: 入参使用 DTO，出参使用 VO，即使字段相同也独立定义。

**理由**: DTO 和 VO 的演进方向不同：入参变更（如新增校验规则）不应影响出参，出参变更（如新增返回字段）不应影响入参。独立定义避免耦合。

**替代方案**: 共享模型（耦合风险）、仅用 DTO（语义不清）。

### 6. ORM Model 禁止直接返回

**决策**: Controller 响应 SHALL NOT 直接返回 ORM Model 实例，必须转换为 VO。

**理由**: ORM Model 包含数据库特定字段（主键、外键、时间戳、关系加载），直接暴露会导致：API 契约不稳定、内部实现泄露、序列化意外（懒加载触发额外查询）。

### 7. 单一 default 队列

**决策**: 使用单一 `default` RQ 队列，不实现多队列策略。

**理由**: 当前项目规模（翻译任务为主）不需要优先级队列或多队列路由。单一队列简化运维和调试。后续如需扩展，可在 `app/queues/` 层增加路由逻辑。

### 8. Repository 每聚合根独立定义

**决策**: 每个聚合根（Aggregate Root）对应一个 Repository 类，不实现通用 Repository 框架。

**理由**: 通用 Repository 框架（如 `GenericRepository[T]`）增加抽象层但实际查询差异大，收益有限。每个聚合根独立定义 Repository，方法签名更明确，测试更简单。

## Risks / Trade-offs

- **迁移成本**: 当前 `app/api/` 模块需要在后续 ticket 中迁移至 `app/controller/`，涉及路由注册、依赖注入和测试更新
- **学习曲线**: SQLAlchemy 2.x 的 async session 管理和 Alembic 迁移对新贡献者有一定学习成本
- **RQ 局限**: RQ 不支持任务优先级、延迟任务和任务重试（需额外实现），后续可能需要替换为更强大的方案
- **DTO/VO 冗余**: 简单场景下 DTO 和 VO 字段完全相同，独立定义增加文件数量但降低耦合风险

## Migration Plan

本 change 是纯 SDD 契约定义，不涉及代码迁移。后续实现 ticket 的迁移顺序：

1. **Phase 1 — 基础设施**: `app/db/`（连接、session、Base）、`app/models/`（ORM Model）、Alembic 配置
2. **Phase 2 — 数据访问**: `app/repositories/`（Repository/DAO）
3. **Phase 3 — 业务编排**: 迁移 `app/services/` 至 Application Service 模式
4. **Phase 4 — 队列**: `app/queues/`（入队封装）、`app/workers/`（Worker 入口）
5. **Phase 5 — API 重构**: `app/controller/`（替代 `app/api/`）、`app/dto/`、`app/vo/`
6. **Phase 6 — 验证**: 确认 Swagger/OpenAPI 正常、ORM Model 不直接返回、所有测试通过
