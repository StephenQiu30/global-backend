## Persistence Layer

### Requirement 1: PostgreSQL 数据库

系统 SHALL 使用 PostgreSQL 作为唯一关系型数据库。

- 连接配置 SHALL 通过环境变量 `DATABASE_URL` 提供
- 连接格式 SHALL 为 SQLAlchemy 兼容的 PostgreSQL URL：`postgresql+asyncpg://user:pass@host:port/dbname`
- 系统 SHALL NOT 使用 SQLite、MySQL 或其他关系型数据库

### Requirement 2: SQLAlchemy 2.x ORM

系统 SHALL 使用 SQLAlchemy 2.x 作为 ORM 框架。

- ORM Model SHALL 使用 SQLAlchemy 2.x 声明式映射（Declarative Mapping）
- ORM Model SHALL 继承自项目统一的 `Base` 基类（定义于 `app/db/base.py`）
- ORM Model SHALL 定义表名、列、关系和约束
- ORM Model SHALL NOT 包含业务逻辑；业务逻辑属于 Application Service
- ORM Model 文件 SHALL 放置在 `app/models/` 目录

### Requirement 3: Alembic 迁移

系统 SHALL 使用 Alembic 管理数据库 schema 迁移。

- 迁移脚本 SHALL 放置在 `alembic/versions/`
- Alembic 配置 SHALL 读取 `DATABASE_URL` 环境变量
- 每个 schema 变更 SHALL 生成独立的迁移脚本
- 迁移脚本 SHALL 包含 `upgrade()` 和 `downgrade()` 方法

## Repository / DAO Layer

### Requirement 4: Repository/DAO 数据访问层

系统 SHALL 提供 Repository/DAO 层封装数据库查询。

- Repository SHALL 放置在 `app/repositories/` 目录
- 每个聚合根（Aggregate Root）SHALL 对应一个 Repository 类
- Repository SHALL 接收 `AsyncSession` 作为依赖注入
- Repository SHALL 返回 ORM Model 实例或查询结果
- Repository SHALL NOT 包含 HTTP 相关逻辑

### Requirement 5: Repository 方法签名

Repository 方法 SHALL 遵循以下命名约定：

- `get_by_id(id)` — 按主键查询单条记录
- `list(filters, offset, limit)` — 带分页的列表查询
- `create(entity)` — 创建新记录
- `update(entity, data)` — 更新已有记录
- `delete(id)` — 删除记录（软删除优先）

## Queue Layer

### Requirement 6: Redis/RQ 队列

系统 SHALL 使用 Redis 作为消息代理，RQ（Redis Queue）作为任务队列框架。

- Redis 连接 SHALL 通过环境变量 `REDIS_URL` 提供
- RQ Queue SHALL 使用默认队列名 `default`
- 系统 SHALL NOT 使用 Celery、Dramatiq 或其他队列框架
- 系统 SHALL NOT 实现多队列策略；单一 `default` 队列满足所有场景

### Requirement 7: Queue 入队层

系统 SHALL 提供 Queue 封装层，将任务入队到 RQ。

- Queue 封装 SHALL 放置在 `app/queues/` 目录
- Queue 封装 SHALL 提供类型安全的入队方法
- Queue 封装 SHALL 将任务函数名和参数序列化到 RQ Job
- Queue 封装 SHALL 返回 RQ Job ID 用于状态追踪

### Requirement 8: Worker 执行层

系统 SHALL 提供 RQ Worker 执行异步任务。

- Worker 入口 SHALL 放置在 `app/workers/` 目录
- Worker SHALL 从 RQ 队列消费任务并执行
- Worker SHALL 处理任务成功、失败和超时场景
- Worker 失败时 SHALL 记录错误日志但不泄露敏感信息

## Controller / API Layer

### Requirement 9: Controller 分层架构

系统 SHALL 使用 `app/controller/` 作为 API 层，替代当前 `app/api/` 直接路由模式。

- 每个业务域 SHALL 对应一个 controller 模块
- Controller SHALL 定义 FastAPI Router 和端点
- Controller SHALL 接收 DTO 作为请求入参
- Controller SHALL 返回 VO 作为响应出参
- Controller SHALL NOT 直接操作数据库；通过 Application Service 编排
- Controller SHALL NOT 返回 ORM Model 实例

### Requirement 10: DTO（Data Transfer Object）

系统 SHALL 定义 DTO 用于 controller 入参。

- DTO SHALL 放置在 `app/dto/` 目录
- DTO SHALL 使用 Pydantic BaseModel 定义
- DTO SHALL 只包含 API 请求所需字段
- DTO SHALL 包含字段校验规则（`Field` 约束）
- DTO SHALL NOT 包含数据库主键或时间戳等持久化字段

### Requirement 11: VO（Value Object）

系统 SHALL 定义 VO 用于 controller 出参。

- VO SHALL 放置在 `app/vo/` 目录
- VO SHALL 使用 Pydantic BaseModel 定义
- VO SHALL 只包含 API 响应所需字段
- VO SHALL NOT 包含内部实现细节（如 ORM 关系字段）
- VO SHALL 与 DTO 分离，即使字段相同也独立定义

### Requirement 12: ORM Model 禁止直接返回

Controller 响应 SHALL NOT 直接返回 ORM Model 实例。

- Controller SHALL 将 ORM Model 转换为 VO 后返回
- 转换逻辑 SHALL 在 Application Service 或专门的 mapper 中完成
- 违反此规则的代码 SHALL NOT 通过 Agent Review

## Application Service Layer

### Requirement 13: Application Service 业务编排

系统 SHALL 提供 Application Service 层编排业务逻辑。

- Application Service SHALL 放置在 `app/services/` 目录（复用现有目录）
- Application Service SHALL 协调 Repository、Queue 和外部服务调用
- Application Service SHALL 包含业务规则校验和事务边界
- Application Service SHALL NOT 包含 HTTP 相关逻辑

## Swagger / OpenAPI

### Requirement 14: Swagger/OpenAPI 自动生成

Swagger/OpenAPI SHALL 由 controller 定义自动生成。

- Swagger UI SHALL 可通过 `/docs` 访问
- OpenAPI JSON SHALL 可通过 `/openapi.json` 访问
- 每个 controller 端点 SHALL 包含 `summary`、`description`、`response_model`
- 请求和响应模型 SHALL 使用 Pydantic schema 自动生成 OpenAPI schema

## Module Boundaries

### Requirement 15: 目录结构

系统 SHALL 遵循以下目录结构：

```
app/
  controller/       # API 层（FastAPI Router）
  services/         # Application Service 层
  domain/           # 领域模型（纯 Python，无框架依赖）
  dto/              # Data Transfer Object（Pydantic，入参）
  vo/               # Value Object（Pydantic，出参）
  models/           # ORM Model（SQLAlchemy）
  repositories/     # Repository/DAO 层
  db/               # 数据库连接、session、Base 定义
  queues/           # RQ 队列封装
  workers/          # RQ Worker 入口
  core/             # 配置、错误处理等基础设施
```

### Requirement 16: 依赖方向

模块之间的依赖方向 SHALL 遵循：

```
controller → service → repository → model
                ↓           ↓
              queue     db/session
                ↓
             worker → service
```

- Controller SHALL NOT 依赖 Repository 或 Model
- Service SHALL NOT 依赖 Controller
- Repository SHALL NOT 依赖 Service 或 Controller
- Worker SHALL 只依赖 Service，不依赖 Controller
