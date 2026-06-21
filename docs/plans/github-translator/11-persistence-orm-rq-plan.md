# PRD 11 — 持久化、ORM、队列与分层架构

## 概述

本文档定义 global-backend（GitHub Markdown Translator 后端）的持久化、ORM、队列和企业级分层架构方案。本计划对应的 OpenSpec change 为 `openspec/changes/add-pgsql-rq-persistence/`。

## 目标

- 定义 PostgreSQL 为唯一关系型数据库
- 定义 SQLAlchemy 2.x + Alembic 为 ORM/迁移工具链
- 定义 Redis/RQ 为唯一队列方案
- 定义 controller/domain/dto/vo/models/repositories/db/queues/workers 分层结构
- 定义 DTO/VO 分离和 ORM Model 禁止直接返回的契约
- 定义 Swagger/OpenAPI 自动生成规范

## 非目标

- 不实现生产代码（纯 SDD 契约定义）
- 不安装依赖或运行数据库迁移
- 不定义具体数据库表结构
- 不实现自定义 MyBatis 类 ORM
- 不实现工作流引擎
- 不实现通用 Repository 框架
- 不实现多队列策略

## 技术选型

| 组件 | 选型 | 理由 |
|------|------|------|
| 数据库 | PostgreSQL | Python/FastAPI 生态最成熟，支持 JSONB、全文索引、asyncpg |
| ORM | SQLAlchemy 2.x | Python 最成熟 ORM，2.x 支持 async，与 FastAPI 原生集成 |
| 迁移 | Alembic | SQLAlchemy 官方迁移工具，支持自动生成和回滚 |
| 消息代理 | Redis | 轻量级，RQ 原生支持 |
| 队列框架 | RQ（Redis Queue） | API 简洁，部署简单，适合中小型项目 |

## 分层架构

```
app/
  controller/       # API 层（FastAPI Router）— 接收 DTO，返回 VO
  services/         # Application Service 层 — 业务编排
  domain/           # 领域模型 — 纯 Python，无框架依赖
  dto/              # Data Transfer Object — Pydantic，入参
  vo/               # Value Object — Pydantic，出参
  models/           # ORM Model — SQLAlchemy 声明式映射
  repositories/     # Repository/DAO 层 — 数据库查询封装
  db/               # 数据库连接、session、Base 定义
  queues/           # RQ 队列封装 — 入队操作
  workers/          # RQ Worker 入口 — 异步任务执行
  core/             # 配置、错误处理等基础设施
```

### 依赖方向

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

## 核心契约

### ORM Model 禁止直接返回

Controller 响应 SHALL NOT 直接返回 ORM Model 实例。必须通过 Application Service 或 mapper 转换为 VO 后返回。

**原因**: ORM Model 包含数据库特定字段（主键、外键、时间戳、关系加载），直接暴露会导致 API 契约不稳定和内部实现泄露。

### DTO/VO 分离

入参使用 DTO，出参使用 VO，即使字段相同也独立定义。

**原因**: 入参和出参的演进方向不同，独立定义避免耦合。

### Swagger/OpenAPI 自动生成

Swagger UI 通过 `/docs` 访问，OpenAPI JSON 通过 `/openapi.json` 访问。由 controller 定义和 Pydantic schema 自动生成。

## 实现分阶段路线

| Phase | 内容 | 对应 OpenSpec 任务 |
|-------|------|--------------------|
| 1 | `app/db/`（连接、session、Base）、Alembic 配置 | 任务 1 |
| 2 | `app/models/`（ORM Model） | 任务 2 |
| 3 | `app/repositories/`（Repository/DAO） | 任务 3 |
| 4 | `app/dto/`、`app/vo/`（DTO/VO 分离） | 任务 4 |
| 5 | `app/controller/`（替代 `app/api/`） | 任务 5 |
| 6 | `app/services/`（Application Service 重构） | 任务 6 |
| 7 | `app/queues/`、`app/workers/`（队列/Worker） | 任务 7 |
| 8 | Swagger/OpenAPI 验证 | 任务 8 |

## 风险与缓解

| 风险 | 影响 | 缓解 |
|------|------|------|
| `app/api/` → `app/controller/` 迁移成本 | 中 | 分阶段迁移，保持向后兼容 |
| SQLAlchemy 2.x async session 学习曲线 | 低 | 文档充足，社区活跃 |
| RQ 不支持优先级/延迟/重试 | 低 | 首版可接受，后续在 `app/queues/` 层扩展 |
| DTO/VO 字段冗余 | 低 | 降低耦合收益大于冗余成本 |

## 验证

- `bash scripts/validate-repository.sh` 确认仓库结构
- OpenSpec artifacts 与本计划文档一致性检查
- Agent Review 确认无生产代码捆绑
