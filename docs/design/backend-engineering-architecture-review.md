# Backend Engineering Architecture Review

> Companion document to the PRD 11 persistence plan
> (`docs/plans/github-translator/11-persistence-orm-rq-plan.md`).

## Goal

Provide a repository-local architecture guide so future backend changes follow
the same enterprise-style layered structure. This is not a platform manifesto;
it is an actionable reference for contributors working in `global-backend`.

## Target Module Layout

```text
app/
  controller/          # FastAPI controllers — the only HTTP interface layer
  application/         # Use-case orchestration services
  domain/              # Pure business logic, enums, value rules
  dto/                 # Inbound request / command schemas
  vo/                  # Outbound response / view schemas
  models/              # SQLAlchemy ORM models mapped to PgSQL tables
  repositories/        # Database access boundary (SQLAlchemy sessions)
  db/                  # Engine, session factory, DeclarativeBase
  services/            # Infrastructure-facing clients (GitHub, OpenAI, etc.)
  queues/              # Redis/RQ queue adapters
  workers/             # RQ job entrypoints
  core/                # Settings, errors, shared infrastructure
```

## Module Responsibilities

### `controller/`

FastAPI `APIRouter` definitions. Controllers are the **only** HTTP interface
source of truth — no endpoint definitions should exist outside this layer.

Each controller file:
- Declares route handlers with explicit `tags`, `response_model`, and
  `responses` metadata.
- Validates inbound data using DTOs from `app/dto/`.
- Returns outbound data as VOs from `app/vo/`.
- Delegates business logic to an application service.
- Contains no direct database queries, no ORM imports, and no inline Pydantic
  request/response models.

**Naming:** `{Resource}Controller` (e.g. `TranslationTaskController`,
`InstallationController`). Files: `{resource}_controller.py`.

### `application/`

Use-case orchestration services that coordinate domain logic, repositories,
infrastructure services, and queue adapters.

Each application service:
- Accepts DTOs or domain objects as input.
- Calls repositories for persistence, infrastructure services for external
  calls, and queue adapters for async work.
- Returns domain objects or VOs.
- Contains no HTTP or FastAPI imports.

**Naming:** `{Resource}Service` (e.g. `TranslationTaskService`). Files:
`{resource}_service.py`.

### `domain/`

Pure business logic: Pydantic models, enums, validation rules, and value
objects that are not tied to HTTP or database concerns.

Current contents include `TaskStatus`, `Task`, `TaskResult`, `RepositoryRef`,
`Language`, and markdown path rules.

**Rule:** Domain must not import from SQLAlchemy, FastAPI, `controller/`,
`dto/`, `vo/`, `models/`, or `repositories/`.

### `dto/`

Inbound request and command schemas used by controllers for input validation.

**Naming:** `{Action}{Resource}DTO` (e.g. `CreateTranslationTaskDTO`,
`VerifyInstallationDTO`). Files: `{resource}_dto.py`.

**Rule:** DTOs are Pydantic `BaseModel` subclasses. They must not import ORM
models or database session objects.

### `vo/`

Outbound response and view schemas returned by controllers.

**Naming:** `{Resource}VO` (e.g. `TranslationTaskVO`,
`TranslationFilePreviewVO`). Files: `{resource}_vo.py`.

**Rule:** VOs are Pydantic `BaseModel` subclasses. Controllers must never
return ORM model instances directly — always convert to a VO first.

### `models/`

SQLAlchemy 2.x ORM models mapped to PostgreSQL tables. Each model file
defines one `Mapped` class with column definitions, indexes, and table name.

**Naming:** `{Resource}Model` (e.g. `TranslationTaskModel`). Files:
`{resource}_model.py`.

**Rule:** Models must not import from `controller/`, `dto/`, `vo/`,
`application/`, or `services/`. Models may only import from `db/` for the
`DeclarativeBase`.

### `repositories/`

Database access boundary using SQLAlchemy async sessions. Each repository
wraps queries and mutations for one aggregate or table.

**Naming:** `{Resource}Repository` (e.g. `TranslationTaskRepository`). Files:
`{resource}_repository.py`.

**Rule:** Repositories may depend on `models/` and `db/`. They must not
depend on `controller/`, `dto/`, `vo/`, or `application/`. Methods are named
after product actions (e.g. `save_task`, `get_task_by_id`), not generic CRUD.

### `db/`

SQLAlchemy engine configuration, async session factory, and `DeclarativeBase`.

Current files:
- `base.py` — `DeclarativeBase` class.
- `session.py` — `init_engine()` and `get_session()` async generator.

### `services/`

Infrastructure-facing clients and providers that already exist in the codebase:
`GitHubAppClient`, `OpenAITranslationProvider`, `PublicRepositoryClient`,
`MarkdownFidelityService`, etc.

These are external system adapters. New business orchestration should go in
`application/`, not here.

### `queues/`

Redis/RQ queue adapters. Each adapter wraps `enqueue()` for one job type.

**Naming:** `{Resource}Queue` (e.g. `TranslationTaskQueue`). Files:
`{resource}_queue.py`.

### `workers/`

RQ job entrypoints. Each worker function receives a job ID, loads the record
via a repository, and delegates to an application service.

**Naming:** `{resource}_jobs.py` (e.g. `translation_jobs.py`).

### `core/`

Shared infrastructure: `Settings` (pydantic-settings), `AppError` exception
class, and other cross-cutting utilities.

## Dependency Rules

```text
controller ──→ dto, vo, application
application ──→ domain, repositories, queues, services
repositories ──→ models, db
models ──→ db (DeclarativeBase only)
domain ──→ (no framework imports)
workers ──→ application, queues
queues ──→ (Redis/RQ client only)
```

**Forbidden directions:**
- `models` must NOT depend on `controller`, `dto`, `vo`, `application`, or
  `services`.
- `domain` must NOT depend on SQLAlchemy, FastAPI, `models/`, `repositories/`,
  `controller/`, `dto/`, or `vo/`.
- `repositories` must NOT depend on `controller`, `dto`, `vo`, or
  `application`.
- `controller` must NOT import ORM models or database sessions.

## Where to Add New Features

| If you are adding...           | Put it in...         | Example file                          |
|--------------------------------|----------------------|---------------------------------------|
| A new API endpoint             | `controller/`        | `translation_task_controller.py`      |
| Business orchestration logic   | `application/`       | `translation_task_service.py`         |
| Business rules or enums        | `domain/`            | `task.py`, `languages.py`             |
| Inbound request validation     | `dto/`               | `translation_task_dto.py`             |
| Outbound response shape        | `vo/`                | `translation_task_vo.py`              |
| A new database table           | `models/`            | `translation_task_model.py`           |
| Database query logic           | `repositories/`      | `translation_task_repository.py`      |
| An external API client         | `services/`          | `github_app.py`                       |
| A background job queue adapter | `queues/`            | `translation_task_queue.py`           |
| A background job entrypoint    | `workers/`           | `translation_jobs.py`                 |
| App configuration              | `core/config.py`     | Add `Settings` field                  |

## Controllers Are the Only HTTP Interface

All HTTP endpoint definitions MUST live under `app/controller/`. After the
migration from `app/api/` is complete, no endpoint definitions should exist
outside this layer.

**Why:** A single source of truth for HTTP interfaces makes Swagger
documentation, API testing, and interface review predictable. Duplicate
endpoint definitions in `api/` and `controller/` create drift and confusion.

## Swagger / OpenAPI Requirements

Every new controller endpoint must satisfy these requirements:

1. **Tags:** Each router must declare `tags=[...]` grouping related endpoints
   (e.g. `installations`, `repositories`, `languages`, `translation-tasks`,
   `public-preview`).

2. **Response model:** Every endpoint must declare `response_model` for the
   success case using a VO from `app/vo/`.

3. **Error responses:** Endpoints must declare `responses` metadata for
   expected error codes (400, 403, 404, 422, 500) with description and schema.

4. **Operation ID:** Configure stable `operation_id` generation so generated
   API clients do not churn unexpectedly between releases.

5. **No ORM models in responses:** Controllers must never return SQLAlchemy
   model instances. Always convert to a VO.

6. **Documentation endpoints:** Swagger UI at `/docs` and OpenAPI JSON at
   `/openapi.json` must remain available.

## Naming Conventions Summary

| Layer          | Class suffix   | File suffix        | Example                              |
|----------------|----------------|--------------------|--------------------------------------|
| Controller     | `Controller`   | `_controller.py`   | `TranslationTaskController`          |
| Application    | `Service`      | `_service.py`      | `TranslationTaskService`             |
| Domain         | (none)         | `.py`              | `Task`, `TaskStatus`                 |
| DTO            | `DTO`          | `_dto.py`          | `CreateTranslationTaskDTO`           |
| VO             | `VO`           | `_vo.py`           | `TranslationTaskVO`                  |
| ORM Model      | `Model`        | `_model.py`        | `TranslationTaskModel`               |
| Repository     | `Repository`   | `_repository.py`   | `TranslationTaskRepository`          |
| Queue Adapter  | `Queue`        | `_queue.py`        | `TranslationTaskQueue`               |
| Worker         | (function)     | `_jobs.py`         | `translation_jobs.py`                |

## Explicit Non-Goals

These are intentionally not part of this architecture:

- **No frontend work.** This document covers backend structure only.
- **No full authentication system.** Auth decisions are deferred.
- **No generic repository base class.** Avoid premature abstraction; add only
  when real duplication appears.
- **No multi-queue prioritization.** One RQ queue until the first path works.
- **No dependency injection framework.** FastAPI `Depends()` is sufficient
  until evidence shows otherwise.
- **No event bus or workflow engine.** Keep orchestration in application
  services.
- **No broad platform manifesto.** This guide is specific to
  `global-backend`.
